class ConstantMissingError(Exception):
    def __init__(self, message: str = 'Constant missing'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class CriticalBotError(Exception):
    def __init__(self, message: str = 'Critical bot error'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class DictKeyDoesNotExistError(Exception):
    def __init__(self, key: str, message: str = ('The dictionary key does '
                                                 'not exist')):
        self.key = key
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.key}'


class EndpointStatusError(Exception):
    def __init__(self, status: int, message: str = 'Endpoint status error'):
        self.const = status
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.const}'
