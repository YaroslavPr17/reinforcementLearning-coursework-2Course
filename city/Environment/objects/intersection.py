from Environment.objects.model_object import Object


class Intersection(Object):
    def __init__(self):
        super().__init__()
        self.label = 'X'
        self.lanes = dict()

    def __str__(self):
        return f"{self.label}" \
               f"({self.lanes.get('N','')}{self.lanes.get('W','')}{self.lanes.get('E','')}{self.lanes.get('S', '')},"\
               f"{sum(self.lanes.values())})".center(Intersection.slots)

    def __repr__(self):
        return self.__str__()
