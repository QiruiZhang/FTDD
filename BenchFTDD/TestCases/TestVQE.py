path = '/home/qiruizh/QCS/TDD-fork/Benchmarks/MQTbench/'
benchmarks = []

''' VQE '''
file_name_base = "vqe/vqe_indep_qiskit_"
# PyTDD division by zero
q_range = [16, 17, 18, 19]
for q in q_range:
    benchmarks.append( (file_name_base + str(q) + '.qasm', False) )

case_name = "VQE"