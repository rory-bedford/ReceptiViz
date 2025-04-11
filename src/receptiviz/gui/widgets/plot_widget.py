from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from PyQt6.QtGui import QVector3D
from PyQt6.QtCore import Qt
from .dimension_selector import DimensionSelectorDialog

class PlotWidget(QWidget):
    def __init__(self, processor, plot_type="receptive_field", parent=None):
        super().__init__(parent)
        self.processor = processor
        self.plot_type = plot_type
        
        # Configure PyQtGraph defaults for dark theme
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'k')  # Black background
        pg.setConfigOption('foreground', 'w')  # White foreground
        
        # Default colors for plot elements
        self.plot_colors = {
            'grid': (50, 50, 50, 0.5),  # Dark gray grid with transparency
            'mesh': (0.2, 0.5, 1.0, 1.0),  # Base mesh color
            'edge': (0.9, 0.9, 1.0, 1.0),  # Edge color for wireframe
        }
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        # Initialize plots
        self._init_plot()
        
    def _init_plot(self):
        """Create the appropriate plot based on plot_type"""
        if self.plot_type == "stimulus":
            self._plot_stimulus()
        elif self.plot_type == "activity":
            self._plot_activity()
        elif self.plot_type == "receptive_field":
            self._plot_receptive_field()
            
    def _plot_activity(self):
        """Plot 1D activity data"""
        # Create plot widget with grid
        plot_widget = pg.PlotWidget()
        plot_widget.showGrid(x=True, y=True)
        
        # Get data and info
        activity = self.processor.activity
        dim_info = self.processor.get_dimension_info("activity")
        value_info = self.processor.get_value_info("activity")
        
        # Create line plot with activity data
        plot_widget.plot(activity, pen={'color': 'b', 'width': 2})
        
        # Set labels
        plot_widget.setLabel('left', value_info['name'], units=value_info['unit'])
        plot_widget.setLabel('bottom', 'Time', units=dim_info['units'][0])
        plot_widget.setTitle('Neural Activity')
        
        # Add to layout
        self.layout.addWidget(plot_widget)
        
    def _plot_stimulus(self):
        """Plot stimulus data based on dimensionality"""
        stimulus = self.processor.stimulus
        dim_info = self.processor.get_dimension_info("stimulus")
        value_info = self.processor.get_value_info("stimulus")
        
        if len(stimulus.shape) == 1:
            # 1D stimulus - simple line plot
            plot_widget = pg.PlotWidget()
            plot_widget.showGrid(x=True, y=True)
            plot_widget.plot(stimulus, pen={'color': 'b', 'width': 2})
            
            plot_widget.setLabel('left', value_info['name'], units=value_info['unit'])
            plot_widget.setLabel('bottom', dim_info['dims'][0], units=dim_info['units'][0])
            plot_widget.setTitle("1D Stimulus")
            
            self.layout.addWidget(plot_widget)
            
        elif len(stimulus.shape) == 2:
            # 2D stimulus - direct 3D wireframe plot
            self._create_3D_surface_plot(stimulus, dim_info, value_info)
            
        else:  # Higher dimensions
            # Let user select a 2D slice, but default to using time as X-axis
            self._create_3D_surface_from_highD(stimulus, dim_info, value_info)
    
    def _create_3D_surface_plot(self, data_2d, dim_info, value_info, 
                                dim0_name=None, dim0_unit=None, dim1_name=None, dim1_unit=None):
        """Create a 3D wireframe plot for 2D data"""
        # Use provided dimension names/units or extract from dim_info
        if dim0_name is None:
            dim0_name = dim_info['dims'][0]
        if dim0_unit is None:
            dim0_unit = dim_info['units'][0]
        if dim1_name is None:
            dim1_name = dim_info['dims'][1]
        if dim1_unit is None:
            dim1_unit = dim_info['units'][1]
        
        # Create axis legend label
        legend = QLabel(
            f'<span style="color: #4444FF">X: {dim1_name} ({dim1_unit})</span> &nbsp;&nbsp; '
            f'<span style="color: #FFFF44">Y: {dim0_name} ({dim0_unit})</span> &nbsp;&nbsp; '
            f'<span style="color: #44FF44">Z: {value_info["name"]} ({value_info["unit"]})</span>'
        )
        legend.setAlignment(Qt.AlignmentFlag.AlignCenter)
        legend.setStyleSheet("font-size: 12px; padding: 3px; color: white;")
        self.layout.addWidget(legend)
        
        # Create 3D plot widget
        plot_widget = gl.GLViewWidget()
        
        # Get data dimensions
        dim0_points, dim1_points = data_2d.shape
        
        # Create mesh based on data
        mesh = self._create_wireframe_mesh(data_2d)
        
        # Configure the GL view
        plot_widget.setBackgroundColor('k')
        plot_widget.setCameraPosition(
            distance=2.0 * max(dim0_points, dim1_points),
            elevation=25,
            azimuth=45
        )
        
        # Add items to the view
        plot_widget.addItem(mesh)
        
        # Add coordinate axes
        axis_length = max(dim1_points, dim0_points, np.abs(data_2d).max())
        axis = gl.GLAxisItem(size=QVector3D(axis_length, axis_length, axis_length))
        plot_widget.addItem(axis)
        
        # Add grid
        grid = gl.GLGridItem()
        grid.setSize(x=dim1_points, y=dim0_points)
        grid.setSpacing(x=dim1_points/10, y=dim0_points/10)
        grid.setColor(self.plot_colors['grid'])
        plot_widget.addItem(grid)
        
        # Add plot with stretch priority
        self.layout.addWidget(plot_widget, 1)
        
    def _create_3D_surface_from_highD(self, stimulus, dim_info, value_info):
        """Create a 3D surface plot from higher dimensional data, using time as X-axis"""
        # Show dimension selector dialog (preselect time dimension for X-axis)
        dialog = DimensionSelectorDialog(self.processor, self, preselect_dim0=0)
        if dialog.exec():
            # Get selected dimensions and slices
            selection = dialog.get_selection()
            dim1, dim2 = selection['dims']
            slices = selection['slices']
            
            # Extract the two selected dimensions
            selected_dim_names = [dim_info['dims'][dim1], dim_info['dims'][dim2]]
            selected_dim_units = [dim_info['units'][dim1], dim_info['units'][dim2]]
            
            # Create slice tuple for numpy indexing
            slice_tuple = [slice(None)] * len(stimulus.shape)
            for dim, value in slices.items():
                slice_tuple[dim] = value
            
            # Extract 2D slice
            data_slice = stimulus[tuple(slice_tuple)]
            
            # Create slice title for display
            slice_info = [f"{dim_info['dims'][d]}={v}" for d, v in slices.items()]
            slice_title = f"Slice at {', '.join(slice_info)}"
            
            # Create 3D surface plot from the 2D slice
            self._create_3D_surface_plot(
                data_slice, 
                dim_info,
                value_info,
                dim0_name=selected_dim_names[0],
                dim0_unit=selected_dim_units[0],
                dim1_name=selected_dim_names[1],
                dim1_unit=selected_dim_units[1]
            )
            
            # Add a title widget to show which slice we're viewing
            title_label = QLabel(slice_title)
            title_label.setStyleSheet("color: white; font-weight: bold;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.insertWidget(0, title_label)  # Add at the top
            
    def _create_wireframe_mesh(self, data):
        """Create a wireframe mesh from 2D data"""
        dim0_points, dim1_points = data.shape
        
        # Create coordinate grids
        x = np.linspace(-dim1_points/2, dim1_points/2, dim1_points)
        y = np.linspace(-dim0_points/2, dim0_points/2, dim0_points)
        x_grid, y_grid = np.meshgrid(x, y)
        
        # Create vertices from coordinate grids and data values
        vertices = np.vstack([
            x_grid.flatten(),
            y_grid.flatten(),
            data.flatten()
        ]).T
        
        # Create faces (triangles) for the mesh
        faces = []
        for i in range(dim0_points-1):
            for j in range(dim1_points-1):
                idx = i * dim1_points + j
                faces.extend([
                    [idx, idx+1, idx+dim1_points],
                    [idx+1, idx+dim1_points+1, idx+dim1_points]
                ])
        faces = np.array(faces)
        
        # Create mesh with wireframe appearance
        mesh_data = gl.MeshData(vertexes=vertices, faces=faces)
        mesh = gl.GLMeshItem(
            meshdata=mesh_data,
            smooth=False,
            computeNormals=True,
            shader='edgeHilight',
            glOptions='opaque',
            color=self.plot_colors['mesh'],
            edgeColor=self.plot_colors['edge'],
            drawEdges=True,
            drawFaces=False,
            edgeWidth=1.0
        )
        
        return mesh
        
    def _plot_receptive_field(self):
        """Plot receptive field correlation map"""
        result = self.processor.get_result()
        if not result:
            return
            
        # Get correlation map and dimension info
        corr_map = result['correlation_map']
        stim_info = self.processor.get_dimension_info("stimulus")
        
        # Create plot widget
        plot_widget = pg.PlotWidget()
        
        # Create image item and add to plot
        img = pg.ImageItem()
        plot_widget.addItem(img)
        img.setImage(corr_map)
        
        # Add colorbar with diverging colormap centered at zero
        max_abs = max(abs(corr_map.min()), abs(corr_map.max()))
        colorbar = pg.ColorBarItem(
            values=(-max_abs, max_abs),
            colorMap=pg.colormap.get('diverging', 'RdBu_r'),
            label='Correlation'
        )
        colorbar.setImageItem(img)
        
        # Set labels if we have dimension info
        if len(stim_info['dims']) >= 3:
            plot_widget.setLabel('left', stim_info['dims'][2], units=stim_info['units'][2])
            plot_widget.setLabel('bottom', stim_info['dims'][1], units=stim_info['units'][1])
            
        plot_widget.setTitle('Receptive Field Map')
        self.layout.addWidget(plot_widget)

