import threading
from graphics.env_vizualization import MapVizualization
from Environment.city import City


class Visualizer(threading.Thread):

    def __init__(self, env: City, delay: float):
        super().__init__()
        self.env = env
        self.delay = delay
        self.map_visualization = None

    def run(self) -> None:
        self.map_visualization: MapVizualization = MapVizualization(self.env, self.delay)
        self.map_visualization.mainloop()
        self.map_visualization.clear()
