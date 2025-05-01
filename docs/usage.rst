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

Note that some arrays have too many dimensions to visualize in 3D. In this case, you have to select two axes to act as the X/Y-axes, and select a slice through the other axes to view. This is made easy with our axes and slice selection widgets. Additionally, for very large arrays, you can reduce the range of values on the X/Y-axes.

Some clarification here might help: in general, receptive fields can have both temporal and spatial components - a given visual neuron, for example, might respond to a centre-surround spatial receptive field, with a biphasic temporal component, where the centre-surround values have different signs at different times in the tim window prior to the neuron response. Additionally, within Receptual, we stack receptive fields for multiple neurons together.

Within the visualizer, you might want to view the spatial structure of this receptive field. To do this, you should select the two spatial axes, and you will clearly see the centre-surround structure of the receptive field. You can then change the kernel timestamp at which you are vieiwng the receptive field, to see how this structure changes throughout the kernel window up to the response time, and you can change the neuron to compare different neurons' receptive fields.