path = './Benchmarks/MQTbench/'
benchmarks = []

''' QFT circuit '''
file_name_base = "qft/qft_"
# GTN memory out >= 15
q_range = [11, 12, 13, 14, 15, 16, 17, 18] # 15 memory out for GTN
for q in q_range:
    benchmarks.append( (file_name_base + str(q) + '.qasm', True) )

case_name = "QFT"