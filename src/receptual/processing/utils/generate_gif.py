"""
Utility script to generate a GIF animation of a receptive field.
This script can be used to create animations for documentation or visualization purposes
without opening the GUI.
"""

import argparse
import numpy as np
import sys
import imageio
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import os
import gc
from PIL import Image

# Import the necessary components from receptual
from receptual.gui.widgets.plot_widget import Plot3DWidget
from receptual.processing.managers.plot_manager import PlotManager


class DummyManager:
	"""A minimal manager class that can be used to initialize a PlotManager."""

	def __init__(self, data, name='Receptive Field'):
		self.data = data
		self.name = name


def capture_plot_rotation_gif(
	plot_widget,
	filename='receptive_field.gif',
	frames=120,
	duration=0.033,
	scale_factor=2.0,
	rotation_degrees=90,
):
	"""
	Capture a high-quality rotation of the current plot and save as a GIF.
	Memory-efficient version that streams frames to disk in chunks to avoid memory issues.

	Args:
		plot_widget: The Plot3DWidget instance to capture
		filename: Output GIF filename
		frames: Number of frames to capture (more frames = smoother animation)
		duration: Duration between frames in seconds
		scale_factor: Multiplier for output resolution (higher = better quality)
		rotation_degrees: Total rotation in degrees (360=full turn, 90=quarter turn)
	"""
	# Ensure the output directory exists
	os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

	# Store current rotation state and stop if active
	was_rotating = plot_widget.is_rotating
	if was_rotating:
		plot_widget.toggle_rotation(False)

	# Store original camera position
	original_azimuth = plot_widget.plot_view.opts['azimuth']

	# Calculate target size with higher resolution
	original_size = plot_widget.plot_view.size()
	target_width = int(original_size.width() * scale_factor)
	target_height = int(original_size.height() * scale_factor)

	# Create a directory for frames in the current working directory
	# Use a unique folder name based on the output filename to avoid conflicts
	frames_dir_name = (
		f'receptual_frames_{os.path.basename(filename).replace(".gif", "")}'
	)
	frames_dir = os.path.join(os.getcwd(), frames_dir_name)

	# Create the directory if it doesn't exist
	if os.path.exists(frames_dir):
		# If it already exists, clear it
		for file in os.listdir(frames_dir):
			try:
				os.remove(os.path.join(frames_dir, file))
			except Exception as e:
				print(f'Warning: Could not remove old file {file}: {e}')
	else:
		os.makedirs(frames_dir)

	# Calculate the azimuth step
	azimuth_step = rotation_degrees / frames

	print(f'Capturing {frames} frames at {target_width}x{target_height} resolution...')
	print(f'Rotation: {rotation_degrees} degrees')
	print(f'Storing frames in: {frames_dir}')
	print(f'Output file will be saved to: {os.path.abspath(filename)}')

	app = QApplication.instance()  # Get the current application instance

	try:
		# First, capture the first frame to determine the exact dimensions we should use
		# Set the initial azimuth
		plot_widget.plot_view.setCameraPosition(azimuth=original_azimuth)

		# Force the widget to update and render
		plot_widget.plot_view.update()
		plot_widget.update()
		app.processEvents()

		# Grab the first frame to determine the standard size
		first_pixmap = plot_widget.plot_view.grab()
		if scale_factor != 1.0:
			first_pixmap = first_pixmap.scaled(
				target_width,
				target_height,
				Qt.AspectRatioMode.KeepAspectRatio,
				Qt.TransformationMode.SmoothTransformation,
			)

		# Get the exact dimensions after scaling (may not match target exactly due to aspect ratio)
		standard_width = first_pixmap.width()
		standard_height = first_pixmap.height()

		print(f'Using standard frame size: {standard_width}x{standard_height}')

		# Save the first frame
		frame_paths = []
		frame_path = os.path.join(frames_dir, 'frame_0000.png')
		first_pixmap.save(frame_path, 'PNG', quality=100)
		frame_paths.append(frame_path)

		# Get the reference size from the first image for validation
		with Image.open(frame_path) as img:
			reference_size = img.size

		# Force garbage collection
		first_pixmap = None
		gc.collect()

		# Determine a reasonable chunk size (adjust as needed)
		# This limits how many frames we process at once to avoid memory issues
		chunk_size = min(50, frames)

		# Now capture the rest of the frames in chunks
		for chunk_start in range(1, frames, chunk_size):
			chunk_end = min(chunk_start + chunk_size, frames)
			print(f'Capturing frames {chunk_start} to {chunk_end - 1} (of {frames})...')

			# Process frames in this chunk
			for i in range(chunk_start, chunk_end):
				# Set the new azimuth for this frame
				new_azimuth = (original_azimuth + i * azimuth_step) % 360
				plot_widget.plot_view.setCameraPosition(azimuth=new_azimuth)

				# Force the widget to update and render
				plot_widget.plot_view.update()
				plot_widget.update()
				app.processEvents()

				# Create a higher-resolution pixmap directly
				pixmap = plot_widget.plot_view.grab()

				# Scale to match EXACTLY the size of the first frame
				pixmap = pixmap.scaled(
					standard_width,
					standard_height,
					Qt.AspectRatioMode.IgnoreAspectRatio,  # Force exact dimensions
					Qt.TransformationMode.SmoothTransformation,
				)

				# Save frame to file
				frame_path = os.path.join(frames_dir, f'frame_{i:04d}.png')
				pixmap.save(frame_path, 'PNG', quality=100)
				frame_paths.append(frame_path)

				# Force garbage collection
				pixmap = None
				app.processEvents()
				gc.collect()

		print(f'All {len(frame_paths)} frames captured.')

		# Now create the GIF using a chunked approach
		# We'll use apng2gif as an intermediate format to avoid loading all frames at once
		try:
			# First create an intermediate animated PNG which is more memory efficient
			print('Creating intermediate file to avoid memory issues...')

			# Use PIL to validate frames and build frame list
			valid_frames = []

			for path in frame_paths:
				if os.path.exists(path):
					try:
						# Just verify the file is valid, don't keep it in memory
						with Image.open(path) as img:
							if img.size == reference_size:
								valid_frames.append(path)
							else:
								print(
									f'Warning: Skipping frame with incorrect size: {path}'
								)
					except Exception as e:
						print(f'Warning: Cannot read frame {path}: {e}')

			if not valid_frames:
				raise ValueError('No valid frames were captured')

			print(f'Found {len(valid_frames)} valid frames')

			# Create GIF using imageio's get_writer for streaming
			print('Creating GIF with streaming writer...')

			with imageio.get_writer(
				filename, mode='I', duration=duration, loop=0
			) as writer:
				# Process frames in chunks to limit memory usage
				for i, frame_path in enumerate(valid_frames):
					if i % 20 == 0:
						print(f'  Processing frame {i}/{len(valid_frames)}...')

					# Load one frame at a time
					img = imageio.imread(frame_path)
					writer.append_data(img)

					# Explicitly delete and garbage collect
					img = None
					gc.collect()

		except Exception as e:
			print(f'Error creating GIF using streaming method: {e}')
			print('Falling back to PIL method with reduced frames...')

			# Fallback to PIL but with reduced number of frames if we have too many
			try:
				max_frames_pil = min(
					len(valid_frames), 100
				)  # Limit to 100 frames for PIL
				if len(valid_frames) > max_frames_pil:
					print(
						f'Reducing from {len(valid_frames)} to {max_frames_pil} frames to avoid memory issues'
					)
					# Pick frames evenly distributed across the animation
					step = len(valid_frames) // max_frames_pil
					selected_frames = valid_frames[::step][:max_frames_pil]
				else:
					selected_frames = valid_frames

				# Load images in small batches
				batch_size = 10

				with Image.open(selected_frames[0]) as first_img:
					# Make a copy to avoid "I/O operation on closed file" error
					first_frame = first_img.copy()

					# Save with batched appending
					print(
						f'Saving GIF with {len(selected_frames)} frames in batches of {batch_size}...'
					)

					# Start with first frame
					first_frame.save(
						filename,
						save_all=True,
						append_images=[],  # We'll append in batches
						optimize=False,  # Optimization can use more memory
						duration=int(duration * 1000),  # PIL uses milliseconds
						loop=0,
					)

					# Now append remaining frames in batches
					for batch_start in range(1, len(selected_frames), batch_size):
						batch_end = min(batch_start + batch_size, len(selected_frames))
						print(f'  Processing batch {batch_start}-{batch_end - 1}...')

						# Open this batch of images
						batch_frames = []
						for path in selected_frames[batch_start:batch_end]:
							with Image.open(path) as img:
								# Make copy to avoid closed file issues
								batch_frames.append(img.copy())

						# Append this batch to the GIF
						first_frame.save(
							filename,
							save_all=True,
							append_images=batch_frames,
							optimize=False,
							duration=int(duration * 1000),
							loop=0,
						)

						# Clear batch from memory
						batch_frames = None
						gc.collect()

				print('Fallback PIL method completed.')
			except Exception as e:
				print(f'Error in fallback PIL method: {e}')
				raise

		# Verify the GIF was created
		if not os.path.exists(filename):
			raise FileNotFoundError(f'GIF file {filename} was not created')

		gif_size = os.path.getsize(filename) / (1024 * 1024)  # Size in MB
		print(f'GIF saved to {filename} ({gif_size:.2f} MB)')

	except Exception as e:
		print(f'Error creating GIF: {e}')
		import traceback

		traceback.print_exc()
		return False
	finally:
		# Restore original state
		plot_widget.plot_view.setCameraPosition(azimuth=original_azimuth)
		if was_rotating:
			plot_widget.toggle_rotation(True)

		# Clean up frame files
		try:
			print(f'Cleaning up frame files from: {frames_dir}')
			# First try to remove individual files
			for file in os.listdir(frames_dir):
				try:
					os.remove(os.path.join(frames_dir, file))
				except Exception as e:
					print(f'Warning: Could not remove file {file}: {e}')

			# Then try to remove the directory
			os.rmdir(frames_dir)
			print('Cleanup completed successfully')
		except Exception as e:
			print(f'Warning: Could not fully clean up frame files: {e}')
			print(f'You may want to manually delete the directory: {frames_dir}')

	# Final verification
	if os.path.exists(filename):
		print(f'✅ GIF creation successful: {filename}')
		return True
	else:
		print(f'❌ GIF creation failed: {filename} does not exist')
		return False


def generate_gif(
	input_file,
	output_file,
	frames=120,
	duration=0.033,
	scale=2.0,
	rotation=90,
	size=(800, 600),
):
	"""
	Generate a GIF animation of a receptive field using the Plot3DWidget.

	Args:
		input_file: Path to the receptive field data file (NPY format)
		output_file: Output GIF file path
		frames: Number of frames in the animation
		duration: Duration between frames in seconds
		scale: Scale factor for resolution
		rotation: Rotation angle in degrees
		size: Size of the output GIF as (width, height)
	"""
	# Make sure the output path is absolute
	output_file = os.path.abspath(output_file)

	# Create output directory if it doesn't exist
	os.makedirs(os.path.dirname(output_file), exist_ok=True)

	print(f'Output will be saved to: {output_file}')

	# Initialize Qt application
	app = QApplication.instance() or QApplication(sys.argv)

	# Load data
	try:
		data = np.load(input_file)
		print(f'Loaded data with shape: {data.shape}')
	except Exception as e:
		print(f'Error loading data: {e}')
		return

	# Create dummy manager with the loaded data
	dummy_manager = DummyManager(data)

	# Create a plot manager with the data
	plot_manager = PlotManager(dummy_manager)

	# Create the plot widget
	plot_widget = Plot3DWidget()
	plot_widget.resize(*size)

	# Set the plot manager to initialize the plot
	plot_widget.set_plot_manager(plot_manager)

	# Force an update and show
	plot_widget.update_plot()
	plot_widget.show()

	# Process events to ensure rendering happens
	app.processEvents()

	# Adjust frames recommendation based on memory considerations
	if frames > 300:
		max_recommended = 300
		print(
			f'⚠️ High frame count detected! Using {frames} frames may cause memory issues.'
		)
		print(
			f'   The recommended maximum is {max_recommended} frames for better stability.'
		)
		print(
			'   Consider reducing the number of frames or using a lower resolution scale.'
		)
		print('   (the script will still try with your requested settings)')

	# Capture the GIF using our function
	success = capture_plot_rotation_gif(
		plot_widget=plot_widget,
		filename=output_file,
		frames=frames,
		duration=duration,
		scale_factor=scale,
		rotation_degrees=rotation,
	)

	# Clean up
	plot_widget.close()

	if success:
		print(f'GIF successfully generated: {output_file}')
	else:
		print(f'Failed to generate GIF: {output_file}')


def main():
	"""Main entry point for the command line tool."""
	parser = argparse.ArgumentParser(
		description='Generate a GIF animation of a receptive field'
	)
	parser.add_argument(
		'--input-file',
		type=str,
		default='sample_data/encoding/centre_surround/receptive_field.npy',
		help='Path to the receptive field file (NPY format)',
	)
	parser.add_argument(
		'--output-file',
		type=str,
		default='assets/receptive_field.gif',
		help='Output GIF file path',
	)
	parser.add_argument(
		'--frames', type=int, default=300, help='Number of frames in the animation'
	)
	parser.add_argument(
		'--duration',
		type=float,
		default=0.003,
		help='Duration between frames in seconds',
	)
	parser.add_argument(
		'--scale', type=float, default=4.0, help='Scale factor for resolution'
	)
	parser.add_argument(
		'--rotation', type=float, default=360.0, help='Rotation angle in degrees'
	)
	parser.add_argument(
		'--size', type=str, default='800x600', help='Output size in format WIDTHxHEIGHT'
	)

	args = parser.parse_args()

	# Parse size
	try:
		width, height = map(int, args.size.lower().split('x'))
		size = (width, height)
	except ValueError:
		print(f'Invalid size format: {args.size}. Using default 800x600.')
		size = (800, 600)

	# Add a memory warning for high-risk combinations
	memory_warning = False
	if args.frames > 500 and args.scale > 1.5:
		memory_warning = True
	elif args.frames > 1000:
		memory_warning = True

	if memory_warning:
		print('\n⚠️ WARNING: The selected parameters might require significant memory!')
		print(f'   - {args.frames} frames at {args.scale}x resolution')
		print('   - Consider reducing frame count or scale for better performance')
		print('   - Continue anyway? (y/n): ', end='')
		response = input().strip().lower()
		if response != 'y':
			print('Operation cancelled.')
			return

	# Generate the GIF
	generate_gif(
		input_file=args.input_file,
		output_file=args.output_file,
		frames=args.frames,
		duration=args.duration,
		scale=args.scale,
		rotation=args.rotation,
		size=size,
	)


if __name__ == '__main__':
	main()
