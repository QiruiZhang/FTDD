''' This script benchmarks the original PyTDD '''
# System
import sys
import signal
import numpy as np
import time
from math import ceil
import pandas as pd

# Import PyTDD
sys.path.append('./source/')
from TDD import Ini_TDD
from TDD_Q import get_real_qubit_num, cir_2_tn_lbl, add_inputs

# Import Qiskit
from qiskit import QuantumCircuit
from qiskit import Aer, transpile


''' Import benchmarks '''
try:
    case = sys.argv[1]
    print(case)
except:
    print("Please provide the case you want to test!")
    sys.exit()

if case == "GHZ":
    import TestCases.TestGHZ as TestCases 
elif case == "GraphState":
    import TestCases.TestGraphState as TestCases
elif case == "QFT":
    import TestCases.TestQFT as TestCases
elif case == "EQFT":
    import TestCases.TestEQFT as TestCases
elif case == "QAOA":
    import TestCases.TestQAOA as TestCases
elif case == "VQE":
    import TestCases.TestVQE as TestCases
elif case == "GRQC":
    import TestCases.TestGRQC as TestCases
else:
    print("Please provide a valid case!")
    sys.exit()


"""
    Utility
"""
# Function to handle the alarm
def handle_alarm(signum, frame):
    raise TimeoutError()

# Set the signal handler
signal.signal(signal.SIGALRM, handle_alarm)

# Logger
class Logger(object):
    def __init__(self, filename="logfile.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

sys.stdout = Logger("./BenchFTDD/log/PyTDD/BenchPyTDD_" + case + ".log")


"""
    Global Initializations
"""
qubit_num_limit = 20
perf_meas_time = 2
meas_max_iter = 20
time_limit = 3600

list_circuit_name = []
list_qubit_num = []
list_depth = []
list_gate_num = []

list_aer_time = []
list_ptdd_time = []
list_fidelity = []


"""
    Loop all the benchmarks
"""
path = TestCases.path
for file in TestCases.benchmarks:
    error = False
    print("Benchmarking " + file[0] + "......\n")
    file_name = path + file[0]
    open_input = file[1]

    ''' Transpile circuit '''
    cir = QuantumCircuit.from_qasm_file(file_name)
    tn_lbl, all_indexs_lbl, depth = cir_2_tn_lbl(cir)
    n = get_real_qubit_num(cir)

    # Jump known time-out circuits
    if ("vqe/vqe_indep_qiskit_" in file_name): # division by zero
        continue

    list_circuit_name.append(file[0])
    list_qubit_num.append(n)
    list_depth.append(depth)
    list_gate_num.append(len(tn_lbl.tensors))

    ''' Add input state '''
    input_s = [0]*n
    if input_s and (not open_input):
        add_inputs(tn_lbl,input_s,n)

    path_t0c0 = tn_lbl.get_seq_path()

    ''' 
        Simulate with AER 
    '''
    if n <= qubit_num_limit and (not open_input):
        print("Simulating circuit with IBM Qiskit Aer......")
        # Set Aer simulation backend
        aer_simulator = Aer.get_backend('aer_simulator')
        aer_simulator.set_options(precision='double')
        # Construct circuit from QASM
        cir_Aer = QuantumCircuit.from_qasm_file(file_name)
        cir_Aer.save_statevector()
        cir_Aer = transpile(cir_Aer, aer_simulator)
        # Simulate and get state vector
        t1 = time.perf_counter()
        result = aer_simulator.run(cir_Aer).result()
        t2 = time.perf_counter()
        dt = t2 - t1
        print("Aer simulation finished with time ", dt, "s")
        list_aer_time.append(dt)
        statevector = result.get_statevector(cir_Aer)
        state_Aer = np.asarray(statevector)

        print('')
    else:
        list_aer_time.append('N/A')


    ''' 
        Simulat PyTDD
    '''
    print("Simulating circuit with PyTDD......")
    signal.alarm(time_limit)
    try:
          # First time meas
        t1 = time.perf_counter()
        Ini_TDD(all_indexs_lbl)
        ptdd = tn_lbl.cont_TN(path_t0c0, False)
        t2 = time.perf_counter()
        dt = t2 - t1
          # Refine time meas
        if dt < perf_meas_time:
            N = min(ceil(perf_meas_time/dt), meas_max_iter)
            t1 = time.perf_counter()
            for i in range(N):
                Ini_TDD(all_indexs_lbl)
                ptdd = tn_lbl.cont_TN(path_t0c0, False)
            t2 = time.perf_counter()
            dt = (t2 - t1)/N
        print("PyTDD simulation finished with time, ", dt, "s")
        list_ptdd_time.append(dt)
    except TimeoutError:
        error = True
        list_ptdd_time.append('T.O.')
        print("PyTDD simulation timed out!")
    except Exception as e:
        error = True
        list_ptdd_time.append('R.E.')
        print(f"Caught an exception: {e}")
    finally:
        signal.alarm(0)
    
    # Convert result to vector array for comparison with IBM
    if n <= qubit_num_limit and (not open_input) and (not error):
        state_ptdd = ptdd.to_array().flatten()

    print('')


    ''' 
        Verify PyTDD against IBM Qiskit Aer
    '''
    if n <= qubit_num_limit and (not open_input) and (not error):
        print("PyTDD vs. Qiskit quantum state difference is ", np.average(np.abs(state_ptdd - state_Aer)))
        fidelity = np.abs(np.inner(state_ptdd, state_Aer.conj()))
        print("PyTDD vs. Qiskit fidelity is ", fidelity*100, "%")
        list_fidelity.append(fidelity)
    else:
        list_fidelity.append(1)

    print('\n')


''' Generate the benchmarking results and save to .csv '''
dict_bench = {
    "Circuit Name":                 list_circuit_name,
    "Number of Qubits":             list_qubit_num,
    "Depth":                        list_depth,
    "Number of Gates":              list_gate_num,

    "Aer CPU Time (s)":             list_aer_time,

    "PyTDD CPU Time (s)":           list_ptdd_time,
    "PyTDD fidelity":               list_fidelity   
}

res_path = "./BenchFTDD/data/PyTDD/"
res_csv_name = (
            res_path
            + "BenchPyTDD_" + case
            + ".csv"
        )
df_bench = pd.DataFrame(dict_bench)
df_bench.to_csv(res_csv_name)