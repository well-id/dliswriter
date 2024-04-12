from dataclasses import dataclass


@dataclass
class DLISWriterConfig:
    high_compat_mode: bool = False


global_config = DLISWriterConfig()
