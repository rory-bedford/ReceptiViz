from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from PyQt6.QtGui import QVector3D
from PyQt6.QtCore import Qt
from .dimension_selector import DimensionSelectorDialog
from .range_slider import SliceRangeDialog

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
        """Plot activity data with range selection"""
        activity = self.processor.activity
        dim_info = self.processor.get_dimension_info("activity")
        value_info = self.processor.get_value_info("activity")
        
        # Define time dimension for range selection
        dimensions = [{
            'name': 'time',
            'min': 0,
            'max': len(activity) - 1,
            'unit': dim_info['units'][0] if len(dim_info['units']) > 0 else ''
        }]
        
        # Show slice range dialog
        slice_dialog = SliceRangeDialog(dimensions, self)
        if slice_dialog.exec():
            # Get selected range
            time_range = slice_dialog.get_ranges()['time']
            min_t, max_t = time_range
            
            # Slice activity data
            sliced_activity = activity[min_t:max_t+1]
            
            # Create plot
            plot_widget = pg.PlotWidget()
            plot_widget.showGrid(x=True, y=True)
            plot_widget.plot(sliced_activity, pen={'color': 'b', 'width': 2})
            
            # Get time unit for display
            time_unit = dim_info['units'][0] if len(dim_info['units']) > 0 else ''
            unit_str = f" {time_unit}" if time_unit else ""
            
            # Create more descriptive labels with range info
            plot_widget.setLabel('left', value_info['name'], units=value_info['unit'])
            plot_widget.setLabel('bottom', 'Time', units=time_unit)
            plot_widget.setTitle(f'Neural Activity (Frames {min_t}-{max_t}{unit_str}, {max_t-min_t+1} points)')
            
            self.layout.addWidget(plot_widget)
    
    def _plot_stimulus(self):
        """Plot stimulus data based on dimensionality"""
        stimulus = self.processor.stimulus
        dim_info = self.processor.get_dimension_info("stimulus")
        value_info = self.processor.get_value_info("stimulus")
        
        # Define dimensions for slice range selection
        dimensions = []
        for i, name in enumerate(dim_info['dims']):
            if i < len(dim_info['units']):
                unit = dim_info['units'][i]
            else:
                unit = ''
                
            dimensions.append({
                'name': name,
                'min': 0,
                'max': stimulus.shape[i] - 1,
                'unit': unit
            })
        
        # Show slice range dialog
        slice_dialog = SliceRangeDialog(dimensions, self)
        if slice_dialog.exec():
            # Get selected ranges
            ranges = slice_dialog.get_ranges()
            
            # Apply ranges to create slice
            slice_indices = [slice(ranges[dim['name']][0], ranges[dim['name']][1] + 1) 
                            for dim in dimensions]
                            
            # Build range info for titles
            range_info = {}
            for dim in dimensions:
                name = dim['name']
                min_val, max_val = ranges[name]
                range_info[name] = (min_val, max_val)
                
            # Get sliced data
            sliced_stimulus = stimulus[tuple(slice_indices)]
            
            # Now proceed with plotting based on dimensionality of sliced data
            if len(sliced_stimulus.shape) == 1:
                self._plot_1d_stimulus(sliced_stimulus, dim_info, value_info, range_info)
            elif len(sliced_stimulus.shape) == 2:
                self._create_3D_surface_plot(sliced_stimulus, dim_info, value_info, range_info=range_info)
            else:
                # Still higher-dimensional, use the dimension selector
                self._create_3D_surface_from_highD(sliced_stimulus, dim_info, value_info, range_info=range_info)
    
    def _plot_1d_stimulus(self, stimulus_1d, dim_info, value_info, range_info=None):
        """Plot 1D stimulus data with range information"""
        plot_widget = pg.PlotWidget()
        plot_widget.showGrid(x=True, y=True)
        plot_widget.plot(stimulus_1d, pen={'color': 'b', 'width': 2})
        
        # Get dimension info
        dim_name = dim_info['dims'][0]
        dim_unit = dim_info['units'][0] if len(dim_info['units']) > 0 else ''
        unit_str = f" {dim_unit}" if dim_unit else ""
        
        # Create labels
        plot_widget.setLabel('left', value_info['name'], units=value_info['unit'])
        plot_widget.setLabel('bottom', dim_name, units=dim_unit)
        
        # Add range info to title if available
        if range_info:
            min_val, max_val = range_info[dim_name]
            plot_widget.setTitle(f"1D Stimulus ({dim_name}: {min_val}-{max_val}{unit_str}, {max_val-min_val+1} points)")
        else:
            plot_widget.setTitle("1D Stimulus")
        
        self.layout.addWidget(plot_widget)
    
    def _create_3D_surface_plot(self, data_2d, dim_info, value_info, 
                                dim0_name=None, dim0_unit=None, dim1_name=None, dim1_unit=None,
                                range_info=None):
        """Create a 3D wireframe plot for 2D data with range information"""
        # Use provided dimension names/units or extract from dim_info
        if dim0_name is None:  # Y-axis
            dim0_name = dim_info['dims'][0]
        if dim0_unit is None:
            dim0_unit = dim_info['units'][0]
        if dim1_name is None:  # X-axis
            dim1_name = dim_info['dims'][1]
        if dim1_unit is None:
            dim1_unit = dim_info['units'][1]
        
        # Create axis legend with consistent color coding and range information
        legend_text = [
            f'<span style="color: #4444FF">X: {dim1_name} ({dim1_unit})</span>',
            f'<span style="color: #FFFF44">Y: {dim0_name} ({dim0_unit})</span>',
            f'<span style="color: #44FF44">Z: {value_info["name"]} ({value_info["unit"]})</span>'
        ]
        
        # Add range information if available
        if range_info:
            # For X-axis (dim1)
            if dim1_name in range_info:
                x_min, x_max = range_info[dim1_name]
                legend_text[0] += f' [{x_min}-{x_max}]'
                
            # For Y-axis (dim0)
            if dim0_name in range_info:
                y_min, y_max = range_info[dim0_name]
                legend_text[1] += f' [{y_min}-{y_max}]'
        
        # Build final legend
        legend = QLabel(' &nbsp;&nbsp; '.join(legend_text))
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
        
    def _create_3D_surface_from_highD(self, stimulus, dim_info, value_info, range_info=None):
        """Create a 3D surface plot from higher dimensional data, using time as Y-axis"""
        # Show dimension selector dialog (preselect time dimension for Y-axis)
        dialog = DimensionSelectorDialog(self.processor, self, preselect_dim0=0)
        if dialog.exec():
            # Get selected dimensions and slices
            selection = dialog.get_selection()
            x_dim, y_dim = selection['dims']  # Unpack x and y dimensions
            slices = selection['slices']
            
            # Get dimension names and units
            x_name = dim_info['dims'][x_dim]
            x_unit = dim_info['units'][x_dim]
            y_name = dim_info['dims'][y_dim]
            y_unit = dim_info['units'][y_dim]
            
            # Create a safer slice extraction approach
            data_slice = None
            try:
                # Create indexing tuple to extract the desired 2D slice
                idx = [0] * len(stimulus.shape)
                
                # For the dimensions we want to visualize, use full slices
                idx[x_dim] = slice(None)
                idx[y_dim] = slice(None)
                
                # For other dimensions, use the specific index values
                for dim, value in slices.items():
                    idx[dim] = value
                
                # Get the slice
                data_slice = stimulus[tuple(idx)]
                
                # If x_dim comes before y_dim in the array, we need to transpose
                # to get the expected orientation (y_dim, x_dim)
                if x_dim < y_dim:
                    data_slice = data_slice.T
                
            except Exception as e:
                # Show error in the plot area
                error_label = QLabel(f"Error extracting slice: {str(e)}")
                error_label.setStyleSheet("color: red; font-weight: bold;")
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.layout.addWidget(error_label)
                return
            
            # Create slice title with max index information
            slice_info = []
            for d, v in slices.items():
                dim_name = dim_info['dims'][d]
                dim_unit = dim_info['units'][d] if d < len(dim_info['units']) else ""
                max_idx = stimulus.shape[d] - 1  # Get max index for this dimension
                
                if dim_unit:
                    slice_info.append(f"{dim_name} = {v}/{max_idx} ({dim_unit})")
                else:
                    slice_info.append(f"{dim_name} = {v}/{max_idx}")
            
            slice_title = f"Slice at {', '.join(slice_info)}"
            
            # Add a title widget to show which slice we're viewing
            title_label = QLabel(slice_title)
            title_label.setStyleSheet("color: white; font-weight: bold;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(title_label)
            
            # Create 3D surface plot if we have valid data
            if data_slice is not None:
                self._create_3D_surface_plot(
                    data_slice, 
                    dim_info,
                    value_info,
                    dim0_name=y_name,  # First dimension (Y-axis)
                    dim0_unit=y_unit,
                    dim1_name=x_name,  # Second dimension (X-axis)
                    dim1_unit=x_unit,
                    range_info=range_info
                )
            
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
        """Plot receptive field with optional range selection"""
        # First process the data if needed
        if not self.processor.get_result():
            # Validate compatibility between arrays
            self.processor.validate_compatibility()
            
            if self.processor.get_errors():
                error_label = QLabel("\n".join(self.processor.get_errors()))
                error_label.setStyleSheet("color: red;")
                self.layout.addWidget(error_label)
                return
                
            # Process the data
            self.processor.process()
            
            if self.processor.get_errors():
                error_label = QLabel("\n".join(self.processor.get_errors()))
                error_label.setStyleSheet("color: red;")
                self.layout.addWidget(error_label)
                return
        
        result = self.processor.get_result()
        corr_map = result['correlation_map']
        stim_info = self.processor.get_dimension_info("stimulus")
        
        # Define dimensions for range selection if correlation map has 2+ dimensions
        if len(corr_map.shape) >= 2:
            dimensions = []
            for i, dim in enumerate(corr_map.shape):
                name = f"dim_{i}"
                unit = ''
                
                # Try to get proper dimension name
                if i + 1 < len(stim_info['dims']):  # Skip time dimension (0)
                    name = stim_info['dims'][i + 1]
                    if i + 1 < len(stim_info['units']):
                        unit = stim_info['units'][i + 1]
                
                dimensions.append({
                    'name': name,
                    'min': 0,
                    'max': corr_map.shape[i] - 1,
                    'unit': unit
                })
            
            # Show slice range dialog
            slice_dialog = SliceRangeDialog(dimensions, self)
            if slice_dialog.exec():
                # Get selected ranges
                ranges = slice_dialog.get_ranges()
                
                # Build range info strings for title
                range_strs = []
                for i, dim in enumerate(dimensions):
                    name = dim['name']
                    min_val, max_val = ranges[name]
                    unit = dim.get('unit', '')
                    unit_str = f" {unit}" if unit else ""
                    range_strs.append(f"{name}: {min_val}-{max_val}{unit_str}")
                
                # Apply ranges to create slice
                slice_indices = []
                for i, dim in enumerate(dimensions):
                    min_val, max_val = ranges[dim['name']]
                    slice_indices.append(slice(min_val, max_val + 1))
                    
                # Slice correlation map
                corr_map = corr_map[tuple(slice_indices)]
        
        # Plot the correlation map (possibly sliced)
        plot_widget = pg.PlotWidget()
        img = pg.ImageItem()
        plot_widget.addItem(img)
        img.setImage(corr_map)
        
        # Add colorbar
        max_abs = max(abs(corr_map.min()), abs(corr_map.max()))
        colorbar = pg.ColorBarItem(
            values=(-max_abs, max_abs),
            colorMap=pg.colormap.get('diverging', 'RdBu_r'),
            label='Correlation'
        )
        colorbar.setImageItem(img)
        
        # Set labels based on dimension names
        if len(stim_info['dims']) >= 3:
            y_label = stim_info['dims'][2] 
            y_unit = stim_info['units'][2] if len(stim_info['units']) > 2 else ''
            
            x_label = stim_info['dims'][1]
            x_unit = stim_info['units'][1] if len(stim_info['units']) > 1 else ''
            
            plot_widget.setLabel('left', y_label, units=y_unit)
            plot_widget.setLabel('bottom', x_label, units=x_unit)
            
        # Set title with range information if available
        if len(corr_map.shape) >= 2 and 'range_strs' in locals():
            plot_widget.setTitle(f'Receptive Field Map ({", ".join(range_strs)})')
        else:
            plot_widget.setTitle('Receptive Field Map')
            
        self.layout.addWidget(plot_widget)

