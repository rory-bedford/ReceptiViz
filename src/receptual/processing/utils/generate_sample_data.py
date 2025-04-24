import numpy as np
import argparse
from pathlib import Path
from receptual import encoder


def generate_white_stimulus(shape: tuple) -> np.ndarray:
	"""Generate a white stimulus with the given shape."""
	stimulus = np.random.randn(*shape)
	return stimulus


def generate_centre_surround() -> np.ndarray:
	"""
	Generate a centre-surround stimulus.
	Returns:
		np.ndarray: The generated centre-surround stimulus.
	Notes:
		- The centre-surround stimulus is generated using two Gaussian functions.
		- K: 1
		- N: 1
		- S: (40,40)
	"""
	shape = (40, 40)
	mean = (20, 20)
	sigma1 = (4, 4)
	sigma2 = (8, 8)

	y, x = np.indices(shape)
	centre_surround = 1.5 * np.exp(
		-((x - mean[0]) ** 2 + (y - mean[1]) ** 2) / (2 * sigma1[0] ** 2)
	)
	centre_surround -= np.exp(
		-((x - mean[0]) ** 2 + (y - mean[1]) ** 2) / (2 * sigma2[0] ** 2)
	)

	centre_surround = centre_surround / np.max(np.abs(centre_surround))
	centre_surround = centre_surround[np.newaxis, np.newaxis, :, :]

	return centre_surround


def generate_on_off() -> np.ndarray:
	"""
	Generate an on-off stimulus.
	Returns:
		np.ndarray: The generated on-off stimulus.
	Notes:
		- The on-off stimulus is generated using two Gaussian functions.
		- K: 20
		- N: 1
		- S: (40,40)
	"""
	shape = (40, 40)
	mean1 = (30, 30)
	mean2 = (10, 10)
	sigma1 = (6, 6)
	sigma2 = (6, 6)

	y, x = np.indices(shape)
	on_off = np.exp(-((x - mean1[0]) ** 2 + (y - mean1[1]) ** 2) / (2 * sigma1[0] ** 2))
	on_off -= np.exp(
		-((x - mean2[0]) ** 2 + (y - mean2[1]) ** 2) / (2 * sigma2[0] ** 2)
	)

	t = np.indices((20,))
	time_component = np.sin(t[0] / 20 * 2 * np.pi) * np.exp(-t[0] / 20)

	on_off = time_component[:, np.newaxis, np.newaxis] * on_off[np.newaxis, :, :]
	on_off = on_off / np.max(np.abs(on_off))
	on_off = on_off[:, np.newaxis, ...]

	return on_off


def generate_gabor_filters() -> np.ndarray:
	"""
	Generate Gabor filters for ten neurons with different orientations.

	Returns:
		np.ndarray: The generated Gabor filters with shape (1, 10, 40, 40)
					(kernel=1, neurons=10, height=40, width=40)

	Notes:
		- Each Gabor filter has a different orientation (theta)
		- The spatial frequency remains constant across filters
		- Theta controls only the orientation, not the spatial frequency
	"""
	shape = (40, 40)
	mean = (20, 20)
	sigma = (8, 8)
	frequency = 0.16  # Spatial frequency (cycles per pixel)
	thetas = [i * np.pi / 10 for i in range(10)]  # Different orientations

	y, x = np.indices(shape)
	gabors = []

	for theta in thetas:
		# Create coordinate system rotated by theta
		x_theta = (x - mean[0]) * np.cos(theta) + (y - mean[1]) * np.sin(theta)
		y_theta = -(x - mean[0]) * np.sin(theta) + (y - mean[1]) * np.cos(theta)

		# Gaussian envelope
		gaussian = np.exp(-(x_theta**2 + y_theta**2) / (2 * sigma[0] ** 2))

		# Cosine carrier - frequency only in x_theta direction
		carrier = np.cos(2 * np.pi * frequency * x_theta)

		# Complete Gabor filter
		gabor = gaussian * carrier
		gabors.append(gabor)

	gabor_filters = np.stack(gabors, axis=0)
	gabor_filters = gabor_filters / np.max(np.abs(gabor_filters))
	gabor_filters = gabor_filters[np.newaxis, ...]

	return gabor_filters


def generate_moving_gaussian() -> np.ndarray:
	"""
	Generate a moving Gaussian stimulus.
	Returns:
		np.ndarray: The generated moving Gaussian stimulus.
	Notes:
		- The moving Gaussian stimulus is generated using a Gaussian function.
		- K: 20
		- N: 1
		- S: (40,40)
	"""
	shape = (40, 40)
	sigma = (5, 5)
	y, x = np.indices(shape)
	moving_mean = np.linspace(5, 35, 20)

	stacked_gaussians = []
	for mean in moving_mean:
		moving_gaussian = np.exp(
			-((x - mean) ** 2 + (y - mean) ** 2) / (2 * sigma[0] ** 2)
		)
		stacked_gaussians.append(moving_gaussian)

	moving_gaussian = np.stack(stacked_gaussians, axis=0)
	moving_gaussian = moving_gaussian / np.max(np.abs(moving_gaussian))
	moving_gaussian = moving_gaussian[:, np.newaxis, ...]

	return moving_gaussian


def generate_test_data(output_dir: str, seed: int = 42):
	"""Generate test data to visualize the functionality of the receptual package."""
	np.random.seed(seed)

	base_dir = Path(output_dir)
	base_dir.mkdir(parents=True, exist_ok=True)

	# Make centre-surround data
	receptive_field = generate_centre_surround()
	stimulus = generate_white_stimulus((10000, 40, 40))
	activity = encoder(stimulus, receptive_field)
	centre_surround_dir = base_dir / 'encoding' / 'centre_surround'
	centre_surround_dir.mkdir(parents=True, exist_ok=True)
	np.save(centre_surround_dir / 'stimulus.npy', stimulus)
	np.save(centre_surround_dir / 'receptive_field.npy', receptive_field)
	np.save(centre_surround_dir / 'activity.npy', activity)

	# Make on-off data
	receptive_field = generate_on_off()
	stimulus = generate_white_stimulus((10000, 40, 40))
	activity = encoder(stimulus, receptive_field)
	on_off_dir = base_dir / 'encoding' / 'on_off'
	on_off_dir.mkdir(parents=True, exist_ok=True)
	np.save(on_off_dir / 'stimulus.npy', stimulus)
	np.save(on_off_dir / 'receptive_field.npy', receptive_field)
	np.save(on_off_dir / 'activity.npy', activity)

	# Make Gabor filters data
	receptive_field = generate_gabor_filters()
	stimulus = generate_white_stimulus((10000, 40, 40))
	activity = encoder(stimulus, receptive_field)
	gabor_dir = base_dir / 'encoding' / 'gabor'
	gabor_dir.mkdir(parents=True, exist_ok=True)
	np.save(gabor_dir / 'stimulus.npy', stimulus)
	np.save(gabor_dir / 'receptive_field.npy', receptive_field)
	np.save(gabor_dir / 'activity.npy', activity)

	# Make moving Gaussian data
	receptive_field = generate_moving_gaussian()
	stimulus = generate_white_stimulus((10000, 40, 40))
	activity = encoder(stimulus, receptive_field)
	moving_gaussian_dir = base_dir / 'encoding' / 'moving_gaussian'
	moving_gaussian_dir.mkdir(parents=True, exist_ok=True)
	np.save(moving_gaussian_dir / 'stimulus.npy', stimulus)
	np.save(moving_gaussian_dir / 'receptive_field.npy', receptive_field)
	np.save(moving_gaussian_dir / 'activity.npy', activity)

	return base_dir


def main():
	"""Main entry point for the command line tool."""
	parser = argparse.ArgumentParser(description='Generate test data for receptual')
	parser.add_argument(
		'--output-dir', type=str, help='Directory to save generated data'
	)

	args = parser.parse_args()

	# If no output directory is specified, use the default location
	if args.output_dir is None:
		# Find the repository root
		current_file = Path(__file__)
		repo_root = current_file.parents[4]  # Go up 4 levels to reach the repo root
		output_dir = repo_root / 'sample_data'
	else:
		output_dir = args.output_dir

	output_path = generate_test_data(output_dir)
	print(f'Generated test data in {output_path}')


if __name__ == '__main__':
	main()
