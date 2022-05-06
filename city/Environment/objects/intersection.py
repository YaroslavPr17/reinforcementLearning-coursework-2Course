from Environment.objects.model_object import Object


class Intersection(Object):
    def __init__(self, road_dir: tuple):
        self.road_dir = road_dir
        self.label = 'X'

    def __repr__(self):
        return f"{self.label}({len(self.road_dir)})".center(Intersection.slots)

    def __str__(self):
        return f"{self.label}({len(self.road_dir)})".center(Intersection.slots)
