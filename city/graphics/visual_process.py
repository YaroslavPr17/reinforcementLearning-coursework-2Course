import threading
from graphics.env_vizualization import MapVizualization
from Environment.city import City


class Visualizer(threading.Thread):

    def __init__(self, env: City, delay: float):
        super().__init__()
        self.env = env
        self.delay = delay

    def run(self) -> None:
        map_visualization = MapVizualization(self.env, self.delay)
        map_visualization.mainloop()
        map_visualization.clear()
