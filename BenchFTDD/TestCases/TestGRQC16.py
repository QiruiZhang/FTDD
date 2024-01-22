path = '/home/qiruizh/QCS/TDD-fork/Benchmarks/MQTbench/'
benchmarks = []

''' GRQC '''
file_name_base = "GRQC/inst_4x4_"
d_range = [10, 12, 14, 16]
for d in d_range:
    benchmarks.append( (file_name_base + str(d) + '_8.qasm', False) )

case_name = "GRQC16"