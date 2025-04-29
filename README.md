# Receptual

[![PyPI version](https://img.shields.io/pypi/v/receptual.svg)](https://pypi.org/project/receptual/)
[![Read the Docs](https://readthedocs.org/projects/receptual/badge/?version=latest)](https://receptual.readthedocs.io/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/rory-bedford/Receptual/actions/workflows/ci.yml/badge.svg)](https://github.com/rory-bedford/Receptual/actions/workflows/ci.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![codecov](https://codecov.io/gh/rory-bedford/Receptual/graph/badge.svg?token=60S5WLF5PE)](https://codecov.io/gh/rory-bedford/Receptual)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Receptual is a simple tool for computing and visualising neuron receptive fields and decoding filters.

<p align="center">
    <img src="assets/receptive_field.gif" width="400">
</p>

Linear encoding and decoding methods are essential for understanding the relationship between neural activity and sensory stimuli. They are widely used in systems neuroscience, computational neuroscience, and mechanistic interpretability for deep learning.

These methods often produce high-dimensional arrays, which can be difficult to analyze and interpret. Receptual has an interactive OpenGL + Qt 3D visualisation tool for this purpose, allowing you to graphically inspect you activity traces, stimuli, receptive fields, and decoding filters.

Receptual provides out-of-the-box fast NumPy + SciPy implementations of the following algorithms:

* Receptive field estimation

* Activity encoding

We also make it easy to load your data from numpy arrays on disk, and save computation results back to disk.

To get started with Receptual, please see our [documentation](https://www.receptual.readthedocs.io/)
