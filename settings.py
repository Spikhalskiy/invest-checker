import ConfigParser

from functools import partial
from itertools import chain


class Helper:
    def __init__(self, section, file):
        self.readline = partial(next, chain(("[{0}]\n".format(section),), file, ("",)))


class Settings:
    __MOCK_SECTION_NAME = "Foo"
    __config = None

    def __init__(self, filename):
        self.__config = ConfigParser.RawConfigParser(allow_no_value=True)
        with open(filename) as settings_file:
            self.__config.readfp(Helper(self.__MOCK_SECTION_NAME, settings_file))

    def get_property(self, key):
        return self.__config.get(self.__MOCK_SECTION_NAME, key)