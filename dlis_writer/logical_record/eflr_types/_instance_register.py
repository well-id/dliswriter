from dlis_writer.logical_record.core.iflr_eflr_base import IflrAndEflrRMeta


class InstanceRegisterMeta(IflrAndEflrRMeta):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj._instance_dict = {}
        return obj


class InstanceRegisterMixin(metaclass=InstanceRegisterMeta):
    from_config: callable  # from EFLR

    def __init__(self, name):
        self._instance_dict[name] = self

    @classmethod
    def get_instance(cls, name):
        return cls._instance_dict.get(name)

    @classmethod
    def get_or_make_from_config(cls, name, config):
        if name in cls._instance_dict:
            return cls.get_instance(name)

        if name in config.sections():
            if (object_name := config[name].get('name', None)) in cls._instance_dict:
                return cls.get_instance(object_name)

        return cls.from_config(config, key=name)
