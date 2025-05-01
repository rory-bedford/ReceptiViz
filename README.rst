Receptual
=========

.. image:: https://raw.githubusercontent.com/rory-bedford/Receptual/main/assets/receptive_field_white.png
   :alt: Receptual demo
   :width: 400px
   :align: center

Badges
------

- `PyPI version <https://pypi.org/project/receptual/>`__
- `Read the Docs <https://receptual.readthedocs.io/>`__
- `Ruff <https://github.com/astral-sh/ruff>`__
- `CI <https://github.com/rory-bedford/Receptual/actions/workflows/ci.yml>`__
- `pre-commit <https://github.com/pre-commit/pre-commit>`__
- `Codecov <https://codecov.io/gh/rory-bedford/Receptual>`__
- `License: MIT <LICENSE>`__

Overview
--------

**Receptual** is a lightweight, interactive tool for computing and visualizing neuron receptive fields and linear decoders.

Linear encoding and decoding methods are essential tools for:

- Systems neuroscience
- Computational neuroscience
- Deep learning interpretability

However, these methods often produce high-dimensional arrays, which are difficult to analyze and interpret. Additionally, despite the ubiquity of linear methods, implementing them can be challenging.

Receptual helps by providing standardized algorithm implementations for linear encoding and decoding methods. We also provide a visualization tool to help you explore the high-dimensional arrays that often result from these methods.

Key Features
------------

- **Interactive 3D Visualization**  
  OpenGL + Qt-based viewer for receptive fields, stimuli, activity traces, and decoders

- **Efficient Algorithms**  
  Fast NumPy and SciPy implementations tailored for neuroscience use cases

Implemented Algorithms
----------------------

Receptual provides the following out-of-the-box:

- Receptive field estimation
- Linear activity encoding

Installation
------------

Receptual requires Python 3.13 or later and is available on PyPI:

.. code-block:: bash

   # Using uv
   uv venv $HOME/venvs/receptual --python 3.13 # or wherever you keep your environments
   source $HOME/venvs/receptual/bin/activate
   uv pip install receptual

   # Using conda
   conda create -n receptual python=3.13
   conda activate receptual
   pip install receptual

Quick Start
-----------

Launch the visualization tool with:

.. code-block:: bash

   receptual

Or use the algorithms yourself:

.. code-block:: python

   import receptual
   activity = receptual.encoder(stimulus, receptive_field)

Documentation
-------------

For detailed usage instructions, examples, and API reference, please visit our `documentation <https://receptual.readthedocs.io/>`__.
