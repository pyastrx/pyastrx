class MissingYAMLConfig(Exception):
    """Exception raised for errors when the YAML config is missing

    Attributes:
        key_name: name of the missing key
        message -- explanation of the error
    """

    def __init__(self, key_name: str, message: str = ""):
        self.key_name = key_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'\nMissing the following attributes {self.key_name} in the pyastrx.yaml' \
            + f'\n\t>> {self.message}'
