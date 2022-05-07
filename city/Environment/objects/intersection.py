from Environment.objects.model_object import Object


class Intersection(Object):
    def __init__(self, index: int):
        self.index = index
        self.label = 'X'
        self.lanes = dict()

    def __str__(self):
        return f"{self.label}({self.index},{self.lanes.get('N', '')}{self.lanes.get('W', '')}{self.lanes.get('E', '')}"\
               f"{self.lanes.get('S', '')},{sum(self.lanes.values())})".center(Intersection.slots)
