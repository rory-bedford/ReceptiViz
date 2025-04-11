from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox, 
                           QLabel, QPushButton, QSpinBox)

class DimensionSelectorDialog(QDialog):
    def __init__(self, processor, parent=None, preselect_dim0=None):
        super().__init__(parent)
        self.processor = processor
        self.setWindowTitle("Select Dimensions to Plot")
        
        layout = QVBoxLayout(self)
        
        # Get dimension info
        dim_info = processor.get_dimension_info("stimulus")
        self.ndims = len(dim_info['dims'])
        
        # Create dimension selectors
        dim_layout = QHBoxLayout()
        self.dim_x_combo = QComboBox()  # X axis (space)
        self.dim_y_combo = QComboBox()  # Y axis (time)
        
        # Add dimension names to combos
        for i, name in enumerate(dim_info['dims']):
            self.dim_x_combo.addItem(f"{name} ({dim_info['units'][i]})", i)
            self.dim_y_combo.addItem(f"{name} ({dim_info['units'][i]})", i)
            
        # Set default selections for time on Y-axis and space on X-axis
        # Typically time is dimension 0, space is dimension 1
        if preselect_dim0 is not None and preselect_dim0 < self.ndims:
            self.dim_y_combo.setCurrentIndex(preselect_dim0)  # Y-axis is time
            # Choose a different dimension for X
            self.dim_x_combo.setCurrentIndex(1 if preselect_dim0 != 1 else 2)
        else:
            # Default selections - time (dim0) on Y-axis, space (dim1) on X-axis
            self.dim_y_combo.setCurrentIndex(0)  # First dimension (time) for Y-axis
            self.dim_x_combo.setCurrentIndex(1)  # Second dimension (space) for X-axis
        
        # Add labels with clear naming
        dim_layout.addWidget(QLabel("X-axis dimension:"))
        dim_layout.addWidget(self.dim_x_combo)
        dim_layout.addWidget(QLabel("Y-axis dimension:"))
        dim_layout.addWidget(self.dim_y_combo)
        
        layout.addLayout(dim_layout)
        
        # Add slice selectors for other dimensions
        self.slice_spinners = {}
        self.slice_layout = QVBoxLayout()
        
        # Initial update of slice selectors
        self.update_slice_selectors()
        
        layout.addLayout(self.slice_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Connect dimension combo changes
        self.dim_x_combo.currentIndexChanged.connect(self.update_slice_selectors)
        self.dim_y_combo.currentIndexChanged.connect(self.update_slice_selectors)
        
    def update_slice_selectors(self):
        """Update which dimensions need slice selection"""
        # Clear existing slice selectors
        for i in reversed(range(self.slice_layout.count())): 
            layout_item = self.slice_layout.itemAt(i)
            if layout_item.layout():
                while layout_item.layout().count():
                    widget_item = layout_item.layout().takeAt(0)
                    if widget_item.widget():
                        widget_item.widget().deleteLater()
                self.slice_layout.removeItem(layout_item)
        
        self.slice_spinners.clear()
        
        # Add new slice selectors
        dim_info = self.processor.get_dimension_info("stimulus")
        selected_dims = [self.dim_x_combo.currentData(), self.dim_y_combo.currentData()]
        
        for i, name in enumerate(dim_info['dims']):
            if i not in selected_dims:
                slice_layout = QHBoxLayout()
                
                # Add dimension name with units
                unit = dim_info['units'][i] if i < len(dim_info['units']) else ""
                unit_str = f" ({unit})" if unit else ""
                slice_layout.addWidget(QLabel(f"{name}{unit_str} slice:"))
                
                # Add spinner
                spinner = QSpinBox()
                spinner.setRange(0, self.processor.stimulus.shape[i] - 1)
                spinner.setValue(self.processor.stimulus.shape[i] // 2)
                self.slice_spinners[i] = spinner
                slice_layout.addWidget(spinner)
                
                # Add layout to main layout
                self.slice_layout.addLayout(slice_layout)
                
    def get_selection(self):
        """Return the selected dimensions and slices"""
        return {
            'dims': (self.dim_x_combo.currentData(), self.dim_y_combo.currentData()),
            'slices': {dim: spinner.value() for dim, spinner in self.slice_spinners.items()}
        }
