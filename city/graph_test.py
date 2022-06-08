from Agent.agent import Agent

a = Agent(3)
a.extract_q_table(Agent.load_compressed_q_table_from_file('compressed_q_table'))
a.perform(11)
