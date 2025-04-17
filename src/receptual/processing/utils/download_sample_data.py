import zipfile
import tempfile
import requests
from pathlib import Path
import importlib.metadata
from tqdm import tqdm
import argparse


def download_sample_data(
	output_dir: str = None, force_download: bool = False, specific_version: str = None
):
	"""
	Download sample data from GitHub releases based on the current version.
	"""
	# Determine the version to use (current or specific)
	if specific_version:
		version = specific_version
	else:
		version = importlib.metadata.version('receptual')

	# Set default output directory if not provided
	if output_dir is None:
		output_dir = Path.cwd()

	# Create output directory if it doesn't exist
	output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)

	# Define GitHub release URL
	github_url = f'https://github.com/rory-bedford/Receptual/releases/download/v{version}/sample_data_v{version}.zip'

	print(f'Downloading sample data for receptual v{version}...')

	try:
		# Download the zip file with progress bar
		with tempfile.NamedTemporaryFile(delete=False) as temp_file:
			temp_path = Path(temp_file.name)
			response = requests.get(github_url, stream=True)

			# Get file size for progress bar
			total_size = int(response.headers.get('content-length', 0))

			# Show download progress
			with tqdm(
				total=total_size, unit='B', unit_scale=True, desc='Download'
			) as pbar:
				for chunk in response.iter_content(chunk_size=8192):
					if chunk:
						temp_file.write(chunk)
						pbar.update(len(chunk))

		# Extract the zip file
		print(f'Extracting files to {output_dir}...')
		with zipfile.ZipFile(temp_path, 'r') as zip_ref:
			zip_ref.extractall(output_dir)

		# Remove the temporary zip file
		temp_path.unlink()

		print(f'Sample data successfully downloaded to {output_dir}.')
		return str(output_dir)

	except Exception as e:
		print(f'Error downloading sample data: {e}')
		# Clean up incomplete downloads
		if Path(temp_file.name).exists():
			Path(temp_file.name).unlink()
		return None


def main():
	"""Main entry point for the command line tool."""
	parser = argparse.ArgumentParser(description='Download sample data for receptual')
	parser.add_argument(
		'--output-dir', type=str, help='Directory to save downloaded data'
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

	output_path = download_sample_data(output_dir)
	print(f'Downloaded sample data in {output_path}')


if __name__ == '__main__':
	main()
