''' This file verifies FTDD against PyTDD and IBM Qiskit Aer '''
import sys
import os
import numpy as np
import time

# Import Python Utilities
sys.path.append('./source/')
from TDD import Ini_TDD, get_count, get_computed_table_num
from TN import TensorNetwork, tdd_to_tensor
from TDD_Q import get_real_qubit_num, add_inputs, cir_2_tn_lbl, TNtoCotInput, squeezeTN, squeezeTN_ultra
from qiskit import QuantumCircuit

# Import Qiskit AER
from qiskit import Aer, transpile

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


''' cTDD Unique Table parameters '''
n = 16
load_factor = 0.5
alpha  = 2
beta = alpha * load_factor

NBUCKET = int(alpha * 2**n)
INITIAL_GC_LIMIT = int(beta * 2**n)
INITIAL_GC_LUR = 0.9
ACT_NBUCKET = 16384
CCT_NBUCKET = 16384
uniqTabConfig = [INITIAL_GC_LIMIT, INITIAL_GC_LUR, NBUCKET, ACT_NBUCKET, CCT_NBUCKET]


''' Verify cTDD against PyTDD and IBM Qiskit Aer '''
path = './Benchmarks/Verification/'

# This round is for non-RQCs
for file_name in os.listdir(path):
    if '.qasm' not in file_name:
        continue

    if 'inst' in file_name:
        continue

    print("Verifying " + file_name + "......")
    cir = QuantumCircuit.from_qasm_file(path+file_name)

    ''' Python: Extract the TN from QASM '''
    tn_lbl, all_indexs_lbl, depth = cir_2_tn_lbl(cir)
    n = get_real_qubit_num(cir)

    ''' Apply Tetris-like Tensor Network Squeezing'''
    tensors_tetris = squeezeTN(tn_lbl.tensors, n, depth)
    tensors_tetris = squeezeTN_ultra(tensors_tetris, n, depth)
    tn_tetris = TensorNetwork(tensors_tetris, tn_lbl.tn_type, n)

    ''' Add input state '''
    input_s = [0]*n
    if input_s:
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
        directory='./TestFTDD/cotengra_cache'
    )

    ''' Set-up for different optimizations'''
      # Tetris = 0, Cotengra = 0
    path_t0c0 = tn_lbl.get_seq_path()
      # Tetris = 1, Cotengra = 0
    path_t1c0 = tn_tetris.get_seq_path()
      # Tetris = 1, Cotengra = 1
    tree_t1c1 = opt.search(tensor_list_t1, open_indices_t1, size_dict_t1)
    path_t1c1 = tree_t1c1.get_path()

    print('')


    ''' Simulate with AER '''
    print("Simulating circuit with IBM Qiskit Aer......")
      # Set Aer simulation backend
    aer_simulator = Aer.get_backend('aer_simulator')
    aer_simulator.set_options(precision='double')
      # Construct circuit from QASM
    cir_Aer = QuantumCircuit.from_qasm_file(path+file_name)
    cir_Aer.save_statevector()
    cir_Aer = transpile(cir_Aer, aer_simulator)
      # Simulate and get state vector
    result = aer_simulator.run(cir_Aer).result()
    statevector = result.get_statevector(cir_Aer)
    state_Aer = np.asarray(statevector)

    print('')


    ''' Dynamically adjust table parameters '''
    uniqTabConfig[0] = int(alpha * 2**n)
    uniqTabConfig[2] = int(beta * 2**n)


    ''' Simulate with PyTDD t0c0 '''
    print("Simulating circuit with PyTDD t0c0......")
      # Initialize PyTDD
    Ini_TDD(all_indexs_lbl)
      # Contract TN in PyTDD
    t1 = time.perf_counter()
    ptdd = tn_lbl.cont_TN(path_t0c0, False)
    t2 = time.perf_counter()
    dt = t2 - t1
    print('PyTDD contraction finished with time ', dt, 's')
      # PyTDD statistics
    get_count()
    print("Computed table size: ", get_computed_table_num())

    print('')

    ''' Simulate with cTDD t0c0 '''
    print("Simulating circuit with cTDD t0c0......")
      # Initialize cTDD
    cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)
      # Create cTDD tensor network
    cTN = PyTN_2_cTN(tn_lbl)
      # Contract TN in cTDD
    t1 = time.perf_counter()
    ctdd = cTN.cont_TN(path_t0c0, False)
    t2 = time.perf_counter()
    dt = t2 - t1
    print('cTDD contraction finished with time ', dt, 's')
      # cTDD statistics
    print(cTDD.get_count())
    print("Add computed table size: ", cTDD.get_add_computed_table_num())
    print("Cont computed table size: ", cTDD.get_cont_computed_table_num())

    print('')

    ''' Compare the state vector from TDD and the one from Aer '''
    print("Comparing t0c0 cTDD results against PyTDD and IBM Qiskit Aer......")
      
      # Verify cTDD statistics vs. PyTDD statistics
    if ptdd.node_number() != ctdd.node_number():
        print("Error: Node numbers of results are not equal!")
    
      # Convert cTDD and PyTDD results to array
    ptdd_ToTensor = np.transpose(ptdd.to_array()) # ptdd in tensor, normal variable order
    ptdd_ToArray = ptdd.to_array().flatten() # ptdd in vector, reversed variable order
    ctdd_ToTensor = tdd_to_tensor(ctdd.to_array(), ptdd.index_set) # ctdd in tensor, normal variable order
    ctdd_ToArray = np.transpose(ctdd_ToTensor).flatten() # ctdd in vector, reversed variable order
      
      # Numerically verify cTDD against PyTDD
    print("cTDD vs. PyTDD quantum state difference is ", np.average(np.abs(ptdd_ToTensor - ctdd_ToTensor)))
    fidelity = np.abs(np.inner(ptdd_ToArray, ctdd_ToArray.conj()))
    print("cTDD vs. PyTDD fidelity is ", fidelity*100, "%")
      
      # Numerically verify cTDD against IBM Qiskit Aer
    print("cTDD vs. Qiskit quantum state difference is ", np.average(np.abs(ptdd_ToArray - state_Aer)))
    fidelity = np.abs(np.inner(ptdd_ToArray, state_Aer.conj()))
    print("cTDD vs. Qiskit fidelity is ", fidelity*100, "%")

    print('\n')


    ''' Simulate with PyTDD t1c1 '''
    print("Simulating circuit with PyTDD t1c1......")
      # Initialize PyTDD
    Ini_TDD(all_indexs_lbl)
      # Contract TN in PyTDD
    t1 = time.perf_counter()
    ptdd = tn_tetris.cont_TN(path_t1c1, False)
    t2 = time.perf_counter()
    dt = t2 - t1
    print('PyTDD contraction finished with time ', dt, 's')
      # PyTDD statistics
    get_count()
    print("Computed table size: ", get_computed_table_num())

    print('')

    ''' Simulate with cTDD t1c1 '''
    print("Simulating circuit with cTDD t1c1......")
      # Initialize cTDD
    cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)
      # Create cTDD tensor network
    cTN = PyTN_2_cTN(tn_tetris)
      # Contract TN in cTDD
    t1 = time.perf_counter()
    ctdd = cTN.cont_TN(path_t1c1, False)
    t2 = time.perf_counter()
    dt = t2 - t1
    print('cTDD contraction finished with time ', dt, 's')
      # cTDD statistics
    print(cTDD.get_count())
    print("Add computed table size: ", cTDD.get_add_computed_table_num())
    print("Cont computed table size: ", cTDD.get_cont_computed_table_num())

    print('')

    ''' Compare the state vector from TDD and the one from Aer '''
    print("Comparing t1c1 cTDD results against PyTDD and IBM Qiskit Aer......")
      
      # Verify cTDD statistics vs. PyTDD statistics
    if ptdd.node_number() != ctdd.node_number():
        print("Error: Node numbers of results are not equal!")

      # Convert cTDD and PyTDD results to array
    ptdd_ToTensor = np.transpose(ptdd.to_array()) # ptdd in tensor, normal variable order
    ptdd_ToArray = ptdd.to_array().flatten() # ptdd in vector, reversed variable order
    ctdd_ToTensor = tdd_to_tensor(ctdd.to_array(), ptdd.index_set) # ctdd in tensor, normal variable order
    ctdd_ToArray = np.transpose(ctdd_ToTensor).flatten() # ctdd in vector, reversed variable order
      
      # Numerically verify cTDD against PyTDD
    print("cTDD vs. PyTDD quantum state difference is ", np.average(np.abs(ptdd_ToTensor - ctdd_ToTensor)))
    fidelity = np.abs(np.inner(ptdd_ToArray, ctdd_ToArray.conj()))
    print("cTDD vs. PyTDD fidelity is ", fidelity*100, "%")
      
      # Numerically verify cTDD against IBM Qiskit Aer
    print("cTDD vs. Qiskit quantum state difference is ", np.average(np.abs(ptdd_ToArray - state_Aer)))
    fidelity = np.abs(np.inner(ptdd_ToArray, state_Aer.conj()))
    print("cTDD vs. Qiskit fidelity is ", fidelity*100, "%")

    print('\n\n')


# This round is for RQCs
for file_name in os.listdir(path):
    if '.qasm' not in file_name:
        continue

    if 'inst' not in file_name:
        continue

    print("Verifying " + file_name + "......")
    cir = QuantumCircuit.from_qasm_file(path+file_name)

    ''' Python: Extract the TN from QASM '''
    tn_lbl, all_indexs_lbl, depth = cir_2_tn_lbl(cir)
    n = get_real_qubit_num(cir)

    ''' Apply Tetris-like Tensor Network Squeezing'''
    tensors_tetris = squeezeTN(tn_lbl.tensors, n, depth)
    tensors_tetris = squeezeTN_ultra(tensors_tetris, n, depth)
    tn_tetris = TensorNetwork(tensors_tetris, tn_lbl.tn_type, n)

    ''' Add input state '''
    input_s = [0]*n
    if input_s:
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
        directory='./TestFTDD/cotengra_cache'
    )

    ''' Set-up for different optimizations'''
      # Tetris = 0, Cotengra = 0
    path_t0c0 = tn_lbl.get_seq_path()
      # Tetris = 1, Cotengra = 0
    path_t1c0 = tn_tetris.get_seq_path()
      # Tetris = 1, Cotengra = 1
    tree_t1c1 = opt.search(tensor_list_t1, open_indices_t1, size_dict_t1)
    path_t1c1 = tree_t1c1.get_path()

    print('')


    ''' Simulate with AER '''
    print("Simulating circuit with IBM Qiskit Aer......")
      # Set Aer simulation backend
    aer_simulator = Aer.get_backend('aer_simulator')
    aer_simulator.set_options(precision='double')
      # Construct circuit from QASM
    cir_Aer = QuantumCircuit.from_qasm_file(path+file_name)
    cir_Aer.save_statevector()
    cir_Aer = transpile(cir_Aer, aer_simulator)
      # Simulate and get state vector
    result = aer_simulator.run(cir_Aer).result()
    statevector = result.get_statevector(cir_Aer)
    state_Aer = np.asarray(statevector)

    print('')


    ''' Dynamically adjust table parameters '''
    uniqTabConfig[0] = int(alpha * 2**n)
    uniqTabConfig[2] = int(beta * 2**n)


    ''' Simulate with PyTDD t0c0 '''
    print("Simulating circuit with PyTDD t0c0......")
      # Initialize PyTDD
    Ini_TDD(all_indexs_lbl)
      # Contract TN in PyTDD
    t1 = time.perf_counter()
    ptdd = tn_lbl.cont_TN(path_t0c0, False)
    t2 = time.perf_counter()
    dt = t2 - t1
    print('PyTDD contraction finished with time ', dt, 's')
      # PyTDD statistics
    get_count()
    print("Computed table size: ", get_computed_table_num())

    print('')

    ''' Simulate with cTDD t0c0 '''
    print("Simulating circuit with cTDD t0c0......")
      # Initialize cTDD
    cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)
      # Create cTDD tensor network
    cTN = PyTN_2_cTN(tn_lbl)
      # Contract TN in cTDD
    t1 = time.perf_counter()
    ctdd = cTN.cont_TN(path_t0c0, False)
    t2 = time.perf_counter()
    dt = t2 - t1
    print('cTDD contraction finished with time ', dt, 's')
      # cTDD statistics
    print(cTDD.get_count())
    print("Add computed table size: ", cTDD.get_add_computed_table_num())
    print("Cont computed table size: ", cTDD.get_cont_computed_table_num())

    print('')

    ''' Compare the state vector from TDD and the one from Aer '''
    print("Comparing t0c0 cTDD results against PyTDD and IBM Qiskit Aer......")
      # Verify cTDD statistics vs. PyTDD statistics
    if ptdd.node_number() != ctdd.node_number():
        print("Error: Node numbers of results are not equal!")

      # Convert cTDD and PyTDD results to array
    ptdd_ToTensor = np.transpose(ptdd.to_array()) # ptdd in tensor, normal variable order
    ptdd_ToArray = ptdd.to_array().flatten() # ptdd in vector, reversed variable order
    ctdd_ToTensor = tdd_to_tensor(ctdd.to_array(), ptdd.index_set) # ctdd in tensor, normal variable order
    ctdd_ToArray = np.transpose(ctdd_ToTensor).flatten() # ctdd in vector, reversed variable order
      
      # Numerically verify cTDD against PyTDD
    print("cTDD vs. PyTDD quantum state difference is ", np.average(np.abs(ptdd_ToTensor - ctdd_ToTensor)))
    fidelity = np.abs(np.inner(ptdd_ToArray, ctdd_ToArray.conj()))
    print("cTDD vs. PyTDD fidelity is ", fidelity*100, "%")
      
      # Numerically verify cTDD against IBM Qiskit Aer
    print("cTDD vs. Qiskit quantum state difference is ", np.average(np.abs(ptdd_ToArray - state_Aer)))
    fidelity = np.abs(np.inner(ptdd_ToArray, state_Aer.conj()))
    print("cTDD vs. Qiskit fidelity is ", fidelity*100, "%")

    print('\n')


    ''' Simulate with PyTDD t1c1 '''
    print("Simulating circuit with PyTDD t1c1......")
      # Initialize PyTDD
    Ini_TDD(all_indexs_lbl)
      # Contract TN in PyTDD
    t1 = time.perf_counter()
    ptdd = tn_tetris.cont_TN(path_t1c1, False)
    t2 = time.perf_counter()
    dt = t2 - t1
    print('PyTDD contraction finished with time ', dt, 's')
      # PyTDD statistics
    get_count()
    print("Computed table size: ", get_computed_table_num())

    print('')

    ''' Simulate with cTDD t1c1 '''
    print("Simulating circuit with cTDD t1c1......")
      # Initialize cTDD
    cTDD.Ini_TDD(all_indexs_lbl, uniqTabConfig, False)
      # Create cTDD tensor network
    cTN = PyTN_2_cTN(tn_tetris)
      # Contract TN in cTDD
    t1 = time.perf_counter()
    ctdd = cTN.cont_TN(path_t1c1, False)
    t2 = time.perf_counter()
    dt = t2 - t1
    print('cTDD contraction finished with time ', dt, 's')
      # cTDD statistics
    print(cTDD.get_count())
    print("Add computed table size: ", cTDD.get_add_computed_table_num())
    print("Cont computed table size: ", cTDD.get_cont_computed_table_num())

    print('')

    ''' Compare the state vector from TDD and the one from Aer '''
    print("Comparing t1c1 cTDD results against PyTDD and IBM Qiskit Aer......")
      # Verify cTDD statistics vs. PyTDD statistics
    if ptdd.node_number() != ctdd.node_number():
        print("Error: Node numbers of results are not equal!")
          
      # Convert cTDD and PyTDD results to array
    ptdd_ToTensor = np.transpose(ptdd.to_array()) # ptdd in tensor, normal variable order
    ptdd_ToArray = ptdd.to_array().flatten() # ptdd in vector, reversed variable order
    ctdd_ToTensor = tdd_to_tensor(ctdd.to_array(), ptdd.index_set) # ctdd in tensor, normal variable order
    ctdd_ToArray = np.transpose(ctdd_ToTensor).flatten() # ctdd in vector, reversed variable order
      
      # Numerically verify cTDD against PyTDD
    print("cTDD vs. PyTDD quantum state difference is ", np.average(np.abs(ptdd_ToTensor - ctdd_ToTensor)))
    fidelity = np.abs(np.inner(ptdd_ToArray, ctdd_ToArray.conj()))
    print("cTDD vs. PyTDD fidelity is ", fidelity*100, "%")
      
      # Numerically verify cTDD against IBM Qiskit Aer
    print("cTDD vs. Qiskit quantum state difference is ", np.average(np.abs(ptdd_ToArray - state_Aer)))
    fidelity = np.abs(np.inner(ptdd_ToArray, state_Aer.conj()))
    print("cTDD vs. Qiskit fidelity is ", fidelity*100, "%")

    print('\n\n')
