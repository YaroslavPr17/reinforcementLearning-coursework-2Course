from Environment.objects.model_object import Object


class Road(Object):
    def __init__(self):
        self.label = 'R'

    def __repr__(self):
        return f"{self.label}()".center(Road.slots)

    def __str__(self):
        return f"{self.label}()".center(Road.slots)
