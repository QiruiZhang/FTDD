# import MQT bench
from mqt.bench import get_benchmark

'''
    Generate GHZ
'''
q_range = range(2, 130)
for q in q_range:
    # Get circuit from MQT bench
    file_name = "ghz_" + str(q)
    cir = get_benchmark("ghz", 1, q)
    # Post-processing to remove all barrier and measurement operations
    for i in range(len(cir.data)):
        if cir.data[i][0].name == 'barrier':
            break
    cir.data = cir.data[0:i]
    cir.qasm(False, "./Benchmarks/MQTbench/ghz/" + file_name + ".qasm")


'''
    Generate Graph state
'''
q_range = range(3, 51)
for q in q_range:
    # Get circuit from MQT bench
    file_name = "graph_state_" + str(q)
    cir = get_benchmark("graphstate", 1, q)
    # Post-processing to remove all barrier and measurement operations
    for i in range(len(cir.data)):
        if cir.data[i][0].name == 'barrier':
            break
    cir.data = cir.data[0:i]
    cir.qasm(False, "./Benchmarks/MQTbench/graph_state/" + file_name + ".qasm")


'''
    Generate Entangled-QFT
'''
q_range = range(2, 31)
for q in q_range:
    # Get circuit from MQT bench
    file_name = "qft_entangled_" + str(q)
    cir = get_benchmark("qftentangled", 1, q)
    # Post-processing to remove all barrier and measurement operations
    for i in range(len(cir.data)):
        if cir.data[i][0].name == 'barrier':
            break
    cir.data = cir.data[0:i]
    cir.qasm(False, "./Benchmarks/MQTbench/qft_entangled/" + file_name + ".qasm")
