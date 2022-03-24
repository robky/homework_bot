class ConstantMissingError(Exception):
    def __init__(self, const: str, message: str):
        self.const = const
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.const}'