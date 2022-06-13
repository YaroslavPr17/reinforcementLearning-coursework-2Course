from graphics.env_vizualization import MapVizualization
from Environment.city import City

from Agent.agent import Agent

a = Agent(1)
a.extract_q_table(Agent.load_compressed_q_table_from_file('compressed_q_table'))
a.perform(11)
