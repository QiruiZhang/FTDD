path = './Benchmarks/MQTbench/'
benchmarks = []

''' Graph State '''
file_name_base = "graph_state/graph_state_"
# GTN memory out >= 29
q_range = [25, 26, 27, 28] 
for q in q_range:
    benchmarks.append( (file_name_base + str(q) + '.qasm', False) )

case_name = "GraphState"