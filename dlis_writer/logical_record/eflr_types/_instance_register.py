class InstanceRegisterMixin:
    from_config: callable  # from EFLR
    _instance_dict = {}

    def __init__(self, name):
        self._instance_dict[name] = self

    @classmethod
    def get_instance(cls, name):
        return cls._instance_dict.get(name)

    @classmethod
    def get_or_make_from_config(cls, name, config):
        if name in cls._instance_dict:
            return cls.get_instance(name)
        return cls.from_config(config, key=name)
