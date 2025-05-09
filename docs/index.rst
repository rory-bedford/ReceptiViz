Receptual Documentation
=======================

**Receptual** is a lightweight, interactive tool for computing and visualizing neuron receptive fields and linear decoders.

.. image:: _static/logo_white_rotating.gif
   :alt: Receptive Field GIF
   :width: 400px
   :align: center

Overview
--------

Linear encoding and decoding methods are essential tools for:

- Systems neuroscience
- Computational neuroscience
- Deep learning interpretability

However, these methods often produce high-dimensional arrays, which are difficult to analyze and interpret. Additionally, despite the ubiquity of linear methods, implementing them can be challenging.

Receptual helps by providing standardized algorithm implementations for linear encoding and decoding methods. We also provide a visualization tool to help you explore the high-dimensional arrays that often result from these methods. Finally, we have detailed mathematical documentation of what exactly linear encoding and decoding methods are and how they are implemented.

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

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   installation
   data_prep
   usage
   appendix
   contributing
   api
