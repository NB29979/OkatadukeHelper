import re


class RegexDict(dict):
    def __init__(self, items=None):
        for key, value in items.items():
            self.__setitem__(key, value)

    def __getitem__(self, item):
        try:
            return super(self.__class__, self).__getitem__(item)
        except:
            for key, value in self.items():
                if isinstance(key, re.Pattern) and key.match(item):
                    return value
            raise KeyError('key not found for %s'%item)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = re.compile(key)
        super(self.__class__, self).__setitem__(key, value)
