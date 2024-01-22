''' This script benchmarks FTDD '''
# System
import sys
import signal
import numpy as np
import time
from math import ceil
import pandas as pd

# Import Python Utilities
sys.path.append('./source')
from TN import TensorNetwork
from TDD_Q import get_real_qubit_num,add_inputs,cir_2_tn_lbl, TNtoCotInput, squeezeTN, squeezeTN_ultra

# Import cTDD
sys.path.append('./source/cpp/build/')
import cTDD

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
elif case == "GRQC16":
    import TestCases.TestGRQC16 as TestCases
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

sys.stdout = Logger("./BenchFTDD/log/FTDD/BenchFTDD_" + case + ".log")

# Convert PyTN to cTN
def PyTN_2_cTN(tn_lbl):
    # Create cTDD tensor network
    cTN = cTDD.TensorNetwork(tn_lbl.tn_type, tn_lbl.qubits_num)
    
    # Add tensors from PyTDD TN to cTDD TN
    for ts in tn_lbl.tensors:
        # Create C++ tensor
        data = ts.data.flatten()
        shape = ts.data.shape
        index_key = [ind.key for ind in ts.index_set]
        index_idx = [ind.idx for ind in ts.index_set]
        name = ts.name
        qubits_list = ts.qubits
        depth = ts.depth
        cTensor = cTDD.Tensor(data, list(shape), index_key, index_idx, name, qubits_list, depth)
        # Add C++ Tensor to C++ TN
        cTN.add_tensor(cTensor, False)
    
    return cTN


"""
    Global Initializations
"""
qubit_num_limit = 20
perf_meas_time = 2
meas_max_iter = 50
time_limit = 3600

list_circuit_name = []
list_qubit_num = []
list_depth = []
list_gate_num = []

list_aer_time = []
list_tetris_time = []
list_ctdd_time_t0c0 = []
list_ctdd_time_t1c0 = []
list_ctdd_time_t0c1 = []
list_ctdd_time_t1c1 = []

list_fidelity = []

list_ctdd_node_t0c0 = []
list_ctdd_node_t0c1 = []
list_ctdd_node_t1c0 = []
list_ctdd_node_t1c1 = []

list_ctdd_gc_t0c0 = []
list_ctdd_gc_t0c1 = []
list_ctdd_gc_t1c0 = []
list_ctdd_gc_t1c1 = []


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

    list_circuit_name.append(file[0])
    list_qubit_num.append(n)
    list_depth.append(depth)
    list_gate_num.append(len(tn_lbl.tensors))

    ''' Apply Tetris-like Tensor Network Squeezing'''
    t1 = time.perf_counter()
    tensors_tetris = squeezeTN(tn_lbl.tensors, n, depth)
    tensors_tetris = squeezeTN_ultra(tensors_tetris, n, depth)
    tn_tetris = TensorNetwork(tensors_tetris, tn_lbl.tn_type, n)
    t2 = time.perf_counter()
    dt = t2 - t1
    print("Tetris costs time ", dt, "s\n")
    list_tetris_time.append(dt)

    print("Original circuit size: ", len(tn_lbl.tensors))
    print("Post-Tetris circuit size: ", len(tn_tetris.tensors), "\n")

    
    ''' Add input state '''
    input_s = [0]*n
    if input_s and (not open_input):
        add_inputs(tn_lbl,input_s,n)
        add_inputs(tn_tetris,input_s,n)

    ''' Set-up inputs for opt_einsum and Cotengra '''
    tensor_list_t0, open_indices_t0, size_dict_t0, arrays_t0, oe_input_t0 = TNtoCotInput(tn_lbl, n)
    tensor_list_t1, open_indices_t1, size_dict_t1, arrays_t1, oe_input_t1 = TNtoCotInput(tn_tetris, n)

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
        cTDD Table parameters
    '''
    nQubit = min(n, qubit_num_limit)
    load_factor = 0.6
    alpha  = 2
    beta = alpha * load_factor

    NBUCKET = int(alpha * 2**nQubit)
    INITIAL_GC_LIMIT = int(beta * 2**nQubit)
    INITIAL_GC_LUR = 0.9
    ACT_NBUCKET = 16384
    CCT_NBUCKET = 16384
    uniqTabConfig = [INITIAL_GC_LIMIT, INITIAL_GC_LUR, NBUCKET, ACT_NBUCKET, CCT_NBUCKET]

    
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
        Simulate with FTDD
    '''
    print("Simulating circuit with FTDD......")

    # t0c0
    signal.alarm(time_limit)
    try:
          # First time meas
        t1 = time.perf_counter()
        cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)
        cTN = PyTN_2_cTN(tn_lbl)
        ctdd = cTN.cont_TN(path_t0c0, False)
        t2 = time.perf_counter()
        dt = t2 - t1
          # Refine time meas
        if dt < perf_meas_time:
            N = min(ceil(perf_meas_time/dt), meas_max_iter)
            t1 = time.perf_counter()
            for i in range(N):
                cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)
                cTN = PyTN_2_cTN(tn_lbl)
                ctdd = cTN.cont_TN(path_t0c0, False)
            t2 = time.perf_counter()        
            dt = (t2 - t1)/N
        print("FTDD t0c0 simulation finished with time, ", dt, "s")
        list_ctdd_time_t0c0.append(dt)
        # log node number
        node_num = ctdd.node_number()
        print("FTDD t0c0 final node number is ", node_num)
        list_ctdd_node_t0c0.append(node_num)
        # log gc runs
        list_ctdd_gc_t0c0.append(cTDD.get_gc_runs())
    except TimeoutError:
        list_ctdd_time_t0c0.append('T.O.')
        list_ctdd_node_t0c0.append('T.O.')
        list_ctdd_gc_t0c0.append('T.O.')
        print("FTDD t0c0 simulation timed out!")
    except Exception as e:
        list_ctdd_time_t0c0.append('R.E.')
        list_ctdd_node_t0c0.append('R.E.')
        list_ctdd_gc_t0c0.append('R.E.')
        print(f"Caught an exception: {e}")
    finally:
        signal.alarm(0)

    # t0c1
    signal.alarm(time_limit)
    try:
          # First time meas
        t1 = time.perf_counter()
        cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)
        cTN = PyTN_2_cTN(tn_lbl)
        ctdd = cTN.cont_TN(path_t0c1, False)
        t2 = time.perf_counter()
        dt = t2 - t1
          # Refine time meas
        if dt < perf_meas_time:
            N = min(ceil(perf_meas_time/dt), meas_max_iter)
            t1 = time.perf_counter()
            for i in range(N):
                cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)
                cTN = PyTN_2_cTN(tn_lbl)
                ctdd = cTN.cont_TN(path_t0c1, False)
            t2 = time.perf_counter()        
            dt = (t2 - t1)/N
        print("FTDD t0c1 simulation finished with time, ", dt, "s")
        list_ctdd_time_t0c1.append(dt)
        # log node number
        node_num = ctdd.node_number()
        print("FTDD t0c1 final node number is ", node_num)
        list_ctdd_node_t0c1.append(node_num)
        # log gc runs
        list_ctdd_gc_t0c1.append(cTDD.get_gc_runs())
    except TimeoutError:
        list_ctdd_time_t0c1.append('T.O.')
        list_ctdd_node_t0c1.append('T.O.')
        list_ctdd_gc_t0c1.append('T.O.')
        print("FTDD t0c1 simulation timed out!")
    except Exception as e:
        list_ctdd_time_t0c1.append('R.E.')
        list_ctdd_node_t0c1.append('R.E.')
        list_ctdd_gc_t0c1.append('R.E.')
        print(f"Caught an exception: {e}")
    finally:
        signal.alarm(0)
    
    # t1c0
    signal.alarm(time_limit)
    try:
          # First time meas
        t1 = time.perf_counter()
        cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)
        cTN = PyTN_2_cTN(tn_tetris)
        ctdd = cTN.cont_TN(path_t1c0, False)
        t2 = time.perf_counter()
        dt = t2 - t1
          # Refine time meas
        if dt < perf_meas_time:
            N = min(ceil(perf_meas_time/dt), meas_max_iter)
            t1 = time.perf_counter()
            for i in range(N):
                cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)
                cTN = PyTN_2_cTN(tn_tetris)
                ctdd = cTN.cont_TN(path_t1c0, False)
            t2 = time.perf_counter()        
            dt = (t2 - t1)/N
        print("FTDD t1c0 simulation finished with time, ", dt, "s")
        list_ctdd_time_t1c0.append(dt)
        # log node number
        node_num = ctdd.node_number()
        print("FTDD t1c0 final node number is ", node_num)
        list_ctdd_node_t1c0.append(node_num)
        # log gc runs
        list_ctdd_gc_t1c0.append(cTDD.get_gc_runs())
    except TimeoutError:
        list_ctdd_time_t1c0.append('T.O.')
        list_ctdd_node_t1c0.append('T.O.')
        list_ctdd_gc_t1c0.append('T.O.')
        print("FTDD t1c0 simulation timed out!")
    except Exception as e:
        list_ctdd_time_t1c0.append('R.E.')
        list_ctdd_node_t1c0.append('R.E.')
        list_ctdd_gc_t1c0.append('R.E.')
        print(f"Caught an exception: {e}")
    finally:
        signal.alarm(0)
    
    # t1c1
    signal.alarm(time_limit)
    try:
          # First time meas
        t1 = time.perf_counter()
        cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)
        cTN = PyTN_2_cTN(tn_tetris)
        ctdd = cTN.cont_TN(path_t1c1, False)
        t2 = time.perf_counter()
        dt = t2 - t1
          # Refine time meas
        if dt < perf_meas_time:
            N = min(ceil(perf_meas_time/dt), meas_max_iter)
            t1 = time.perf_counter()
            for i in range(N):
                cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)
                cTN = PyTN_2_cTN(tn_tetris)
                ctdd = cTN.cont_TN(path_t1c1, False)
            t2 = time.perf_counter()        
            dt = (t2 - t1)/N
        print("FTDD t1c1 simulation finished with time, ", dt, "s")
        list_ctdd_time_t1c1.append(dt)
        # log node number
        node_num = ctdd.node_number()
        print("FTDD t1c1 final node number is ", node_num)
        list_ctdd_node_t1c1.append(node_num)
        # log gc runs
        list_ctdd_gc_t1c1.append(cTDD.get_gc_runs())
    except TimeoutError:
        list_ctdd_time_t1c1.append('T.O.')
        list_ctdd_node_t1c1.append('T.O.')
        list_ctdd_gc_t1c1.append('T.O.')
        print("FTDD t1c0 simulation timed out!")
    except Exception as e:
        list_ctdd_time_t1c1.append('R.E.')
        list_ctdd_node_t1c1.append('R.E.')
        list_ctdd_gc_t1c1.append('R.E.')
        print(f"Caught an exception: {e}")
    finally:
        signal.alarm(0)
    
    # Convert result to vector array for comparison with IBM
    if n <= qubit_num_limit and (not open_input) and (not error):
        state_ctdd = np.transpose(ctdd.to_array().reshape(tuple([2 for i in range(n)]))).flatten()

    print('')


    ''' 
        Verify FTDD against IBM Qiskit Aer
    '''
    if n <= qubit_num_limit and (not open_input) and (not error):
        print("FTDD vs. Qiskit quantum state difference is ", np.average(np.abs(state_ctdd - state_Aer)))
        fidelity = np.abs(np.inner(state_ctdd, state_Aer.conj()))
        print("FTDD vs. Qiskit fidelity is ", fidelity*100, "%")
        list_fidelity.append(fidelity)
    else:
        list_fidelity.append(1)

    print('\n')


''' Generate the benchmarking results and save to .csv '''
dict_bench = {
    "Circuit Name":                     list_circuit_name,
    "Number of Qubits":                 list_qubit_num,
    "Depth":                            list_depth,
    "Number of Gates":                  list_gate_num,

    "Aer CPU Time (s)":                 list_aer_time,

    "Tetris CPU Time (s)":              list_tetris_time,

    "FTDD baseline CPU Time (s)":       list_ctdd_time_t0c0,
    "FTDD baseline final node":         list_ctdd_node_t0c0,
    "FTDD baseline gc runs":            list_ctdd_gc_t0c0,

    "FTDD w/ Tetris CPU Time (s)":      list_ctdd_time_t1c0,
    "FTDD w/ Tetris final node":        list_ctdd_node_t1c0,
    "FTDD w/ Tetris gc runs":           list_ctdd_gc_t1c0,

    "FTDD w/ Cotengra CPU Time (s)":    list_ctdd_time_t0c1,
    "FTDD w/ Cotengra final node":      list_ctdd_node_t0c1,
    "FTDD w/ Cotengra gc runs":         list_ctdd_gc_t0c1,

    "FTDD w/ both CPU Time (s)":        list_ctdd_time_t1c1,
    "FTDD w/ both final node":          list_ctdd_node_t1c1,
    "FTDD w/ both gc runs":             list_ctdd_gc_t1c1,

    "FTDD w/ both fidelity":            list_fidelity   
}

res_path = "./BenchFTDD/data/FTDD/"
res_csv_name = (
            res_path
            + "BenchFTDD_" + case
            + ".csv"
        )
df_bench = pd.DataFrame(dict_bench)
df_bench.to_csv(res_csv_name)
