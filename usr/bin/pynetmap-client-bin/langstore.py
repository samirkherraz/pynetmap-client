import ConfigParser
from const import CONFIG_PATH


class LangStore():
    def __init__(self, config):
        self.configuration = ConfigParser.ConfigParser()
        self.file = "/etc/pynetmap-client/langs.conf"
        self.config = config

    def read(self):
        with open(self.file, "r") as fp:
            self.configuration.readfp(fp)

    def get(self, key):
        try:
            return self.configuration.get(self.config.get("Language"), key)
        except:
            try:
                return self.configuration.get("DEFAULT", key)
            except:
                return key
