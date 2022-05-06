from Environment.objects.model_object import Object


class Ground(Object):
    def __init__(self):
        self.label = 'G'

    def __repr__(self):
        return f"{self.label}()".center(Ground.slots)

    def __str__(self):
        return f"{self.label}()".center(Ground.slots)
