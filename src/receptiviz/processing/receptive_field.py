import numpy as np
import os
from ..utils.data_utils import load_numpy_array

# Constants for validation
MIN_TIME_POINTS = 10
MIN_SPATIAL_DIM = 5

class ReceptiveFieldProcessor:
    """
    Handles loading, validating, and processing data for receptive field analysis.
    """
    
    def __init__(self):
        self.reset_state()
        
    def reset_state(self):
        """Reset all state variables"""
        self.activity = None
        self.stimulus = None
        self.result = None
        self.errors = []
        
        # Dimension information
        self.activity_dims = {}
        self.stimulus_dims = {}
        self.stimulus_ndim = 0
        
        # Value information
        self.activity_value_info = {"name": "Firing rate", "unit": "Hz"}
        self.stimulus_value_info = {"name": "Stimulus", "unit": "a.u."}
        
        return self
    
    def validate_file(self, file_path, file_type):
        """Validate a single file"""
        errors = []
        data = None
        
        # Basic file validation
        if not os.path.exists(file_path):
            errors.append(f"File not found: {file_path}")
            return False, errors, None
            
        if not os.path.isfile(file_path):
            errors.append(f"Not a file: {file_path}")
            return False, errors, None
            
        if not file_path.lower().endswith('.npy'):
            errors.append(f"Not a NumPy file (must end with .npy)")
            return False, errors, None
            
        # Try to load the file
        try:
            data = load_numpy_array(file_path)
            
            if data is None:
                errors.append(f"Failed to load {file_type} array")
                return False, errors, None
                
            # Check data type
            if not isinstance(data, np.ndarray):
                errors.append(f"File does not contain a NumPy array")
                return False, errors, None
                
            # Check for NaN values
            if np.isnan(data).any():
                errors.append(f"Array contains NaN values")
                return False, errors, None
                
            # Validate shape based on file type
            if file_type == "activity":
                # Activity must be 1D
                if len(data.shape) != 1:
                    errors.append(f"Activity array must be 1D, got {len(data.shape)}D with shape {data.shape}")
                    return False, errors, None
                    
                if data.shape[0] < MIN_TIME_POINTS:
                    errors.append(f"Activity array too small (length {data.shape[0]}), must have at least {MIN_TIME_POINTS} time points")
                    return False, errors, None
                    
                # Set up default dimension names for activity
                self.activity_dims = {
                    "dims": ["time"],
                    "units": ["frames"]
                }
                
                # Check compatibility with existing stimulus
                if self.stimulus is not None and data.shape[0] != self.stimulus.shape[0]:
                    errors.append(f"Activity length ({data.shape[0]}) must match stimulus time dimension ({self.stimulus.shape[0]})")
                    return False, errors, None
                    
            elif file_type == "stimulus":
                # First dimension must have enough time points
                if data.shape[0] < MIN_TIME_POINTS:
                    errors.append(f"Stimulus time dimension too small (only {data.shape[0]} time points), must have at least {MIN_TIME_POINTS} time points")
                    return False, errors, None
                
                # Store the number of dimensions in the stimulus array
                self.stimulus_ndim = len(data.shape)
                
                # Set up default dimension names for stimulus
                dim_names = ["time"] 
                dim_units = ["frames"]
                
                # Add default names for additional dimensions
                for i in range(1, self.stimulus_ndim):
                    if i == 1:
                        dim_names.append("height")
                        dim_units.append("pixels")
                    elif i == 2:
                        dim_names.append("width")
                        dim_units.append("pixels")
                    else:
                        dim_names.append(f"dim_{i}")
                        dim_units.append("units")
                
                self.stimulus_dims = {
                    "dims": dim_names,
                    "units": dim_units,
                    "shape": data.shape
                }
                
                # Check compatibility with existing activity
                if self.activity is not None and data.shape[0] != self.activity.shape[0]:
                    errors.append(f"Stimulus time dimension ({data.shape[0]}) must match activity length ({self.activity.shape[0]})")
                    return False, errors, None
            
            return True, [], data
            
        except Exception as e:
            errors.append(f"Error loading file: {str(e)}")
            return False, errors, None
    
    def set_activity(self, activity):
        """Set activity data"""
        self.activity = activity
        return self
        
    def set_stimulus(self, stimulus):
        """Set stimulus data"""
        self.stimulus = stimulus
        self.stimulus_ndim = len(stimulus.shape)
        return self
    
    def set_dimension_info(self, array_type, dim_names=None, dim_units=None):
        """Set dimension names and units for an array"""
        if array_type == "activity":
            if not self.activity_dims:
                self.activity_dims = {}
            if dim_names:
                self.activity_dims["dims"] = dim_names
            if dim_units:
                self.activity_dims["units"] = dim_units
        elif array_type == "stimulus":
            if not self.stimulus_dims:
                self.stimulus_dims = {}
            if dim_names:
                self.stimulus_dims["dims"] = dim_names
            if dim_units:
                self.stimulus_dims["units"] = dim_units
        return self
    
    def get_dimension_info(self, array_type):
        """Get dimension information for an array"""
        if array_type == "activity":
            return self.activity_dims
        elif array_type == "stimulus":
            return self.stimulus_dims
        return None
    
    def set_value_info(self, array_type, value_name, value_unit):
        """Set the name and unit for the data values"""
        if array_type == "activity":
            if not hasattr(self, "activity_value_info"):
                self.activity_value_info = {}
            self.activity_value_info["name"] = value_name
            self.activity_value_info["unit"] = value_unit
        elif array_type == "stimulus":
            if not hasattr(self, "stimulus_value_info"):
                self.stimulus_value_info = {}
            self.stimulus_value_info["name"] = value_name
            self.stimulus_value_info["unit"] = value_unit
        return self
    
    def get_value_info(self, array_type):
        """Get the name and unit for the data values"""
        if array_type == "activity":
            if not hasattr(self, "activity_value_info"):
                self.activity_value_info = {"name": "Firing rate", "unit": "Hz"}
            return self.activity_value_info
        elif array_type == "stimulus":
            if not hasattr(self, "stimulus_value_info"):
                self.stimulus_value_info = {"name": "Stimulus", "unit": "a.u."}
            return self.stimulus_value_info
        return None
    
    def validate_compatibility(self):
        """Validate that activity and stimulus arrays are compatible"""
        self.errors = []
        
        if self.activity is None or self.stimulus is None:
            self.errors.append("Both activity and stimulus data must be set")
            return self
            
        # Check compatibility between arrays - time dimension must match
        if self.activity.shape[0] != self.stimulus.shape[0]:
            self.errors.append(f"Activity length ({self.activity.shape[0]}) must match stimulus time dimension ({self.stimulus.shape[0]})")
            
        return self
        
    def process(self):
        """Process the receptive field analysis"""
        if self.errors:
            return self
            
        try:
            # Reshape stimulus for correlation regardless of dimensionality
            # First dimension is time, all others get flattened
            stim_reshaped = self.stimulus.reshape(self.stimulus.shape[0], -1)
            
            # Calculate correlation between activity and each stimulus element
            corr_matrix = np.corrcoef(self.activity, stim_reshaped.T)[0, 1:]
            
            # Reshape correlation back to original spatial dimensions
            spatial_dims = self.stimulus.shape[1:]
            corr_map = corr_matrix.reshape(spatial_dims)
            
            self.result = {
                'correlation_map': corr_map,
                'activity_stats': {
                    'mean': np.mean(self.activity),
                    'std': np.std(self.activity)
                },
                'stimulus_stats': {
                    'mean': np.mean(self.stimulus),
                    'std': np.std(self.stimulus)
                },
                'stimulus_dims': self.stimulus_dims,
                'activity_dims': self.activity_dims,
                'activity_value_info': self.activity_value_info,
                'stimulus_value_info': self.stimulus_value_info
            }
            
        except Exception as e:
            self.errors.append(f"Processing error: {str(e)}")
            
        return self
        
    def get_result(self):
        """Get the processed result"""
        return self.result
        
    def get_errors(self):
        """Get any errors that occurred during processing"""
        return self.errors