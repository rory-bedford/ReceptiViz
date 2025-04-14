"""
Receptual: A tool for visualizing and computing neuron receptive fields.
"""

# Import key functions for easy access
from receptual.processing.core.encoder import (
	encoder as encoder,
	receptive_field as receptive_field,
)
# from receptual.processing.core.decoder import decoder

# Version is managed by pyproject.toml and setuptools_scm
try:
	from importlib.metadata import version

	__version__ = version('receptual')
except ImportError:
	__version__ = 'unknown'
