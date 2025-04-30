Usage
=====

Launching the App
-----------------

Receptual's graphical user interface can be launched in your activated environment by simply running:

.. code-block:: bash

   receptual

In addition to the GUI, Receptual's core algorithms are available as Python functions for use in your own scripts.  
See the **API Reference** for details.

GUI Overview
------------

The GUI features a menu bar at the top, with options to:

- **Load** data from disk
- **Compute** derived arrays
- **Save** results back to disk
- **Plot** currently available data

**Data Consistency Rule:**  
To enforce consistency, you can only load data that cannot be computed from already-loaded arrays. For example:

- You may load a **stimulus** and a **receptive field** array, and then compute **activity**.
- You may not load all three arrays simultaneously.

You can **plot** or **save** any array that has been either loaded or computed.  
Use the **Refresh** button at any time to clear all data from the interface.

Sample Data
-----------

To get started, you can download and explore sample datasets directly within the GUI.  
These demonstrate typical **spatial** and **temporal** receptive fields, and help build intuition for how the tool works.

Visualization Tool
------------------

The built-in visualizer uses **OpenGL** for 3D rendering. It displays:

- **Z-axis:** Values from the array
- **X/Y-axes:** Two chosen dimensions of the array

This interactive visualization helps you explore the shape and structure of your data in 3D space.
