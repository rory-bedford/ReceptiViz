from PyQt6.QtWidgets import (QWidget, QSlider, QHBoxLayout, QLabel, QGridLayout,
                           QPushButton, QDialog, QVBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal

class RangeSlider(QWidget):
    """
    A custom widget providing a range slider with two handles
    """
    # Signal emitted when the range changes
    rangeChanged = pyqtSignal(int, int)
    
    def __init__(self, min_value=0, max_value=100, parent=None):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self._setupUI()
        
    def _setupUI(self):
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create min and max labels
        self.min_label = QLabel(f"{self.min_value}")
        self.max_label = QLabel(f"{self.max_value}")
        
        # Create sliders
        self.min_slider = QSlider(Qt.Orientation.Horizontal)
        self.min_slider.setRange(self.min_value, self.max_value)
        self.min_slider.setValue(self.min_value)
        
        self.max_slider = QSlider(Qt.Orientation.Horizontal)
        self.max_slider.setRange(self.min_value, self.max_value)
        self.max_slider.setValue(self.max_value)
        
        # Connect signals
        self.min_slider.valueChanged.connect(self._minSliderChanged)
        self.max_slider.valueChanged.connect(self._maxSliderChanged)
        
        # Add widgets to layout
        layout.addWidget(self.min_label)
        layout.addWidget(self.min_slider)
        layout.addWidget(self.max_slider)
        layout.addWidget(self.max_label)
        
    def _minSliderChanged(self, value):
        """Handle min slider value changed"""
        # Ensure min doesn't go above max
        if value > self.max_slider.value():
            self.min_slider.setValue(self.max_slider.value())
            return
            
        # Update label
        self.min_label.setText(f"{value}")
        
        # Emit signal
        self.rangeChanged.emit(self.min_slider.value(), self.max_slider.value())
        
    def _maxSliderChanged(self, value):
        """Handle max slider value changed"""
        # Ensure max doesn't go below min
        if value < self.min_slider.value():
            self.max_slider.setValue(self.min_slider.value())
            return
            
        # Update label
        self.max_label.setText(f"{value}")
        
        # Emit signal
        self.rangeChanged.emit(self.min_slider.value(), self.max_slider.value())
        
    def getRange(self):
        """Get the current range values"""
        return self.min_slider.value(), self.max_slider.value()
        
    def setRange(self, min_value, max_value):
        """Set the overall range of the slider"""
        self.min_value = min_value
        self.max_value = max_value
        
        # Update sliders
        self.min_slider.setRange(min_value, max_value)
        self.max_slider.setRange(min_value, max_value)
        
        # Update values
        self.min_slider.setValue(min_value)
        self.max_slider.setValue(max_value)
        
        # Update labels
        self.min_label.setText(f"{min_value}")
        self.max_label.setText(f"{max_value}")
        
    def setValues(self, min_val, max_val):
        """Set the current values of the sliders"""
        self.min_slider.setValue(min_val)
        self.max_slider.setValue(max_val)
        self.min_label.setText(f"{min_val}")
        self.max_label.setText(f"{max_val}")


class SliceRangeDialog(QDialog):
    """A dialog for selecting slice ranges across dimensions"""
    
    def __init__(self, dimensions, parent=None):
        """
        Initialize with dimension details
        dimensions: list of dicts with keys 'name', 'min', 'max', 'unit'
        """
        super().__init__(parent)
        self.dimensions = dimensions
        self.setWindowTitle("Select Slice Ranges")
        self.range_sliders = {}
        self.point_count_labels = {}
        self._setupUI()
        
    def _setupUI(self):
        layout = QVBoxLayout(self)
        
        # Create info label to explain the purpose
        info_label = QLabel(
            "Select range of values to include in each dimension. "
            "Use sliders to adjust min and max values."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-style: italic; color: gray; padding-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Create grid for sliders
        grid = QGridLayout()
        
        # Add header row with more descriptive labels
        grid.addWidget(QLabel("<b>Dimension</b>"), 0, 0)
        grid.addWidget(QLabel("<b>Range Selection</b>"), 0, 1)
        grid.addWidget(QLabel("<b>Points</b>"), 0, 2)
        
        # Add a range slider for each dimension
        for i, dim in enumerate(self.dimensions):
            name = dim['name']
            min_val = dim['min']
            max_val = dim['max']
            unit = dim.get('unit', '')
            
            # Create label with unit
            unit_str = f" ({unit})" if unit else ""
            label = QLabel(f"{name}{unit_str}:")
            
            # Create range slider
            slider = RangeSlider(min_val, max_val)
            self.range_sliders[name] = slider
            
            # Create label showing number of points
            points_label = QLabel(f"{max_val - min_val + 1}")
            self.point_count_labels[name] = points_label
            
            # Connect range change to update point count
            slider.rangeChanged.connect(lambda min_v, max_v, dim_name=name: 
                                       self._update_point_count(dim_name, min_v, max_v))
            
            # Add to grid
            grid.addWidget(label, i+1, 0)
            grid.addWidget(slider, i+1, 1)
            grid.addWidget(points_label, i+1, 2)
        
        layout.addLayout(grid)
        
        # Add buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
    def _update_point_count(self, dim_name, min_val, max_val):
        """Update the point count label for a dimension"""
        if dim_name in self.point_count_labels:
            points = max_val - min_val + 1
            self.point_count_labels[dim_name].setText(f"{points}")
        
    def get_ranges(self):
        """Get the selected ranges for all dimensions"""
        ranges = {}
        for name, slider in self.range_sliders.items():
            ranges[name] = slider.getRange()
        return ranges
