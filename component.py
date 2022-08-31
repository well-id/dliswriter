from common.data_types import *

component_dictionary = {
	'000': 'ABSATR',
	'001': 'ATTRIB',
	'010': 'INVATR',
	'011': 'OBJECT',
	'100': 'reserved',
	'101': 'RDSET',
	'110': 'RSET',
	'111': 'SET'
}


class Component(object):
	def smh(self):
		pass

class Set(Component):

	'''

	Each Logical Record Segment must contain at least 1 set component.
	Set component determines the type of objects that is in the Logical Record Segment



	:set_type -> MUST be one of the following:
		FILE-HEADER
		ORIGIN
		WELL-REFERENCE
		AXIS
		CHANNEL
		FRAME
		PATH
		CALIBRATION
		CALIBRATION-COEFFICIENT
		CALIBRATION-MEASUREMENT
		COMPUTATION
		EQUIPMENT
		GROUP
		PARAMETER
		PROCESS
		SPICE
		TOOL
		ZONE
		COMMENT
		UPDATE
		NO-FORMAT
		LONG-NAME
		ATTRIBUTE
		CODE
		EFLR
		IFLR
		OBJECT-TYPE
		REPRESENTATION-CODE
		SPECIFICATION
		UNIT-SYMBOL
		BASE-DICTIONARY
		IDENTIFIER
		LEXICON
		OPTION

	Please keep in mind that each Logical Record Type has a list of "allowable set types"
	For example, a if the Logical Record Type is "FILE-HEADER" set_type can only be "FILE-HEADER"
	For the full list of Logical Record Types and allowable set types,
	please visit http://w3.energistics.org/rp66/v1/rp66v1_appa.html#A_2


	:set_name (optional)

	'''


	def __init__(self,
				 set_type:str,
				 set_name:str=None):

		self.set_type = set_type
		self.set_name = set_name

	def get_as_bytes(self):

		set_component_bytes = b''

		if self.set_name:
			descriptive_bits = '11111000'
		else:
			descriptive_bits = '11110000'

		set_component_bytes += write_struct('USHORT', int(descriptive_bits, 2))
		set_component_bytes += write_struct('IDENT', self.set_type)

		if self.set_name:
			set_component_bytes += write_struct('IDENT', self.set_name)

		return set_component_bytes






class Attribute(Component):

	'''

	QUOTE
		1. The Label Characteristic is a dictionary-controlled name that identifies the Attribute. 
		The phrases "Attribute Label", "Attribute Name", and "Attribute Label Characteristic" are used 
		interchangeably for both Attribute Components and Invariant Attribute Components.
		
		2. The Count, Representation Code, Units,; and Value Characteristics are closely related. 
		A Value consists of zero or more ordered Elements. Each Element has the same Representation Code, 
		specified by the value of the Representation Code Characteristic, and the same physical units of measurement, 
		specified by the Units Characteristic. The number of Elements that make up the Value is specified by the Count Characteristic. 
		The Count Characteristic may be zero. In this case, the Value Characteristic is undefined, i.e., it is an Absent Value.
		Note that although the Representation Code Characteristic is always represented in a Component as a USHORT (one-byte unsigned integer), 
		the global default value for this Characteristic is the numeric code denoted by the symbol IDENT (see Appendix B).
		The phrases "Attribute Count" and "Attribute Count Characteristic" are used interchangeably, as are "Attribute Value" 
		and "Attribute Value Characteristic", as are "Attribute Representation Code" and "Attribute Representation Code Characteristic", 
		as are "Attribute Units" and "Attribute Units Characteristic".

	END QUOTE FROM -> RP66 V1 Section 3.2.2.1 -> http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2_1






	'''


	def __init__(self,
				 label:str=None,
				 count:int=1,
				 representation_code:str='IDENT',
				 units:str=None,
				 value=None):


		self.label = label
		self.count = count
		self.representation_code = representation_code
		self.units = units
		self.value = value


class Template(object):
	'''

	Each Logical Record Segment has a template right after the set_component.


	QUOTE
		A Set consists of one or more Objects, preceded by a Template. The Objects in a Set share 
		a common set of Attributes. The order and default Characteristics for these Attributes 
		are defined in the Template. The Template immediately follows the Set Component and is 
		terminated by an Object Component. A Template consists of a collection of 
		Attribute Components and/or Invariant Attribute Components, mixed in any fashion. 
		These Components define the structure of the Objects in the Set.

	END QUOTE FROM -> RP66 V1 Section 3.2.2.2 -> http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2_2

	'''


	def __init__(self,
				 components:list=[]):
		'''
		
		:components -> A list of Component object instances.

		'''
		self.components = components


class Object(Component):
	'''
	
	Object component has an OBNAME, and a list of Attribute object instances.

	Name of the Object is specified with representation code: OBNAME -> http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_23
	
	This OBNAME object has:
		:origin_reference -> The Origin Subfield must reference an Origin Object that is present in the same Logical File.
		:copy_number
		:name
		:attributes -> A list of Attribute object instances


	'''

	def __init__(self,
				 name:str,
				 origin_reference:int=None,
				 copy_number:int=0,
				 attributes:list=[]):

		self.name = name
		self.origin_reference = origin_reference
		self.copy_number = copy_number
		self.attributes = attributes
