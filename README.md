# Receptual

[![PyPI version](https://img.shields.io/pypi/v/receptual.svg)](https://pypi.org/project/receptual/)
[![Read the Docs](https://readthedocs.org/projects/receptual/badge/?version=latest)](https://receptual.readthedocs.io/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/rory-bedford/Receptual/actions/workflows/ci.yml/badge.svg)](https://github.com/rory-bedford/Receptual/actions/workflows/ci.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![codecov](https://codecov.io/gh/rory-bedford/Receptual/graph/badge.svg?token=60S5WLF5PE)](https://codecov.io/gh/rory-bedford/Receptual)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Receptual** is a lightweight, interactive tool for computing and visualizing neuron receptive fields and linear decoders.

<p align="center">
    <img src="https://raw.githubusercontent.com/rory-bedford/Receptual/main/assets/receptive_field_black.gif" width="400">
</p>

## Overview

Linear encoding and decoding methods are essential tools for:

- Systems neuroscience
- Computational neuroscience
- Deep learning interpretability

However, these methods often produce high-dimensional arrays, which are difficult to analyze and interpret. Additionally, despite the ubiquity of linear methods, implementing them can be challenging.

Receptual helps by providing standardized algorithm implementations for linear encoding and decoding methods. We also provide a visualization tool to help you explore the high-dimensional arrays that often result from these methods.

## Key Features

- **Interactive 3D Visualization**  
  OpenGL + Qt-based viewer for receptive fields, stimuli, activity traces, and decoders

- **Efficient Algorithms**  
  Fast NumPy and SciPy implementations tailored for neuroscience use cases

## Implemented Algorithms

Receptual provides the following out-of-the-box:

- Receptive field estimation
- Linear activity encoding

## Installation

Receptual requires Python 3.13 or later and is available on PyPI:

```bash
# Using uv
uv venv $HOME/venvs/receptual --python 3.13 # or wherever you keep your environments
source $HOME/venvs/receptual/bin/activate
uv pip install receptual

# Using conda
conda create -n receptual python=3.13
conda activate receptual
pip install receptual
```

## Quick Start

Launch the visualization tool with:

```bash
receptual
```

Or use the algorithms yourself:
```python
import receptual
activity = receptual.encoder(stimulus, receptive_field)
```

## Documentation

For detailed usage instructions, examples, and API reference, please visit our [documentation](https://receptual.readthedocs.io/).
