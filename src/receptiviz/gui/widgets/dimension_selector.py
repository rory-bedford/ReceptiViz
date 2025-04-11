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
        self.dim_names = dim_info['dims']
        self.dim_units = dim_info['units']
        
        # Create dimension selectors
        dim_layout = QHBoxLayout()
        self.dim_x_combo = QComboBox()  # X axis (space)
        self.dim_y_combo = QComboBox()  # Y axis (time)
        
        # Initially populate dimension combos
        self._populate_dimension_combos()
        
        # Set default selections for time on Y-axis and space on X-axis
        if preselect_dim0 is not None and preselect_dim0 < self.ndims:
            # Y-axis is preselected dimension (usually time)
            self.dim_y_combo.setCurrentIndex(self.dim_y_combo.findData(preselect_dim0))
            
            # Choose a default X-axis that's different from Y-axis
            # Use dimension 1 if available, otherwise use first dimension that's not preselect_dim0
            x_dim = 1 if preselect_dim0 != 1 and self.ndims > 1 else (0 if preselect_dim0 != 0 else 2)
            self.dim_x_combo.setCurrentIndex(self.dim_x_combo.findData(x_dim))
        else:
            # Default selections - time (dim0) on Y-axis, space (dim1) on X-axis if available
            self.dim_y_combo.setCurrentIndex(self.dim_y_combo.findData(0))  # First dimension for Y
            self.dim_x_combo.setCurrentIndex(self.dim_x_combo.findData(1 if self.ndims > 1 else 0))  # Second for X
            
        # Connect signals for combo boxes to prevent duplicate selection
        self.dim_x_combo.currentIndexChanged.connect(self._on_x_dimension_changed)
        self.dim_y_combo.currentIndexChanged.connect(self._on_y_dimension_changed)
        
        # Layout for dimension selectors
        dim_layout.addWidget(QLabel("X-axis dimension:"))
        dim_layout.addWidget(self.dim_x_combo)
        dim_layout.addWidget(QLabel("Y-axis dimension:"))
        dim_layout.addWidget(self.dim_y_combo)
        layout.addLayout(dim_layout)
        
        # Add slice selectors for other dimensions
        self.slice_spinners = {}
        self.slice_layout = QVBoxLayout()
        layout.addLayout(self.slice_layout)
        
        # Initial update of slice selectors
        self.update_slice_selectors()
        
        # Add buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def _populate_dimension_combos(self):
        """Populate dimension combo boxes with available dimensions"""
        self.dim_x_combo.clear()
        self.dim_y_combo.clear()
        
        for i, name in enumerate(self.dim_names):
            if i < len(self.dim_units):
                unit = self.dim_units[i]
                unit_str = f" ({unit})" if unit else ""
                label = f"{name}{unit_str}"
            else:
                label = name
                
            self.dim_x_combo.addItem(label, i)
            self.dim_y_combo.addItem(label, i)
    
    def _on_x_dimension_changed(self, index):
        """Handle X dimension changed - ensure Y dimension is different"""
        if index < 0:
            return
            
        x_dim = self.dim_x_combo.currentData()
        y_dim = self.dim_y_combo.currentData()
        
        # If same dimension selected, change the Y dimension
        if x_dim == y_dim:
            # Find a dimension that's not the current X dimension
            for i in range(self.ndims):
                if i != x_dim:
                    self.dim_y_combo.setCurrentIndex(self.dim_y_combo.findData(i))
                    break
                    
        # Update slice selectors after dimension change
        self.update_slice_selectors()
    
    def _on_y_dimension_changed(self, index):
        """Handle Y dimension changed - ensure X dimension is different"""
        if index < 0:
            return
            
        x_dim = self.dim_x_combo.currentData()
        y_dim = self.dim_y_combo.currentData()
        
        # If same dimension selected, change the X dimension
        if x_dim == y_dim:
            # Find a dimension that's not the current Y dimension
            for i in range(self.ndims):
                if i != y_dim:
                    self.dim_x_combo.setCurrentIndex(self.dim_x_combo.findData(i))
                    break
                    
        # Update slice selectors after dimension change
        self.update_slice_selectors()
        
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
        
        # Get currently selected dimensions
        x_dim = self.dim_x_combo.currentData()
        y_dim = self.dim_y_combo.currentData()
        selected_dims = [x_dim, y_dim]
        
        # Add spinners for dimensions not being visualized
        for i in range(self.ndims):
            if i not in selected_dims:
                slice_layout = QHBoxLayout()
                
                # Get dimension size (max value + 1)
                dim_size = self.processor.stimulus.shape[i]
                max_idx = dim_size - 1
                
                # Add dimension name with units and max value
                unit = self.dim_units[i] if i < len(self.dim_units) else ""
                unit_str = f" ({unit})" if unit else ""
                slice_layout.addWidget(QLabel(f"{self.dim_names[i]}{unit_str} slice [0-{max_idx}]:"))
                
                # Add spinner
                spinner = QSpinBox()
                spinner.setRange(0, max_idx)
                spinner.setValue(dim_size // 2)  # Default to middle slice
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
