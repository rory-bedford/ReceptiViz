.. Receptual documentation master file, created by
   sphinx-quickstart on Thu Apr 17 17:35:25 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Receptual documentation
=======================

Receptual is a simple tool for computing and visualising neuron receptive fields and linear decoders.

.. image:: images/receptive_field_white.gif
   :alt: Receptive Field GIF
   :width: 400px
   :align: center

Linear encoding and decoding methods are essential for understanding the relationship between neural activity and sensory stimuli. They are widely used in systems neuroscience, computational neuroscience, and mechanistic interpretability for deep learning.

These methods often produce high-dimensional arrays, which can be difficult to analyze and interpret. Receptual has an interactive OpenGL + Qt 3D visualisation tool for this purpose, allowing you to graphically inspect you activity traces, stimuli, receptive fields, and linear decoders.

Receptual provides out-of-the-box fast NumPy + SciPy implementations of the following algorithms:

- Receptive field estimation
- Activity encoding

We also make it easy to load your data from numpy arrays on disk, and save computation results back to disk.


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   installation
   data_prep
   overview
   appendix
   contributing
   api
