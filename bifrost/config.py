class ConfigObject(dict):
    DEBUG = True
    EXTENSION_DIR = "."

    def __getattr__(self, item):
        return self.get(item)


Config = ConfigObject()
