path = './Benchmarks/MQTbench/'
benchmarks = []

''' QAOA '''
file_name_base = "qaoa/qaoa_indep_qiskit_"
# QMDD core dump
q_range = [12, 13, 14, 15]
for q in q_range:
    benchmarks.append( (file_name_base + str(q) + '.qasm', False) )

case_name = "QAOA"