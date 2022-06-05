from Environment.objects.model_object import Object


class Car(Object):
    def __init__(self, direction: str, road_coordinates: tuple, lane: int):
        super().__init__()
        self.direction = direction
        self.road_coordinates = road_coordinates
        self.lane = lane
