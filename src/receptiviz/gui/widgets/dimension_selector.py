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
        self.dim1_combo = QComboBox()
        self.dim2_combo = QComboBox()
        
        # Add dimension names to combos
        for i, name in enumerate(dim_info['dims']):
            self.dim1_combo.addItem(f"{name} ({dim_info['units'][i]})", i)
            self.dim2_combo.addItem(f"{name} ({dim_info['units'][i]})", i)
            
        # Set default selections
        # If specified, use preselected dim for X-axis (usually time)
        if preselect_dim0 is not None and preselect_dim0 < self.ndims:
            self.dim1_combo.setCurrentIndex(preselect_dim0)
            # Choose a different dimension for Y
            self.dim2_combo.setCurrentIndex(1 if preselect_dim0 != 1 else 2)
        else:
            # Default selections
            self.dim1_combo.setCurrentIndex(1)  # Second dimension by default
            self.dim2_combo.setCurrentIndex(2 if self.ndims > 2 else 0)  # Third or first
        
        # Add label for X axis (usually time)
        dim_layout.addWidget(QLabel("X-axis dimension:"))
        dim_layout.addWidget(self.dim1_combo)
        dim_layout.addWidget(QLabel("Y-axis dimension:"))
        dim_layout.addWidget(self.dim2_combo)
        
        layout.addLayout(dim_layout)
        
        # Add slice selectors for other dimensions
        self.slice_spinners = {}
        self.slice_layout = QVBoxLayout()
        
        for i, name in enumerate(dim_info['dims']):
            if i not in [self.dim1_combo.currentData(), self.dim2_combo.currentData()]:
                slice_layout = QHBoxLayout()
                slice_layout.addWidget(QLabel(f"{name} slice:"))
                spinner = QSpinBox()
                spinner.setRange(0, processor.stimulus.shape[i] - 1)
                spinner.setValue(processor.stimulus.shape[i] // 2)  # Default to middle slice
                self.slice_spinners[i] = spinner
                slice_layout.addWidget(spinner)
                self.slice_layout.addLayout(slice_layout)
                
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
        self.dim1_combo.currentIndexChanged.connect(self.update_slice_selectors)
        self.dim2_combo.currentIndexChanged.connect(self.update_slice_selectors)
        
    def update_slice_selectors(self):
        """Update which dimensions need slice selection"""
        # Clear existing slice selectors
        for i in reversed(range(self.slice_layout.count())): 
            self.slice_layout.itemAt(i).layout().itemAt(1).widget().deleteLater()
            self.slice_layout.itemAt(i).layout().itemAt(0).widget().deleteLater()
            self.slice_layout.removeItem(self.slice_layout.itemAt(i))
        
        self.slice_spinners.clear()
        
        # Add new slice selectors
        dim_info = self.processor.get_dimension_info("stimulus")
        selected_dims = [self.dim1_combo.currentData(), self.dim2_combo.currentData()]
        
        for i, name in enumerate(dim_info['dims']):
            if i not in selected_dims:
                slice_layout = QHBoxLayout()
                slice_layout.addWidget(QLabel(f"{name} slice:"))
                spinner = QSpinBox()
                spinner.setRange(0, self.processor.stimulus.shape[i] - 1)
                spinner.setValue(self.processor.stimulus.shape[i] // 2)
                self.slice_spinners[i] = spinner
                slice_layout.addWidget(spinner)
                self.slice_layout.addLayout(slice_layout)
                
    def get_selection(self):
        """Return the selected dimensions and slices"""
        return {
            'dims': (self.dim1_combo.currentData(), self.dim2_combo.currentData()),
            'slices': {dim: spinner.value() for dim, spinner in self.slice_spinners.items()}
        }
