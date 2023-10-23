"""This module serves as a dictionary and can be extended in the future by providing
default attribute values for each set type

"""

from dlis_writer.utils.enums import RepresentationCode


class RP66:
    """Serves as a lookup dictionary of Set Types and their attributes' count and data types"""

    WELL_REFERENCE = {
        
        'permanent_datum': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'vertical_zero': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'permanent_datum_elevation': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'above_permanent_datum': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'magnetic_declination': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'coordinate_1_name': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'coordinate_1_value': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'coordinate_2_name': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'coordinate_2_value': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'coordinate_3_name': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'coordinate_3_value': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        }
    }

    AXIS = {
        
        'axis_id': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
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
            'representation_code': RepresentationCode.ASCII
        },

        'quantity': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'quantity_modifier': {
            'count': None,
            'representation_code': RepresentationCode.ASCII
        },

        'altered_form': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'entity': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'entity_modifier': {
            'count': None,
            'representation_code': RepresentationCode.ASCII
        },

        'entity_number': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'entity_part': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'entity_part_number': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'generic_source': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'source_part': {
            'count': None,
            'representation_code': RepresentationCode.ASCII
        },

        'source_part_number': {
            'count': None,
            'representation_code': RepresentationCode.ASCII
        },

        'conditions': {
            'count': None,
            'representation_code': RepresentationCode.ASCII
        },

        'standard_symbol': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'private_symbol': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        }
    }

    CHANNEL = {
        
        'long_name': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'properties': {
            'count': None,
            'representation_code': RepresentationCode.IDENT
        },

        'representation_code': {
            'count': 1,
            'representation_code': RepresentationCode.USHORT
        },

        'units': {
            'count': 1,
            'representation_code': RepresentationCode.UNITS
        },

        'dimension': {
            'count': None,
            'representation_code': RepresentationCode.UVARI
        },

        'axis': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'element_limit': {
            'count': None,
            'representation_code': RepresentationCode.UVARI
        },

        'source': {
            'count': 1,
            'representation_code': RepresentationCode.OBJREF
        },
        'minimum_value': {
            'count': None,
            'representation_code': RepresentationCode.FDOUBL
        },
        'maximum_value': {
            'count': None,
            'representation_code': RepresentationCode.FDOUBL
        }
    }

    FRAME = {

        'description': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'channels': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'index_type': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
        },

        'direction': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
        },

        'spacing': {
            'count': 1,
            'representation_code': None
        },

        'encrypted': {
            'count': 1,
            'representation_code': RepresentationCode.USHORT
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
            'representation_code': RepresentationCode.OBNAME
        },

        'well_reference_point': {
            'count': 1,
            'representation_code': RepresentationCode.OBNAME
        },

        'value': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
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
            'representation_code': RepresentationCode.ASCII
        },

        'domain': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
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
            'representation_code': RepresentationCode.ASCII
        },

        'dimension': {
            'count': None,
            'representation_code': RepresentationCode.UVARI
        },

        'axis': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'zones': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'values': {
            'count': None,
            'representation_code': None
        }
    }

    EQUIPMENT = {

        'trademark_name': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'status': {
            'count': 1,
            'representation_code': RepresentationCode.STATUS
        },

        '_type': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
        },

        'serial_number': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
        },

        'location': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
        },

        'height': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'length': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'minimum_diameter': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'maximum_diameter': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'volume': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'weight': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'hole_size': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'pressure': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'temperature': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'vertical_depth': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'radial_drift': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        },

        'angular_drift': {
            'count': 1,
            'representation_code': RepresentationCode.FDOUBL
        }
    }

    TOOL = {

        'description': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'trademark_name': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'generic_name': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'parts': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'status': {
            'count': 1,
            'representation_code': RepresentationCode.STATUS
        },

        'channels': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'parameters': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        }
    }

    COMPUTATION = {

        'long_name': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'properties': {
            'count': None,
            'representation_code': RepresentationCode.IDENT
        },

        'dimension': {
            'count': None,
            'representation_code': RepresentationCode.UVARI
        },

        'axis': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'zones': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
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
            'representation_code': RepresentationCode.ASCII
        },

        'trademark_name' : {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'version' : {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'properties' : {
            'count': None,
            'representation_code': RepresentationCode.IDENT
        },

        'status' : {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
        },

        'input_channels' : {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'output_channels' : {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'input_computations' : {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'output_computations' : {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'parameters' : {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'comments' : {
            'count': None,
            'representation_code': RepresentationCode.ASCII
        }
    }

    CALIBRATION_MEASUREMENT = {
        
        'phase': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
        },

        'measurement_source': {
            'count': 1,
            'representation_code': RepresentationCode.OBJREF
        },

        '_type': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
        },

        'dimension': {
            'count': None,
            'representation_code': RepresentationCode.UVARI
        },

        'axis': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
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
            'representation_code': RepresentationCode.IDENT
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
            'representation_code': RepresentationCode.OBNAME
        },

        'uncalibrated_channels': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'coefficients': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'measurements': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'parameters': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'method': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
        }
    }

    GROUP = {

        'description': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        },

        'object_type': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
        },

        'object_list': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'group_list': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        }
    }

    SPLICE = {

        'output_channel': {
            'count': 1,
            'representation_code': RepresentationCode.OBNAME
        },

        'input_channels': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        },

        'zones': {
            'count': None,
            'representation_code': RepresentationCode.OBNAME
        }
    }

    NO_FORMAT = {

        'consumer_name': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
        },

        'description': {
            'count': 1,
            'representation_code': RepresentationCode.ASCII
        }
    }

    MESSAGE = {

        '_type': {
            'count': 1,
            'representation_code': RepresentationCode.IDENT
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
            'representation_code': RepresentationCode.ASCII
        } 
    }

    COMMENT = {
        
        'text': {
            'count': None,
            'representation_code': RepresentationCode.ASCII
        }
    }