path = './Benchmarks/MQTbench/'
benchmarks = []

''' entangled QFT '''
file_name_base = "qft_entangled/qft_entangled_"
# QMDD times out >= 18
q_range = [14, 15, 16, 17]
for q in q_range:
    benchmarks.append( (file_name_base + str(q) + '.qasm', False) )

case_name = "EQFT"