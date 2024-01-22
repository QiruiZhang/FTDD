''' This script benchmarks Google TensorNetwork backended by PyTorch '''
# Set single thread
import torch
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

# System
import sys
import signal
import numpy as np
import time
from math import ceil
import pandas as pd

# Import Python Utilities
sys.path.append('./source/')
from TDD import Ini_TDD
from TN import TensorNetwork,reorder_gts
from TDD_Q import get_real_qubit_num, add_inputs, cir_2_tn_lbl, TNtoCotInput2, squeezeTN, squeezeTN_ultra

# Import Qiskit
from qiskit import QuantumCircuit
from qiskit import Aer, transpile

# Import Cotengra
import cotengra as ctg


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

sys.stdout = Logger("./BenchFTDD/log/GTN/BenchGTN_" + case + ".log")


"""
    Global Initializations
"""
qubit_num_limit = 30
perf_meas_time = 2
time_limit = 3600

list_circuit_name = []
list_qubit_num = []
list_depth = []
list_gate_num = []

list_aer_time = []
list_gtn_time_t0c0 = []
list_gtn_time_t1c0 = []
list_gtn_time_t0c1 = []
list_gtn_time_t1c1 = []

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
    if ("ghz/ghz_" in file_name) and (n > 28):
        continue
    if ("graph_state/graph_state_" in file_name) and (n > 28):
        continue
    if ("qft/qft_" in file_name) and (n > 14):
        continue

    list_circuit_name.append(file[0])
    list_qubit_num.append(n)
    list_depth.append(depth)
    list_gate_num.append(len(tn_lbl.tensors))

    ''' Apply Tetris-like Tensor Network Squeezing'''
    tensors_tetris = squeezeTN(tn_lbl.tensors, n, depth)
    tensors_tetris = squeezeTN_ultra(tensors_tetris, n, depth)
    tn_tetris = TensorNetwork(tensors_tetris, tn_lbl.tn_type, n)

    ''' Add input state '''
    input_s = [0]*n
    if input_s and (not open_input):
        add_inputs(tn_lbl,input_s,n)
        add_inputs(tn_tetris,input_s,n)

    ''' Set-up inputs for opt_einsum and Cotengra '''
    tensor_list_t0, open_indices_t0, size_dict_t0, arrays_t0, oe_input_t0 = TNtoCotInput2(tn_lbl, n)
    tensor_list_t1, open_indices_t1, size_dict_t1, arrays_t1, oe_input_t1 = TNtoCotInput2(tn_tetris, n)

    ''' Setup Cotengra Optimizers '''
    opt = ctg.ReusableHyperOptimizer(
        minimize=f'combo-{56}',
        
        max_repeats=512,
        max_time=30,

        progbar=True,
        directory='./BenchFTDD/cotengra_cache'
    )

    ''' Set-up for different optimizations'''
    # Tetris = 0, Cotengra = 0
    path_t0c0 = tn_lbl.get_seq_path()

    # Tetris = 1, Cotengra = 0
    path_t1c0 = tn_tetris.get_seq_path()

    # Tetris = 0, Cotengra = 1
    tree_t0c1 = opt.search(tensor_list_t0, open_indices_t0, size_dict_t0)
    path_t0c1 = tree_t0c1.get_path()

    # Tetris = 1, Cotengra = 1
    tree_t1c1 = opt.search(tensor_list_t1, open_indices_t1, size_dict_t1)
    path_t1c1 = tree_t1c1.get_path()


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
        Simulat Google TensorNetwork, backended by PyTorch
    '''
    print("Simulating circuit with Google TensorNetwork (PyTorch backend)......")

    # t0c0
    signal.alarm(time_limit)
    try:
          # Initialize
        Ini_TDD(all_indexs_lbl)
          # First time meas
        t1 = time.perf_counter()
        res_GTN = tn_lbl.cont_GTN(path_t0c0, debug=False)
        t2 = time.perf_counter()
        dt = t2 - t1
          # Refine time meas
        if dt < perf_meas_time:
            N = ceil(perf_meas_time/dt)
            t1 = time.perf_counter()
            for i in range(N):
                res_GTN = tn_lbl.cont_GTN(path_t0c0, debug=False)
            t2 = time.perf_counter()
            dt = (t2 - t1)/N
        print("GTN t0c0 simulation finished with time, ", dt, "s")
        list_gtn_time_t0c0.append(dt)
    except TimeoutError:
        list_gtn_time_t0c0.append('T.O.')
        print("GTN t0c0 simulation timed out!")
    except Exception as e:
        list_gtn_time_t0c0.append('R.E.')
        print(f"Caught an exception: {e}")
    finally:
        signal.alarm(0)

    # t0c1
    signal.alarm(time_limit)
    try:
        # Initialize
        Ini_TDD(all_indexs_lbl)
        # First time meas
        t1 = time.perf_counter()
        res_GTN = tn_lbl.cont_GTN(path_t0c1, debug=False)
        t2 = time.perf_counter()
        dt = t2 - t1
        # Refine time meas
        if dt < perf_meas_time:
            N = ceil(perf_meas_time/dt)
            t1 = time.perf_counter()
            for i in range(N):
                res_GTN = tn_lbl.cont_GTN(path_t0c1, debug=False)
            t2 = time.perf_counter()
            dt = (t2 - t1)/N
        print("GTN t0c1 simulation finished with time, ", dt, "s")
        list_gtn_time_t0c1.append(dt)
    except TimeoutError:
        list_gtn_time_t0c1.append('T.O.')
        print("GTN t0c1 simulation timed out!")
    except Exception as e:
        list_gtn_time_t0c1.append('R.E.')
        print(f"Caught an exception: {e}")
    finally:
        signal.alarm(0)

    # t1c0
    signal.alarm(time_limit)
    try:
        # Initialize
        Ini_TDD(all_indexs_lbl)
        # First time meas
        t1 = time.perf_counter()
        res_GTN = tn_tetris.cont_GTN(path_t1c0, debug=False)
        t2 = time.perf_counter()
        dt = t2 - t1
        # Refine time meas
        if dt < perf_meas_time:
            N = ceil(perf_meas_time/dt)
            t1 = time.perf_counter()
            for i in range(N):
                res_GTN = tn_tetris.cont_GTN(path_t1c0, debug=False)
            t2 = time.perf_counter()
            dt = (t2 - t1)/N
        print("GTN t1c0 simulation finished with time, ", dt, "s")
        list_gtn_time_t1c0.append(dt)
    except TimeoutError:
        list_gtn_time_t1c0.append('T.O.')
        print("GTN t1c0 simulation timed out!")
    except Exception as e:
        list_gtn_time_t1c0.append('R.E.')
        print(f"Caught an exception: {e}")
    finally:
        signal.alarm(0)
    
    # t1c1
    signal.alarm(time_limit)
    try:
        # Initialize
        Ini_TDD(all_indexs_lbl)
        # First time meas
        t1 = time.perf_counter()
        res_GTN = tn_tetris.cont_GTN(path_t1c1, debug=False)
        t2 = time.perf_counter()
        dt = t2 - t1
        # Refine time meas
        if dt < perf_meas_time:
            N = ceil(perf_meas_time/dt)
            t1 = time.perf_counter()
            for i in range(N):
                res_GTN = tn_tetris.cont_GTN(path_t1c1, debug=False)
            t2 = time.perf_counter()
            dt = (t2 - t1)/N
        print("GTN t1c1 simulation finished with time, ", dt, "s")
        list_gtn_time_t1c1.append(dt)
    except TimeoutError:
        error = True
        list_gtn_time_t1c1.append('T.O.')
        print("GTN t1c1 simulation timed out!")
    except Exception as e:
        error = True
        list_gtn_time_t1c1.append('R.E.')
        print(f"Caught an exception: {e}")
    finally:
        signal.alarm(0)

    # Convert result to vector array for comparison with IBM
    if n <= qubit_num_limit and (not open_input) and (not error):
        res_GTN_reord = reorder_gts(res_GTN)  
        state_GTN = np.transpose(res_GTN_reord[0].tensor).flatten()

    print('')


    ''' 
        Verify GTN against IBM Qiskit Aer
    '''
    if n <= qubit_num_limit and (not open_input) and (not error):
        print("GTN vs. Qiskit quantum state difference is ", np.average(np.abs(state_GTN - state_Aer)))
        fidelity = np.abs(np.inner(state_GTN, state_Aer.conj()))
        print("GTN vs. Qiskit fidelity is ", fidelity*100, "%")
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

    "GTN baseline CPU Time (s)":    list_gtn_time_t0c0,
    "GTN w/ Tetris CPU Time (s)":   list_gtn_time_t1c0,
    "GTN w/ Cotengra CPU Time (s)": list_gtn_time_t0c1,
    "GTN w/ both CPU Time (s)":     list_gtn_time_t1c1,

    "GTN w/ both fidelity":         list_fidelity   
}

res_path = "./BenchFTDD/data/GTN/"
res_csv_name = (
            res_path
            + "BenchGTN_" + case
            + ".csv"
        )
df_bench = pd.DataFrame(dict_bench)
df_bench.to_csv(res_csv_name)