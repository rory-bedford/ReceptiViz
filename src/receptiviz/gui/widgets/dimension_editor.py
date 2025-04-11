from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QFormLayout, QGroupBox, QPushButton, QDialog, QTabWidget)
from PyQt6.QtCore import pyqtSignal

class DimensionEditor(QWidget):
    """Widget for editing dimension names and units"""
    
    # Signal with array_type, dimension names, and units
    dimensions_changed = pyqtSignal(str, list, list)
    
    def __init__(self, processor, array_type, parent=None):
        super().__init__(parent)
        self.processor = processor  # Reference to the ReceptiveFieldProcessor
        self.array_type = array_type  # "activity" or "stimulus"
        
        # Setup UI
        self.layout = QVBoxLayout(self)
        self.setup_ui()
        
    def setup_ui(self):
        # Initial empty state
        self.layout.addWidget(QLabel("No dimensions to edit"))
    
    def update_ui(self):
        """Update UI based on current processor state"""
        # Clear existing UI
        self.clear_layout()
        
        # Get array data and dimension info
        array = self.processor.activity if self.array_type == "activity" else self.processor.stimulus
        
        if array is None:
            self.layout.addWidget(QLabel("No data loaded"))
            return
            
        shape = array.shape
        
        dim_info = self.processor.get_dimension_info(self.array_type)
        dim_names = dim_info.get("dims", []) if dim_info else []
        dim_units = dim_info.get("units", []) if dim_info else []
        
        # Title
        self.layout.addWidget(QLabel(f"{self.array_type.capitalize()} Dimensions:"))
        
        # Create form for dimension editors
        form = QFormLayout()
        
        # Add dimension editors
        for i in range(len(shape)):
            box = QGroupBox(f"Dimension {i} (size: {shape[i]})")
            box_layout = QFormLayout(box)
            
            # Use default values if dimensions not defined
            name = dim_names[i] if i < len(dim_names) else ("time" if i == 0 else f"dim_{i}")
            unit = dim_units[i] if i < len(dim_units) else ("frames" if i == 0 else "units")
            
            name_edit = QLineEdit(name)
            unit_edit = QLineEdit(unit)
            
            box_layout.addRow("Name:", name_edit)
            box_layout.addRow("Units:", unit_edit)
            
            # Connect signals with dimension index
            name_edit.textChanged.connect(lambda text, idx=i, field="name": self.on_field_changed(idx, field, text))
            unit_edit.textChanged.connect(lambda text, idx=i, field="unit": self.on_field_changed(idx, field, text))
            
            form.addRow(box)
        
        self.layout.addLayout(form)
    
    def on_field_changed(self, index, field_type, text):
        """Handle field changes - collect current values and emit signal"""
        # Get current dimension info from processor
        dim_info = self.processor.get_dimension_info(self.array_type)
        dim_names = dim_info.get("dims", []).copy() if dim_info else []
        dim_units = dim_info.get("units", []).copy() if dim_info else []
        
        # Ensure lists are long enough
        array = self.processor.activity if self.array_type == "activity" else self.processor.stimulus
        if array is None:
            return
            
        while len(dim_names) < len(array.shape):
            dim_names.append("time" if len(dim_names) == 0 else f"dim_{len(dim_names)}")
        
        while len(dim_units) < len(array.shape):
            dim_units.append("frames" if len(dim_units) == 0 else "units")
        
        # Update the changed field
        if field_type == "name" and 0 <= index < len(dim_names):
            dim_names[index] = text
        elif field_type == "unit" and 0 <= index < len(dim_units):
            dim_units[index] = text
        
        # Emit signal to update processor
        self.dimensions_changed.emit(self.array_type, dim_names, dim_units)
    
    def clear_layout(self):
        """Clear all widgets from the layout"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                # Clear sublayouts recursively
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget() is not None:
                        child.widget().deleteLater()

class DimensionEditorDialog(QDialog):
    """Dialog for editing dimensions and data value info for both arrays"""
    
    def __init__(self, processor, parent=None):
        super().__init__(parent)
        self.processor = processor
        self.setWindowTitle("Edit Data Dimensions and Units")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.layout = QVBoxLayout(self)
        
        # Create tabs for organization
        self.tabs = QTabWidget()
        self.dimensions_tab = QWidget()
        self.values_tab = QWidget()
        
        self.tabs.addTab(self.dimensions_tab, "Dimensions")
        self.tabs.addTab(self.values_tab, "Data Values")
        
        self.setup_dimensions_tab()
        self.setup_values_tab()
        
        self.layout.addWidget(self.tabs)
        
        # Add OK button
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)
        
    def setup_dimensions_tab(self):
        """Setup the dimensions tab"""
        layout = QVBoxLayout(self.dimensions_tab)
        
        # Time dimension is shared - it should only be edited once
        time_group = QGroupBox("Time Dimension (shared)")
        time_layout = QFormLayout(time_group)
        
        # Get the current time dimension info
        activity_dims = self.processor.get_dimension_info("activity")
        stim_dims = self.processor.get_dimension_info("stimulus")
        
        time_name = "time"
        time_unit = "frames"
        
        if activity_dims and "dims" in activity_dims and "units" in activity_dims and len(activity_dims["dims"]) > 0:
            time_name = activity_dims["dims"][0]
            time_unit = activity_dims["units"][0]
        
        self.time_name_edit = QLineEdit(time_name)
        self.time_unit_edit = QLineEdit(time_unit)
        
        time_layout.addRow("Name:", self.time_name_edit)
        time_layout.addRow("Unit:", self.time_unit_edit)
        
        layout.addWidget(time_group)
        
        # Activity additional dimensions (should be none since it's 1D, but handle just in case)
        activity_dims_group = None
        if self.processor.activity is not None and len(self.processor.activity.shape) > 1:
            activity_dims_group = QGroupBox("Activity Additional Dimensions")
            activity_dims_layout = QFormLayout(activity_dims_group)
            
            self.activity_dim_editors = []
            
            for i in range(1, len(self.processor.activity.shape)):
                name = activity_dims["dims"][i] if activity_dims and "dims" in activity_dims and i < len(activity_dims["dims"]) else f"dim_{i}"
                unit = activity_dims["units"][i] if activity_dims and "units" in activity_dims and i < len(activity_dims["units"]) else "units"
                
                name_edit = QLineEdit(name)
                unit_edit = QLineEdit(unit)
                
                activity_dims_layout.addRow(f"Dimension {i} Name:", name_edit)
                activity_dims_layout.addRow(f"Dimension {i} Unit:", unit_edit)
                
                self.activity_dim_editors.append((name_edit, unit_edit))
            
            layout.addWidget(activity_dims_group)
        
        # Stimulus additional dimensions
        stimulus_dims_group = None
        if self.processor.stimulus is not None and len(self.processor.stimulus.shape) > 1:
            stimulus_dims_group = QGroupBox("Stimulus Additional Dimensions")
            stimulus_dims_layout = QFormLayout(stimulus_dims_group)
            
            self.stimulus_dim_editors = []
            
            for i in range(1, len(self.processor.stimulus.shape)):
                name = stim_dims["dims"][i] if stim_dims and "dims" in stim_dims and i < len(stim_dims["dims"]) else f"dim_{i}"
                unit = stim_dims["units"][i] if stim_dims and "units" in stim_dims and i < len(stim_dims["units"]) else "units"
                
                name_edit = QLineEdit(name)
                unit_edit = QLineEdit(unit)
                
                stimulus_dims_layout.addRow(f"Dimension {i} (size: {self.processor.stimulus.shape[i]}) Name:", name_edit)
                stimulus_dims_layout.addRow(f"Dimension {i} Unit:", unit_edit)
                
                self.stimulus_dim_editors.append((name_edit, unit_edit))
            
            layout.addWidget(stimulus_dims_group)
        
        if not activity_dims_group and not stimulus_dims_group:
            layout.addWidget(QLabel("No additional dimensions to edit"))
            
        layout.addStretch(1)
        
    def setup_values_tab(self):
        """Setup the values tab"""
        layout = QVBoxLayout(self.values_tab)
        
        # Get current value info
        activity_value = self.processor.get_value_info("activity")
        stimulus_value = self.processor.get_value_info("stimulus")
        
        # Activity value info
        activity_group = QGroupBox("Activity Data Value")
        activity_layout = QFormLayout(activity_group)
        
        self.activity_name_edit = QLineEdit(activity_value.get("name", "Firing rate") if activity_value else "Firing rate")
        self.activity_unit_edit = QLineEdit(activity_value.get("unit", "Hz") if activity_value else "Hz")
        
        activity_layout.addRow("Name:", self.activity_name_edit)
        activity_layout.addRow("Unit:", self.activity_unit_edit)
        
        layout.addWidget(activity_group)
        
        # Stimulus value info
        stimulus_group = QGroupBox("Stimulus Data Value")
        stimulus_layout = QFormLayout(stimulus_group)
        
        self.stimulus_name_edit = QLineEdit(stimulus_value.get("name", "Stimulus") if stimulus_value else "Stimulus")
        self.stimulus_unit_edit = QLineEdit(stimulus_value.get("unit", "a.u.") if stimulus_value else "a.u.")
        
        stimulus_layout.addRow("Name:", self.stimulus_name_edit)
        stimulus_layout.addRow("Unit:", self.stimulus_unit_edit)
        
        layout.addWidget(stimulus_group)
        layout.addStretch(1)
        
    def accept(self):
        """Save all changes when OK is clicked"""
        # Save time dimension (shared)
        time_name = self.time_name_edit.text()
        time_unit = self.time_unit_edit.text()
        
        # Update activity dimensions
        activity_dims = self.processor.get_dimension_info("activity") or {}
        activity_dim_names = activity_dims.get("dims", []).copy() if "dims" in activity_dims else []
        activity_dim_units = activity_dims.get("units", []).copy() if "units" in activity_dims else []
        
        # Ensure lists are long enough
        while len(activity_dim_names) < 1:
            activity_dim_names.append("time")
        while len(activity_dim_units) < 1:
            activity_dim_units.append("frames")
            
        # Update time dimension
        activity_dim_names[0] = time_name
        activity_dim_units[0] = time_unit
        
        # Update additional activity dimensions if any
        if hasattr(self, "activity_dim_editors"):
            for i, (name_edit, unit_edit) in enumerate(self.activity_dim_editors):
                dim_idx = i + 1  # +1 because time is at index 0
                
                # Ensure lists are long enough
                while len(activity_dim_names) <= dim_idx:
                    activity_dim_names.append(f"dim_{len(activity_dim_names)}")
                while len(activity_dim_units) <= dim_idx:
                    activity_dim_units.append("units")
                    
                activity_dim_names[dim_idx] = name_edit.text()
                activity_dim_units[dim_idx] = unit_edit.text()
        
        # Update stimulus dimensions
        stimulus_dims = self.processor.get_dimension_info("stimulus") or {}
        stimulus_dim_names = stimulus_dims.get("dims", []).copy() if "dims" in stimulus_dims else []
        stimulus_dim_units = stimulus_dims.get("units", []).copy() if "units" in stimulus_dims else []
        
        # Ensure lists are long enough
        while len(stimulus_dim_names) < 1:
            stimulus_dim_names.append("time")
        while len(stimulus_dim_units) < 1:
            stimulus_dim_units.append("frames")
            
        # Update time dimension (shared)
        stimulus_dim_names[0] = time_name
        stimulus_dim_units[0] = time_unit
        
        # Update additional stimulus dimensions
        if hasattr(self, "stimulus_dim_editors"):
            for i, (name_edit, unit_edit) in enumerate(self.stimulus_dim_editors):
                dim_idx = i + 1  # +1 because time is at index 0
                
                # Ensure lists are long enough
                while len(stimulus_dim_names) <= dim_idx:
                    stimulus_dim_names.append(f"dim_{len(stimulus_dim_names)}")
                while len(stimulus_dim_units) <= dim_idx:
                    stimulus_dim_units.append("units")
                    
                stimulus_dim_names[dim_idx] = name_edit.text()
                stimulus_dim_units[dim_idx] = unit_edit.text()
        
        # Save all changes to processor
        self.processor.set_dimension_info("activity", activity_dim_names, activity_dim_units)
        self.processor.set_dimension_info("stimulus", stimulus_dim_names, stimulus_dim_units)
        
        # Save data value info
        self.processor.set_value_info("activity", self.activity_name_edit.text(), self.activity_unit_edit.text())
        self.processor.set_value_info("stimulus", self.stimulus_name_edit.text(), self.stimulus_unit_edit.text())
        
        super().accept()