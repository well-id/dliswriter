"""This module serves as a dictionary and can be extended in the future by providing
default attribute values for each set type

"""


class RP66:
    """Serves as a lookup dictionary of Set Types and their attributes' count and data types"""

    ORIGIN = {
        
        'file_id': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'file_set_name': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'file_set_number': {
            'count': 1,
            'representation_code': 'UVARI'
        },

        'file_number': {
            'count': 1,
            'representation_code': 'UVARI'
        },

        'file_type': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'product': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'version': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'programs': {
            'count': None,
            'representation_code': 'ASCII'
        },

        'creation_time': {
            'count': 1,
            'representation_code': 'DTIME'
        },

        'order_number': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'descent_number': {
            'count': 1,
            'representation_code': 'UNORM'
        },

        'run_number': {
            'count': 1,
            'representation_code': 'UNORM'
        },

        'well_id': {
            'count': 1,
            'representation_code': 'UNORM'
        },

        'well_name': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'field_name': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'producer_code': {
            'count': 1,
            'representation_code': 'UNORM'
        },

        'producer_name': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'company': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'name_space_name': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'name_space_version': {
            'count': 1,
            'representation_code': 'UVARI'
        }
    }

    WELL_REFERENCE = {
        
        'permanent_datum': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'vertical_zero': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'permanent_datum_elevation': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'above_permanent_datum': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'magnetic_declination': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'coordinate_1_name': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'coordinate_1_value': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'coordinate_2_name': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'coordinate_2_value': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'coordinate_3_name': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'coordinate_3_value': {
            'count': 1,
            'representation_code': 'FDOUBL'
        }
    }

    AXIS = {
        
        'axis_id': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'coordinates': {
            'count': None,
            'representation_code': None
        },

        'spacing': {
            'count': 1,
            'representation_code': None
        }
    }

    LONG_NAME = {
        
        'general_modifier': {
            'count': None,
            'representation_code': 'ASCII'
        },

        'quantity': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'quantity_modifier': {
            'count': None,
            'representation_code': 'ASCII'
        },

        'altered_form': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'entity': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'entity_modifier': {
            'count': None,
            'representation_code': 'ASCII'
        },

        'entity_number': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'entity_part': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'entity_part_number': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'generic_source': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'source_part': {
            'count': None,
            'representation_code': 'ASCII'
        },

        'source_part_number': {
            'count': None,
            'representation_code': 'ASCII'
        },

        'conditions': {
            'count': None,
            'representation_code': 'ASCII'
        },

        'standard_symbol': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'private_symbol': {
            'count': 1,
            'representation_code': 'ASCII'
        }
    }

    CHANNEL = {
        
        'long_name': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'properties': {
            'count': None,
            'representation_code': 'IDENT'
        },

        'representation_code': {
            'count': 1,
            'representation_code': 'USHORT'
        },

        'units': {
            'count': 1,
            'representation_code': 'UNITS'
        },

        'dimension': {
            'count': None,
            'representation_code': 'UVARI'
        },

        'axis': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'element_limit': {
            'count': None,
            'representation_code': 'UVARI'
        },

        'source': {
            'count': 1,
            'representation_code': 'OBJREF'
        }
    }

    FRAME = {

        'description': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'channels': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'index_type': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'direction': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'spacing': {
            'count': 1,
            'representation_code': None
        },

        'encrypted': {
            'count': 1,
            'representation_code': 'USHORT'
        },

        'index_min': {
            'count': 1,
            'representation_code': None
        },

        'index_max': {
            'count': 1,
            'representation_code': None
        }
    }

    PATH = {
        
        'frame_type': {
            'count': 1,
            'representation_code': 'OBNAME'
        },

        'well_reference_point': {
            'count': 1,
            'representation_code': 'OBNAME'
        },

        'value': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'borehole_depth': {
            'count': 1,
            'representation_code': None
        },

        'vertical_depth': {
            'count': 1,
            'representation_code': None
        },

        'radial_drift': {
            'count': 1,
            'representation_code': None
        },

        'angular_drift': {
            'count': 1,
            'representation_code': None
        },

        'time': {
            'count': 1,
            'representation_code': None
        },

        'depth_offset': {
            'count': 1,
            'representation_code': None
        },

        'measure_point_offset': {
            'count': 1,
            'representation_code': None
        },

        'tool_zero_offset': {
            'count': 1,
            'representation_code': None
        }
    }

    ZONE = {
        
        'description': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'domain': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'maximum': {
            'count': 1,
            'representation_code': None
        },

        'minimum': {
            'count': 1,
            'representation_code': None
        }
    }

    PARAMETER = {

        'long_name': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'dimension': {
            'count': None,
            'representation_code': 'UVARI'
        },

        'axis': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'zones': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'values': {
            'count': None,
            'representation_code': None
        }
    }

    EQUIPMENT = {

        'trademark_name': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'status': {
            'count': 1,
            'representation_code': 'STATUS'
        },

        '_type': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'serial_number': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'location': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'height': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'length': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'minimum_diameter': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'maximum_diameter': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'volume': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'weight': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'hole_size': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'pressure': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'temperature': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'vertical_depth': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'radial_drift': {
            'count': 1,
            'representation_code': 'FDOUBL'
        },

        'angular_drift': {
            'count': 1,
            'representation_code': 'FDOUBL'
        }
    }

    TOOL = {

        'description': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'trademark_name': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'generic_name': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'parts': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'status': {
            'count': 1,
            'representation_code': 'STATUS'
        },

        'channels': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'parameters': {
            'count': None,
            'representation_code': 'OBNAME'
        }
    }

    COMPUTATION = {

        'long_name': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'properties': {
            'count': None,
            'representation_code': 'IDENT'
        },

        'dimension': {
            'count': None,
            'representation_code': 'UVARI'
        },

        'axis': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'zones': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'values': {
            'count': None,
            'representation_code': None
        },

        'source': {
            'count': None,
            'representation_code': None
        }
    }

    PROCESS = {
        
        'description' : {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'trademark_name' : {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'version' : {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'properties' : {
            'count': None,
            'representation_code': 'IDENT'
        },

        'status' : {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'input_channels' : {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'output_channels' : {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'input_computations' : {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'output_computations' : {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'parameters' : {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'comments' : {
            'count': None,
            'representation_code': 'ASCII'
        }
    }

    CALIBRATION_MEASUREMENT = {
        
        'phase': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'measurement_source': {
            'count': 1,
            'representation_code': 'OBJREF'
        },

        '_type': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'dimension': {
            'count': None,
            'representation_code': 'UVARI'
        },

        'axis': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'measurement': {
            'count': None,
            'representation_code': None
        },

        'sample_count': {
            'count': 1,
            'representation_code': None
        },

        'maximum_deviation': {
            'count': 1,
            'representation_code': None
        },

        'standard_deviation': {
            'count': 1,
            'representation_code': None
        },

        'begin_time': {
            'count': 1,
            'representation_code': None
        },

        'duration': {
            'count': 1,
            'representation_code': None
        },

        'reference': {
            'count': None,
            'representation_code': None
        },

        'standard': {
            'count': None,
            'representation_code': None
        },

        'plus_tolerance': {
            'count': None,
            'representation_code': None
        },

        'minus_tolerance': {
            'count': None,
            'representation_code': None
        }
    }

    CALIBRATION_COEFFICIENT = {
        
        'label': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'coefficients': {
            'count': None,
            'representation_code': None
        },

        'references': {
            'count': None,
            'representation_code': None
        },

        'plus_tolerances': {
            'count': None,
            'representation_code': None
        },

        'minus_tolerances': {
            'count': None,
            'representation_code': None
        }
    }

    CALIBRATION = {
        
        'calibrated_channels': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'uncalibrated_channels': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'coefficients': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'measurements': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'parameters': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'method': {
            'count': 1,
            'representation_code': 'IDENT'
        }
    }

    GROUP = {

        'description': {
            'count': 1,
            'representation_code': 'ASCII'
        },

        'object_type': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'object_list': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'group_list': {
            'count': None,
            'representation_code': 'OBNAME'
        }
    }

    SPLICE = {

        'output_channels': {
            'count': 1,
            'representation_code': 'OBNAME'
        },

        'input_channels': {
            'count': None,
            'representation_code': 'OBNAME'
        },

        'zones': {
            'count': None,
            'representation_code': 'OBNAME'
        }
    }

    NO_FORMAT = {

        'consumer_name': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'description': {
            'count': 1,
            'representation_code': 'ASCII'
        }
    }

    MESSAGE = {

        '_type': {
            'count': 1,
            'representation_code': 'IDENT'
        },

        'time': {
            'count': 1,
            'representation_code': None
        },

        'borehole_drift': {
            'count': 1,
            'representation_code': None
        },

        'vertical_depth': {
            'count': 1,
            'representation_code': None
        },

        'radial_drift': {
            'count': 1,
            'representation_code': None
        },

        'angular_drift': {
            'count': 1,
            'representation_code': None
        },

        'text': {
            'count': None,
            'representation_code': 'ASCII'
        } 
    }

    COMMENT = {
        
        'text': {
            'count': None,
            'representation_code': 'ASCII'
        }
    }