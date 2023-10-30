from enum import Enum, IntEnum
from struct import Struct


def get_enum_member(en, v, allow_none=False):
    if allow_none:
        if v is None:
            return None

    if isinstance(v, en):
        return v

    try:
        return en(v)
    except ValueError:
        pass

    if isinstance(v, str):
        if v.isdigit():
            try:
                return en(int(v))
            except ValueError:
                pass

        try:
            return en[v]
        except KeyError:
            pass

    raise ValueError(f"{en.__name__} '{v}' is not defined")


class _ConverterEnum(int, Enum):
    def __new__(cls, code: int, converter: Struct):
        obj = super().__new__(cls, code)
        obj._value_ = code
        obj.converter = converter
        return obj


class RepresentationCode(_ConverterEnum):
    """Class serves as a lookup for RP66 V1 representation codes.

    Some representation codes can not be directly converted using Struct.
    Those have the value None. They are still included here, so that it also
    serves as a full list of representation codes included in the RP66 V1.

    Compiled using dlispy and RP66 V1 specification.

    .. _dlispy:
        https://github.com/Teradata/dlispy/blob/master/dlispy/RCReader.py

    .. _RP66V1 Appendix B:
        http://w3.energistics.org/rp66/v1/rp66v1_appb.html

    """
    FSHORT = 1, Struct('>h')
    FSINGL = 2, Struct('>f')
    FSING1 = 3, Struct('>ff')
    FSING2 = 4, Struct('>fff')
    ISINGL = 5, Struct('>i')
    VSINGL = 6, Struct('>i')
    FDOUBL = 7, Struct('>d')
    FDOUB1 = 8, Struct('>dd')
    FDOUB2 = 9, Struct('>ddd')
    CSINGL = 10, Struct('>ff')
    CDOUBL = 11, Struct('>dd')
    SSHORT = 12, Struct('>b')
    SNORM = 13, Struct('>h')
    SLONG = 14, Struct('>i')
    USHORT = 15, Struct('>B')
    UNORM = 16, Struct('>H')
    ULONG = 17, Struct('>I')
    UVARI = 18, 'UVARI'
    IDENT = 19, 'IDENT'
    ASCII = 20, 'ASCII'
    DTIME = 21, Struct('>BBBBBBH')
    ORIGIN = 22, 'ORIGIN'
    OBNAME = 23, 'OBNAME'
    OBJREF = 24, 'OBJREF'
    ATTREF = 25, 'ATTREF'
    STATUS = 26, Struct('>B')

    @classmethod
    def get_member(cls, c, allow_none=False):
        return get_enum_member(cls, c, allow_none=allow_none)

UNITS = (

    "A",
    "K",
    "cd",
    "dAPI",
    "dB",
    "gAPI",
    "kg",
    "m",
    "mol",
    "nAPI",
    "rad",
    "s",
    "sr",
    "Btu",
    "C",
    "D",
    "GPa",
    "Gal",
    "Hz",
    "J",
    "L",
    "MHz",
    "MPa",
    "MeV",
    "Mg",
    "Mpsi",
    "N",
    "Oe",
    "P",
    "Pa",
    "S",
    "T",
    "V",
    "W",
    "Wb",
    "a",
    "acre",
    "atm",
    "b",
    "bar",
    "bbl",
    "c",
    "cP",
    "cal",
    "cm",
    "cu",
    "d",
    "daN",
    "deg",
    "degC",
    "degF,"
    "dm",
    "eV",
    "fC",
    "ft",
    "g",
    "gal",
    "h",
    "in",
    "kHz",
    "kPa",
    "kV",
    "keV",
    "kgf",
    "km",
    "lbf",
    "lbm",
    "mA",
    "mC",
    "mD",
    "mGal",
    "mL",
    "mS",
    "mT",
    "mV",
    "mW",
    "mg",
    "min",
    "mm",
    "mohm",
    "ms",
    "nC",
    "nW",
    "ns",
    "ohm",
    "pC",
    "pPa",
    "ppdk",
    "ppk",
    "ppm",
    "psi",
    "pu",
    "t",
    "ton",
    "uA",
    "uC",
    "uPa",
    "uV",
    "um",
    "uohm",
    "upsi",
    "us"
)

class LogicalRecordType(IntEnum):
    FHLR = 0
    OLR = 1
    AXIS = 2
    CHANNL = 3
    FRAME = 4
    STATIC = 5
    SCRIPT = 6
    UPDATE = 7
    UDI = 8
    LNAME = 9
    SPEC = 10
    DICT = 11

    @classmethod
    def get_member(cls, t, allow_none=False):
        return get_enum_member(cls, t, allow_none=allow_none)
