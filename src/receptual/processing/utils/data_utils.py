import numpy as np
from pathlib import Path


def load_numpy_array(filepath: str) -> np.ndarray:
	path = Path(filepath)
	if not path.exists():
		raise FileNotFoundError(f'No file found at {filepath}')
	return np.load(path)
