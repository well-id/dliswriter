"""This module serves as a dictionary and can be extended in the future by providing
default attribute values for each set type

"""

from dlis_writer.utils.enums import RepresentationCode


class RP66:
    """Serves as a lookup dictionary of Set Types and their attributes' count and data types"""

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