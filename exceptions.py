class ConstantMissingError(Exception):
    pass


class EndpointStatusError(Exception):
    def __init__(self, status: int, message: str = 'Ошибка статуса'):
        self.const = status
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.const}'
