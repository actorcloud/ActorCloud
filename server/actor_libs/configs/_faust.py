from ._base import BaseConfig
import pytz


__all__ = ['FaustConfig']


class FaustConfig:
    __config = BaseConfig().config

    def __init__(self):
        self.__dict__ = self.__config

    @property
    def config(self):
        return self.__dict__


_config = FaustConfig()
_config.TIMEZONE = pytz.timezone(_config.TIMEZONE)
_config.KAFKA_SERVERS = ';'.join(_config.KAFKA_SERVERS)



