class ConstantMissingError(Exception):
    def __init__(self, const: str = '', message: str = 'Constant missing'):
        self.const = const
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.const}'


class EndpointStatusError(Exception):
    def __init__(self, status: int, message: str = 'Endpoint status error'):
        self.const = status
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.const}'
