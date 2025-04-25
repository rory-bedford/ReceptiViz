import numpy as np
from pathlib import Path


def load_numpy_array(filepath: str) -> np.ndarray:
	path = Path(filepath)
	if not path.exists():
		raise FileNotFoundError(f'No file found at {filepath}')
	return np.load(path)


def save_numpy_array(filepath: str, array: np.ndarray) -> None:
	path = Path(filepath)
	assert path.suffix == '.npy', 'File extension must be .npy'
	if not path.parent.exists():
		path.parent.mkdir(parents=True, exist_ok=True)
	np.save(path, array)
