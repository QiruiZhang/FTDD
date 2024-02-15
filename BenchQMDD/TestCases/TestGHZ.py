path = './Benchmarks/MQTbench/'
benchmarks = []

''' GHZ '''
file_name_base = "ghz/ghz_"
# GTN memory out >= 29
q_range = [25, 26, 27, 28]
for q in q_range:
    benchmarks.append( (file_name_base + str(q) + '.qasm', False) )

case_name = "GHZ"