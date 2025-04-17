import numpy as np
from pathlib import Path


def generate_test_data(output_dir: str, n_timepoints: int = 100, seed: int = 42):
	"""Generate test data with different stimulus dimensions."""
	np.random.seed(seed)

	# Create output directories
	base_dir = Path(output_dir)
	for dim in [1, 2, 3]:
		dim_dir = base_dir / f'example{dim}'
		dim_dir.mkdir(parents=True, exist_ok=True)

		# Generate activity data (always 1D)
		activity = np.random.normal(0, 1, n_timepoints)

		# Generate stimulus data based on dimension
		if dim == 1:
			# 1D stimulus (time series)
			stimulus = np.random.normal(0, 1, n_timepoints)

		elif dim == 2:
			# 2D stimulus (time x space)
			spatial_dim = 10
			stimulus = np.random.normal(0, 1, (n_timepoints, spatial_dim))

		else:  # dim == 3
			# 3D stimulus (time x height x width)
			height = width = 10
			stimulus = np.random.normal(0, 1, (n_timepoints, height, width))

			# Add some structure to make it interesting
			for t in range(n_timepoints):
				# Add a moving gaussian bump
				x = int(5 + 3 * np.sin(2 * np.pi * t / n_timepoints))
				y = int(5 + 3 * np.cos(2 * np.pi * t / n_timepoints))
				stimulus[t] += np.exp(
					-(
						(np.arange(width)[:, None] - x) ** 2
						+ (np.arange(height)[None, :] - y) ** 2
					)
					/ 4
				)

			# Make activity correlate with the center pixel
			activity = 0.7 * stimulus[:, 5, 5] + 0.3 * np.random.normal(
				0, 1, n_timepoints
			)

			# Generate receptive field - simple correlation map
			receptive_field = np.zeros((height, width))
			for i in range(height):
				for j in range(width):
					receptive_field[i, j] = np.corrcoef(activity, stimulus[:, i, j])[
						0, 1
					]

			# Save receptive field
			np.save(dim_dir / 'receptive_field.npy', receptive_field)

		# Save the data
		np.save(dim_dir / 'activity.npy', activity)
		np.save(dim_dir / 'stimulus.npy', stimulus)

		# Save metadata about the arrays
		with open(dim_dir / 'info.txt', 'w') as f:
			f.write(f'Activity shape: {activity.shape}\n')
			f.write(f'Stimulus shape: {stimulus.shape}\n')
			if dim == 3:
				f.write('Note: Activity is correlated with center pixel of stimulus\n')
				f.write(f'Receptive field shape: {receptive_field.shape}\n')


if __name__ == '__main__':
	# Find the repository root (assuming this script is in src/receptual/processing/utils)
	current_file = Path(__file__)
	repo_root = current_file.parents[4]  # Go up 4 levels to reach the repo root

	# Create a sample_data directory at the repo root
	output_dir = repo_root / 'sample_data'

	generate_test_data(output_dir)
	print(f'Generated test data in {output_dir}')
