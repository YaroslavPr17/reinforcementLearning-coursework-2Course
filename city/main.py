from Agent.agent import Agent

agent = Agent(map_sample=1, layout_sample=0, graphics=False, delay=1.5)
agent.extract_q_table(Agent.load_compressed_q_table_from_file('compressed_q_table'))
agent.perform(11)


