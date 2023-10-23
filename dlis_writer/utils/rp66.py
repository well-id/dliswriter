"""This module serves as a dictionary and can be extended in the future by providing
default attribute values for each set type

"""

from dlis_writer.utils.enums import RepresentationCode


class RP66:
    """Serves as a lookup dictionary of Set Types and their attributes' count and data types"""

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