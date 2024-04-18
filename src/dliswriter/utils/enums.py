from dliswriter.utils.internal.validator_enum import ValidatorEnum


class Unit(ValidatorEnum):
    """All units explicitly allowed by the RP66 standard."""

    AMPERE = "A"
    KELVIN = "K"
    CANDELA = "cd"
    API_GRAVITY = "dAPI"
    DECIBEL = "dB"
    API_GAMMA_RAY = "gAPI"
    KILOGRAM = "kg"
    METER = "m"
    MOLE = "mol"
    API_NEUTRON = "nAPI"
    RADIAN = "rad"
    SECOND = "s"
    STERADIAN = "sr"
    BRITISH_THERMAL_UNIT = "Btu"
    COULOMB = "C"
    DARCY = "D"
    GIGAPASCAL = "GPa"
    GAL = "Gal"
    HERTZ = "Hz"
    JOULE = "J"
    LITER = "L"
    MEGAHERTZ = "MHz"
    MEGAPASCAL = "MPa"
    MEGAELECTRONVOLT = "MeV"
    MEGAGRAM = "Mg"
    MEGA_POUNDS_PER_SQUARE_METER = "Mpsi"
    NEWTON = "N"
    OERSTED = "Oe"
    POISE = "P"
    PASCAL = "Pa"
    SIEMENS = "S"
    TESLA = "T"
    VOLT = "V"
    WATT = "W"
    WEBER = "Wb"
    ANNUM = "a"
    ACRE = "acre"
    STD_ATMOSPHERE = "atm"
    BARN = "b"
    BAR = "bar"
    BARREL = "bbl"
    REVOLUTION_CYCLE = "c"
    CENTIPOISE = "cP"
    CALORIE = "cal"
    CENTIMETER = "cm"
    CAPTURE_UNIT = "cu"
    DAY = "d"
    DECANEWTON = "daN"
    DEGREE_ANGLE = "deg"
    DEGREE_CELSIUS = "degC"
    DEGREE_FAHRENHEIT = "degF"
    DECIMETER = "dm"
    ELECTRONVOLT = "eV"
    FEMTOCOULOMB = "fC"
    FOOT = "ft"
    GRAM = "g"
    GALLON = "gal"
    HOUR = "h"
    INCH = "in"
    KILOHERTZ = "kHz"
    KILOPASCAL = "kPa"
    KILOVOLT = "kV"
    KILOELECTRONVOLT = "keV"
    KILOGRAM_FORCE = "kgf"
    KILOMETER = "km"
    POUND_FORCE = "lbf"
    POUND_MASS = "lbm"
    MILLIAMPERE = "mA"
    MILLICOULOMB = "mC"
    MILLIDARCY = "mD"
    MILLIGAL = "mGal"
    MILLILITER = "mL"
    MILLISIEMENS = "mS"
    MILLITESLA = "mT"
    MILLIVOLT = "mV"
    MILLIWAT = "mW"
    MILLIGRAM = "mg"
    MINUTE = "min"
    MILLIMETER = "mm"
    MILLIOHM = "mohm"
    MILLISECOND = "ms"
    NANOCOULOMB = "nC"
    NANOWATT = "nW"
    NANOSECOND = "ns"
    OHM = "ohm"
    PICCOCOULOMB = "pC"
    PICOPASCAL = "pPa"
    PART_PER_TEN_THOUSAND = "ppdk"
    PART_PER_THOUSAND = "ppk"
    PART_PER_MILLION = "ppm"
    POUND_PER_SQUARE_INCH = "psi"
    POROSITY_UNIT = "pu"
    METRIC_TON = "t"
    US_SHORT_TON = "ton"
    MICROAMPERE = "uA"
    MICROCOULOMB = "uC"
    MICROPASCAL = "uPa"
    MICROVOLT = "uV"
    MICROMETER = "um"
    MICROOHM = "uohm"
    MICRO_POUND_PER_SQUARE_INCH = "upsi"
    MICROSECOND = "us"


class Property(ValidatorEnum):
    """Allowed values for elements of the 'properties' attribute of Channel, Computation, and Process"""

    AVERAGED = 'AVERAGED'
    CALIBRATED = 'CALIBRATED'
    CHANGED_INDEX = 'CHANGED-INDEX'
    COMPUTED = 'COMPUTED'
    DEPTH_MATCHED = 'DEPTH-MATCHED'
    DERIVED = 'DERIVED'
    FILTERED = 'FILTERED'
    HOLE_SIZE_CORRECTED = 'HOLE-SIZE-CORRECTED'
    INCLINOMETRY_CORRECTED = 'INCLINOMETRY-CORRECTD'
    LITHOLOGY_CORRECTED = 'LITHOLOGY-CORRECTED'
    LOCAL_COMPUTATION = 'LOCAL-COMPUTATION'
    LOCALLY_DEFINED = 'LOCALLY-DEFINED'
    MODELLED = 'MODELLED'
    MUDCAKE_CORRECTED = 'MUDCAKE-CORRECTED'
    NORMALIZED = 'NORMALIZED'
    OVERSAMPLED = 'OVER-SAMPLED'
    PATCHED = 'PATCHED'
    PRESSURE_CONTROLLED = 'PRESSURE-CORRECTED'
    RESAMPLED = 'RE-SAMPLED'
    SALINITY_CONTROLLED = 'SALINITY-CORRECTED'
    SAMPLED_DOWNWARD = 'SAMPLED-DOWNWARD'
    SAMPLED_UPWARD = 'SAMPLED-UPWARD'
    SPEED_CORRECTED = 'SPEED-CORRECTED'
    SPLICED = 'SPLICED'
    SQUARED = 'SQUARED'
    STACKED = 'STACKED'
    STD = 'STANDARD-DEVIATION'
    STANDOFF_CORRECTED = 'STANDOFF-CORRECTED'
    TEMPERATURE_CORRECTED = 'TEMPERATURE-CORRECTED'
    UNDERSAMPLED = 'UNDER-SAMPLED'


class CalibrationMeasurementPhase(ValidatorEnum):
    """Allowed values for 'phase' of a CalibrationMeasurementItem."""

    AFTER = 'AFTER'
    BEFORE = 'BEFORE'
    MASTER = 'MASTER'


class EquipmentType(ValidatorEnum):
    """Options for the 'type' ('_type') attribute of Equipment, allowed by the standard"""

    ADAPTER = "Adapter"
    BOARD = "Board"
    BOTTOM_NOSE = "Bottom-Nose"
    BRIDLE = "Bridle"
    CABLE = "Cable"
    CALIBRATOR = "Calibrator"
    CARTRIDGE = "Cartridge"
    CENTRALIZER = "Centralizer"
    CHAMBER = "Chamber"
    CUSHION = "Cushion"
    DEPTH_DEVICE = "Depth-Device"
    DISPLAY = "Display"
    DRAWER = "Drawer"
    EXCENTRALIZER = "Excentralizer"
    EXPLOSIVE_SOURCE = "Explosive-Source"
    FLASK = "Flask"
    GEOPHONE = "Geophone"
    GUN = "Gun"
    HEAD = "Head"
    HOUSING = "Housing"
    JIG = "Jig"
    JOINT = "Joint"
    NUCLEAR_DETECTOR = "Nuclear-Detector"
    PACKER = "Packer"
    PAD = "Pad"
    PANE = "Pane"
    POSITIONING = "Positioning"
    PRINTER = "Printer"
    RADIOACTIVE_SOURCE = "Radioactive-Source"
    SHIELD = "Shield"
    SIMULATOR = "Simulator"
    SKID = "Skid"
    SONDE = "Sonde"
    SPACER = "Spacer"
    STANDOFF = "Standoff"
    SYSTEM = "System"
    TOOL = "Tool"
    TOOL_MODULE = "Tool-Module"
    TRANSDUCER = "Transducer"
    VIBRATION_SOURCE = "Vibration-Source"


class EquipmentLocation(ValidatorEnum):
    """Options for the 'location' attribute of Equipment, allowed by the standard."""

    LOGGING_SYSTEM = 'Logging-System'
    REMOTE = 'Remote'
    RIG = 'Rig'
    WELL = 'Well'


class FrameIndexType(ValidatorEnum):
    """Values for frame index type allowed by the standard."""

    ANGULAR_DRIFT = 'ANGULAR-DRIFT'
    BOREHOLE_DEPTH = 'BOREHOLE-DEPTH'
    NON_STANDARD = 'NON-STANDARD'
    RADIAL_DRIFT = 'RADIAL-DRIFT'
    VERTICAL_DEPTH = 'VERTICAL-DEPTH'


class ProcessStatus(ValidatorEnum):
    """Allowed values of the 'status' Attribute of Process."""

    COMPLETE = 'COMPLETE'
    ABORTED = 'ABORTED'
    IN_PROGRESS = 'IN-PROGRESS'


class ZoneDomain(ValidatorEnum):
    """Allowed values for 'domain' Attribute of Zone.

    Comments are quotes from RP66; 'Zone interval is'...:"""

    BOREHOLE_DEPTH = 'BOREHOLE-DEPTH'   # 'along the borehole'
    TIME = 'TIME'                       # 'elapsed time'
    VERTICAL_DEPTH = 'VERTICAL-DEPTH'   # 'depth along the Vertical Generatrix'
