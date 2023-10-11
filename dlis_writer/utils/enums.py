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


class Units(Enum):

    A = 'ampere'
    K = 'Kelvin'
    cd = 'candela'
    dAPI = 'API gravity'
    dB = 'decibel'
    gAPI = 'API gamma ray'
    kg = 'kilogram'
    m = 'meter'
    mol = 'mole'
    nAPI = 'API neutron'
    rad = 'radian'
    s = 'second'
    sr = 'steradian'
    Btu = 'British thermal unit (international)'
    C = 'coulomb'
    D = 'darcy'
    GPa = 'gigapascal'
    Gal = 'Gal'
    Hz = 'hertz'
    J = 'joule'
    L = 'liter'
    MHz = 'megahertz'
    MPa = 'megapascal'
    MeV = 'megaelectronvolt'
    Mg = 'thousand kilograms'
    Mpsi = 'million pounds per square inch'
    N = 'Newton'
    Oe = 'oersted'
    P = 'poise'
    Pa = 'pascal'
    S = 'siemens'
    T = 'tesla'
    V = 'volt'
    W = 'watt'
    Wb = 'weber'
    a = 'annum (sidereal year)'
    acre = 'acre'
    atm = 'standard atmosphere'
    b = 'barn'
    bar = 'bar'
    bbl = 'barrel'
    c = 'revolution (cycle)'
    cP = 'centipoise'
    cal = 'calorie (international)'
    cm = 'centimeter'
    cu = 'capture unit'
    d = 'day'
    daN = 'decanewton'
    deg = 'degree (angle)'
    degC = 'degree celsius'
    degF = 'degree fahrenheit'
    dm = 'decimeter'
    eV = 'electron volt'
    fC = 'femtocoulomb'
    ft = 'foot'
    g = 'gram'
    gal = 'gallon'
    h = 'hour'
    in_ = 'inch'
    kHz = 'kilohertz'
    kPa = 'kilopascal'
    kV = 'kilovolt'
    keV = 'kiloelectronvolt'
    kgf = 'kilogram force'
    km = 'kilometer'
    lbf = 'pound force'
    lbm = 'pound mass (avoirdupois)'
    mA = 'milliampere'
    mC = 'millicoulomb'
    mD = 'millidarcy'
    mGal = 'milligal'
    mL = 'milliliter'
    mS = 'millisiemens'
    mT = 'millitesla'
    mV = 'millivolt'
    mW = 'milliwatt'
    mg = 'milligram'
    min_ = 'minute'
    mm = 'millimeter'
    mohm = 'milliohm'
    ms = 'millisecond'
    nC = 'nanocoulomb'
    nW = 'nanowatt'
    ns = 'nanosecond'
    ohm = 'ohm'
    pC = 'picocoulomb'
    pPa = 'picopascal'
    ppdk = 'part per ten thousand'
    ppk = 'part per thousand'
    ppm = 'part per million'
    psi = 'pound per square inch'
    pu = 'porosity unit'
    t = 'metric ton'
    ton = 'U.S. short ton'
    uA = 'microampere'
    uC = 'microcoulomb'
    uPa = 'micropascal'
    uV = 'microvolt'
    um = 'micrometer'
    uohm = 'microohm'
    upsi = 'micropound per square inch'
    us = 'microsecond'

    @classmethod
    def get_member(cls, u, allow_none=False):
        return get_enum_member(cls, u, allow_none=allow_none)


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
    UNITS = 27, 'UNITS'

    @classmethod
    def get_member(cls, c, allow_none=False):
        return get_enum_member(cls, c, allow_none=allow_none)


# TODO: verify
numpy_dtype_converter = {
    'int_': RepresentationCode.SLONG,
    'int8': RepresentationCode.SSHORT,
    'int16': RepresentationCode.SSHORT,
    'int32': RepresentationCode.SNORM,
    'int64': RepresentationCode.SLONG,
    'uint8': RepresentationCode.USHORT,
    'uint16': RepresentationCode.USHORT,
    'uint32': RepresentationCode.UNORM,
    'uint64': RepresentationCode.ULONG,
    'float_': RepresentationCode.FDOUBL,
    'float16': RepresentationCode.FSINGL,
    'float32': RepresentationCode.FSINGL,
    'float64': RepresentationCode.FDOUBL
}


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
