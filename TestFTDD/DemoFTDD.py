''' This file demonstrates FTDD with a quantum circuit '''
import sys
import numpy as np
import time

# Import Python Utilities
sys.path.append('./source/')
from TDD import Ini_TDD, get_count, get_unique_table_num
from TN import TensorNetwork, tdd_to_tensor
from TDD_Q import get_real_qubit_num, add_inputs, cir_2_tn_lbl, TNtoCotInput, squeezeTN, squeezeTN_ultra
from qiskit import QuantumCircuit

# Import Cotengra
import cotengra as ctg

# Import cTDD
sys.path.append('./source/cpp/build/')
import cTDD


'''
    Utility functions
'''
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


''' 
    Pick a quantum circuit for this demo 
'''
path = './Benchmarks/Verification/'
file_name = sys.argv[1]
cir = QuantumCircuit.from_qasm_file(path+file_name+'.qasm')
cir.draw('mpl').savefig("./CircuitDiagrams/"+ file_name + ".png")

print('\nQuantum circuit: ', file_name+'.qasm\n')


''' 
    Circuit-to-TN Transpilation 
'''
tn_lbl, all_indexs_lbl, depth = cir_2_tn_lbl(cir)
n = get_real_qubit_num(cir)


''' 
    Tetris-based Rank Simlification
'''
tensors_tetris = squeezeTN(tn_lbl.tensors, n, depth)
tensors_tetris = squeezeTN_ultra(tensors_tetris, n, depth)
tn_tetris = TensorNetwork(tensors_tetris, tn_lbl.tn_type, n)

# Add initial state tensors
input_s = [0]*n
if input_s:
    add_inputs(tn_lbl,input_s,n)
    add_inputs(tn_tetris,input_s,n)


'''
    Contraction Order Search with Cotengra
'''

# Set-up inputs for Cotengra
tensor_list_t0, open_indices_t0, size_dict_t0, arrays_t0, oe_input_t0 = TNtoCotInput(tn_lbl, n)
tensor_list_t1, open_indices_t1, size_dict_t1, arrays_t1, oe_input_t1 = TNtoCotInput(tn_tetris, n)

# Setup Cotengra Optimizers
opt = ctg.ReusableHyperOptimizer(
    minimize=f'combo-{56}',
    max_repeats=512,
    max_time=30,
    progbar=True,
    directory='./TestFTDD/cotengra_cache'
)

# Set-up for different optimizations
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
    Test PyTDD
'''
print("Test PyTDD, t0c0")

# Initialize PyTDD
tdd = Ini_TDD(all_indexs_lbl)

# Contract TN in PyTDD
t1 = time.perf_counter()
ptdd = tn_lbl.cont_TN(path_t0c0, False)
t2 = time.perf_counter()
dt = t2 - t1
print('PyTDD contraction finished with time ', dt, 's')

# PyTDD statistics
print("PyTDD result # nodes: ", ptdd.node_number())
print("PyTDD unique table size is: ", get_unique_table_num())
get_count()

print('\n')




'''
    Test FTDD
'''
print("Test FTDD, t1c1")

# cTDD Table parameters
load_factor = 1
alpha  = 2
beta = alpha * load_factor

NBUCKET = int(alpha * 2**n)
INITIAL_GC_LIMIT = int(beta * 2**n)
INITIAL_GC_LUR = 0.9
ACT_NBUCKET = 32768
CCT_NBUCKET = 32768
uniqTabConfig = [INITIAL_GC_LIMIT, INITIAL_GC_LUR, NBUCKET, ACT_NBUCKET, CCT_NBUCKET]

# Initialize cTDD
cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)

# Create cTDD tensor network
# cTN = PyTN_2_cTN(tn_lbl)
cTN = PyTN_2_cTN(tn_tetris)

# Contract TN in cTDD
t1 = time.perf_counter()
# ctdd = cTN.cont_TN(path_t0c0, False)
ctdd = cTN.cont_TN(path_t1c1, False)
t2 = time.perf_counter()
dt = t2 - t1
print('FTDD contraction finished with time ', dt, 's')

# cTDD statistics
print("FTDD result # nodes: ", ctdd.node_number())
print("FTDD unique table size is: ", cTDD.get_unique_table_num())
print(cTDD.get_count())

print('\n')


''' 
    Verify FTDD against PyTDD
'''
ptdd_ToTensor = np.transpose(ptdd.to_array())
ctdd_ToTensor = tdd_to_tensor(ctdd.to_array(), ptdd.index_set)
print("FTDD vs. PyTDD quantum state difference is ", np.average(np.abs(ptdd_ToTensor - ctdd_ToTensor)))
fidelity = np.abs(np.inner(ptdd_ToTensor.flatten(), ctdd_ToTensor.flatten().conj()))
print("FTDD vs. PyTDD fidelity is ", fidelity*100, "%")

print('\n')


''' 
    Demo get_amplitude()
'''
print("Demonstrate FTDD functionality for returning probability amplitude")

addr1 = [0] * 16
addr2 = [1] * 16

print("PyTDD result amplitude for addr1 is ", ptdd.get_amplitude(addr1.copy()))
print("FTDD result amplitude for addr1 is ", ctdd.get_amplitude(addr1.copy()))
print("PyTDD result amplitude for addr2 is ", ptdd.get_amplitude(addr2.copy()))
print("FTDD result amplitude for addr2 is ", ctdd.get_amplitude(addr2.copy()))

print('\n')


'''
    Demo measure()
'''
print("Demonstrate FTDD functionality for measuring samples")

string = '0'*n
string_int = [int(i) for i in string]
print("Theoretical probability for measuring ", string, " is ", abs(ptdd.get_amplitude(string_int))**2)

n_sample = 1000000

count_ptdd = 0
for i in range(n_sample):
    sample_ptdd = ptdd.measure()
    if sample_ptdd == string:
        count_ptdd += 1
print("PyTDD probability for measuring ", string, " is ", count_ptdd/n_sample)

ctdd.get_measure_prob()
count_ctdd = 0
for i in range(n_sample):
    sample_ctdd = ctdd.measure()
    if sample_ctdd == string:
        count_ctdd += 1
print("FTDD probability for measuring ", string, " is ", count_ctdd/n_sample)
