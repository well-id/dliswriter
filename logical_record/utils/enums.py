from enum import Enum
from struct import Struct


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


class RepresentationCode(Enum):
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
    FSHORT = Struct('>h')
    FSINGL = Struct('>f')
    FSING1 = Struct('>ff')
    FSING2 = Struct('>fff')
    ISINGL = Struct('>i')
    VSINGL = Struct('>i')
    FDOUBL = Struct('>d')
    FDOUB1 = Struct('>dd')
    FDOUB2 = Struct('>ddd')
    CSINGL = Struct('>ff')
    CDOUBL = Struct('>dd')
    SSHORT = Struct('>b')
    SNORM = Struct('>h')
    SLONG = Struct('>i')
    USHORT = Struct('>B')
    UNORM = Struct('>H')
    ULONG = Struct('>I')
    UVARI = 'UVARI'
    IDENT = 'IDENT'
    ASCII = 'ASCII'
    DTIME = Struct('>BBBBBBH')
    ORIGIN = 'ORIGIN'
    OBNAME = 'OBNAME'
    OBJREF = 'OBJREF'
    ATTREF = 'ATTREF'
    STATUS = Struct('>B')
    UNITS = 'UNITS'