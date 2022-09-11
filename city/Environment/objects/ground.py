from Environment.objects.model_object import Object


class Ground(Object):
    """
    A class for Ground cell
    """

    def __init__(self):
        super().__init__()
        self.label = 'G'

    def __str__(self):
        return f"{self.label}()".ljust(Ground.slots)

    def __repr__(self):
        return self.__str__()

    def __copy__(self):
        return Ground()
