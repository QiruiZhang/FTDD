'''
Original code from TDD (https://github.com/Veriqc/TDD)

Modifications by Qirui Zhang (qiruizh@umich.edu) for FTDD (https://github.com/QiruiZhang/FTDD)
    - Fixed a bug in the original cir_2_tn() function. See line #125
    - Line #232 and beyond
'''

import numpy as np
from TN import Index,Tensor,TensorNetwork, HyperEdgeReduced, contTensor
from qiskit.quantum_info.operators import Operator
from qiskit.converters import circuit_to_dag, dag_to_circuit

def is_diagonal(U):
    i, j = np.nonzero(U)
    return np.all(i == j)

def add_hyper_index(var_list,hyper_index):
    for var in var_list:
        if not var in hyper_index:
            hyper_index[var]=0

def reshape(U):
    if U.shape==(1,1):
        return U
    
    if U.shape[0]==U.shape[1]:
        split_U=np.split(U,2,1)
    else:
        split_U=np.split(U,2,0)
    split_U[0]=reshape(split_U[0])
    split_U[1]=reshape(split_U[1]) 
    return np.array([split_U])[0]

def get_real_qubit_num(cir):
    """Calculate the real number of qubits of a circuit"""
    gates=cir.data
    q=0
    for k in range(len(gates)):
        q=max(q,max([qbit.index for qbit in gates[k][1]]))
    return q+1

def cir_2_tn(cir,input_s=[],output_s=[]):
    """return the dict that link every quantum gate to the corresponding index"""
    
    hyper_index=dict() 
    qubits_index = dict()
    start_tensors= dict()
    end_tensors = dict()
    
    qubits_num=get_real_qubit_num(cir)
    for k in range(qubits_num):
        qubits_index[k]=0
        
    tn=TensorNetwork([],tn_type='cir',qubits_num=qubits_num)
        
    if input_s:
        U0=np.array([1,0])
        U1=np.array([0,1])
        for k in range(qubits_num):
            if input_s[k]==0:
                ts=Tensor(U0,[Index('x'+str(k))],'in',[k])
            elif input_s[k]==1:
                ts=Tensor(U1,[Index('x'+str(k))],'in',[k])
            else:
                print('Only support computational basis input')
            tn.tensors.append(ts)

    gates=cir.data
    for k in range(len(gates)):
        g=gates[k]
        nam=g[0].name
        q = [q.index for q in g[1]]

        var=[]
        ts=Tensor([],[],nam,q)
        U=Operator(g[0]).data

        if nam=='cx':
            U=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
            U=reshape(U)
            ts.data=U

            var_con='x'+ str(q[0])+'_'+str(qubits_index[q[0]])
            var_tar_in='x'+ str(q[1])+'_'+str(qubits_index[q[1]])
            var_tar_out='x'+ str(q[1])+'_'+str(qubits_index[q[1]]+1)
            add_hyper_index([var_con,var_tar_in,var_tar_out],hyper_index)
            var+=[Index(var_con,hyper_index[var_con]),Index(var_con,hyper_index[var_con]+1),Index(var_tar_in,hyper_index[var_tar_in]),Index(var_tar_out,hyper_index[var_tar_out])]
            
            if qubits_index[q[0]]==0 and hyper_index[var_con]==0:
                start_tensors[q[0]]=ts
            if qubits_index[q[1]]==0 and hyper_index[var_tar_in]==0:
                start_tensors[q[1]]=ts
            end_tensors[q[0]]=ts
            end_tensors[q[1]]=ts
            hyper_index[var_con]+=1
            qubits_index[q[1]]+=1   

            ts.index_set=var
            tn.tensors.append(ts)
        elif is_diagonal(U):
            if len(q)>1:
                U=reshape(U)
            ts.data=U
            
            for k in q:
                var_in='x'+ str(k)+'_'+str(qubits_index[k])
                add_hyper_index([var_in],hyper_index)
                var+=[Index(var_in,hyper_index[var_in]),Index(var_in,hyper_index[var_in]+1)]

                if qubits_index[k]==0 and hyper_index[var_in]==0:
                    start_tensors[k]=ts
                end_tensors[k]=ts             
                hyper_index[var_in]+=1
            
            ts.index_set=var
            tn.tensors.append(ts)
        else:
            ''' 
            The original code here has a bug:
                QASM and QISKIT data comes as matrices with rows being output indices and columns being input indices
                For >= 2-qubit gates, reshape() recognizes that and will convert the matrix to be a tensor in the index order of
                [qi0, qo0, qi1, qo1, ...]. For 1-qubit gates, TDD still uses the [qi0, qo0] order by default, but QISKIT assumes
                [qo0, qi0] for indexing. So, if we take the QISKIT matrix directly as a tensor and use [qi0, qo0] to index it, 
                we will be essentially transposing the matrix, which is incorrect. And we will create TDDs that are also not correct, 
                essentially the TDDs for the transposed operation matrix. For most gates, as they happen to be symmetric (note, not
                hermitian), that is not a problem. But, for gates like Y, and U3, that is making the QCS give wrong results.

            if len(q)>1:
                U=reshape(U)
            ts.data=U
            '''
            # Above Bug Fixed:
            U=reshape(U)
            if len(q) == 1:
                U = U[:,:,0,0]
            ts.data=U

            for k in q:
                var_in='x'+ str(k)+'_'+str(qubits_index[k])
                var_out='x'+ str(k)+'_'+str(qubits_index[k]+1)
                add_hyper_index([var_in,var_out],hyper_index)
                var+=[Index(var_in,hyper_index[var_in]),Index(var_out,hyper_index[var_out])]

                if qubits_index[k]==0 and hyper_index[var_in]==0:
                    start_tensors[k]=ts
                end_tensors[k]=ts                
                qubits_index[k]+=1

            ts.index_set=var
            tn.tensors.append(ts)          

    for k in range(qubits_num):
        if k in start_tensors:
            last1=Index('x'+str(k)+'_'+str(0),0)
            new1=Index('x'+str(k),0)            
            start_tensors[k].index_set[start_tensors[k].index_set.index(last1)]=new1
        
        if k in end_tensors:
            last2=Index('x'+str(k)+'_'+str(qubits_index[k]),hyper_index['x'+str(k)+'_'+str(qubits_index[k])])
            new2=Index('y'+str(k),0)            
            end_tensors[k].index_set[end_tensors[k].index_set.index(last2)]=new2

    for k in range(qubits_num):
        U=np.eye(2)
        if qubits_index[k]==0 and not 'x'+str(k)+'_'+str(0) in hyper_index:
            var_in='x'+str(k)
            var=[Index('x'+str(k),0),Index('y'+str(k),0)]
            ts=Tensor(U,var,'nu_q',[k])
            tn.tensors.append(ts)

    if output_s:
        U0=np.array([1,0])
        U1=np.array([0,1])
        for k in range(qubits_num):
            if input_s[k]==0:
                ts=Tensor(U0,[Index('y'+str(k))],'out',[k])
            elif input_s[k]==1:
                ts=Tensor(U1,[Index('y'+str(k))],'out',[k])
            else:
                print('Only support computational basis output')
            tn.tensors.append(ts)
    
    all_indexs=[]
    for k in range(qubits_num):
        all_indexs.append('x'+str(k))
        for k1 in range(qubits_index[k]+1): 
            all_indexs.append('x'+str(k)+'_'+str(k1))
        all_indexs.append('y'+str(k))
    
    return tn,all_indexs

def add_inputs(tn,input_s,qubits_num):
    U0=np.array([1,0])
    U1=np.array([0,1])
    if len(input_s)!= qubits_num:
        print("inputs is not match qubits number")
        return 
    for k in range(qubits_num-1,-1,-1):
        if input_s[k]==0:
            ts=Tensor(U0,[Index('x'+str(k))],'in',[k], 0)
        elif input_s[k]==1:
            ts=Tensor(U1,[Index('x'+str(k))],'in',[k], 0)
        else:
            print('Only support computational basis input')
        tn.tensors.insert(0,ts)
            
def add_outputs(tn,output_s,qubits_num, depth=0):
    U0=np.array([1,0])
    U1=np.array([0,1])
    if len(output_s)!= qubits_num:
        print("outputs is not match qubits number")
        return 
    for k in range(qubits_num):
        if output_s[k]==0:
            ts=Tensor(U0,[Index('y'+str(k))],'out',[k], depth+1)
        elif output_s[k]==1:
            ts=Tensor(U1,[Index('y'+str(k))],'out',[k], depth+1)
        else:
            print('Only support computational basis output')
        tn.tensors.append(ts)       

def add_trace_line(tn,qubits_num):
    U=np.eye(2)
    for k in range(qubits_num-1,-1,-1):
        var_in='x'+str(k)
        var=[Index('x'+str(k),0),Index('y'+str(k),0)]
        ts=Tensor(U,var,'tr',[k])
        tn.tensors.insert(0,ts)


''' 
    Below are functions added by Qirui Zhang (qiruizh@umich.edu) for FTDD (https://github.com/QiruiZhang/FTDD) 
'''

def print_gate(g): 
    nam=g[0].name
    q = [q.index for q in g[1]]
    print('Gate ' + nam + ' on qubits ' + str(q))

''' Transpile QASM into a TN in the sequential order (qubit by qubit and layer by layer) '''
def cir_2_tn_lbl(cir,input_s=[],output_s=[]):
    
    hyper_index=dict() 
    qubits_index = dict()
    start_tensors= dict()
    end_tensors = dict()
    
    ''' Get qubit number and initialize qubits_index '''
    qubits_num=get_real_qubit_num(cir)
    for k in range(qubits_num):
        qubits_index[k]=0
        
    ''' Create an empty tensor network for the circuit '''
    tn=TensorNetwork([],tn_type='cir',qubits_num=qubits_num)
        
    if input_s:
        U0=np.array([1,0])
        U1=np.array([0,1])
        for k in range(qubits_num):
            if input_s[k]==0:
                ts=Tensor(U0,[Index('x'+str(k))],'in',[k], 0)
            elif input_s[k]==1:
                ts=Tensor(U1,[Index('x'+str(k))],'in',[k], 0)
            else:
                print('Only support computational basis input')
            tn.tensors.append(ts)

    ''' Convert circuit to a DAG to be later parsed layer by layer '''
    dag = circuit_to_dag(cir)
    k_layer = 0

    ''' Add gates to the TN layer by layer '''
    for layer in dag.layers():
        k_layer += 1
        cir_layer = dag_to_circuit(layer['graph'])
        gates = cir_layer.data
        for k in range(len(gates)):
            g=gates[k]
            nam=g[0].name
            q = [q.index for q in g[1]]

            var=[]
            ts=Tensor([],[],nam,q, k_layer)
            U=Operator(g[0]).data

            if nam=='cx':
                U=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
                U=reshape(U)
                ts.data=U

                var_con='x'+ str(q[0])+'_'+str(qubits_index[q[0]])
                var_tar_in='x'+ str(q[1])+'_'+str(qubits_index[q[1]])
                var_tar_out='x'+ str(q[1])+'_'+str(qubits_index[q[1]]+1)
                add_hyper_index([var_con,var_tar_in,var_tar_out],hyper_index)
                var+=[Index(var_con,hyper_index[var_con]),Index(var_con,hyper_index[var_con]+1),Index(var_tar_in,hyper_index[var_tar_in]),Index(var_tar_out,hyper_index[var_tar_out])]
                
                if qubits_index[q[0]]==0 and hyper_index[var_con]==0:
                    start_tensors[q[0]]=ts
                if qubits_index[q[1]]==0 and hyper_index[var_tar_in]==0:
                    start_tensors[q[1]]=ts
                end_tensors[q[0]]=ts
                end_tensors[q[1]]=ts
                hyper_index[var_con]+=1
                qubits_index[q[1]]+=1   

                ts.index_set=var
                tn.tensors.append(ts)
            elif is_diagonal(U):
                if len(q)>1:
                    U=reshape(U)
                ts.data=U
                
                for k in q:
                    var_in='x'+ str(k)+'_'+str(qubits_index[k])
                    add_hyper_index([var_in],hyper_index)
                    var+=[Index(var_in,hyper_index[var_in]),Index(var_in,hyper_index[var_in]+1)]

                    if qubits_index[k]==0 and hyper_index[var_in]==0:
                        start_tensors[k]=ts
                    end_tensors[k]=ts             
                    hyper_index[var_in]+=1
                
                ts.index_set=var
                tn.tensors.append(ts)
            else:
                # See the original cir_2_tn function for a bug (fixed) that used to be here:
                U=reshape(U)
                if len(q) == 1:
                    U = U[:,:,0,0]
                ts.data=U

                for k in q:
                    var_in='x'+ str(k)+'_'+str(qubits_index[k])
                    var_out='x'+ str(k)+'_'+str(qubits_index[k]+1)
                    add_hyper_index([var_in,var_out],hyper_index)
                    var+=[Index(var_in,hyper_index[var_in]),Index(var_out,hyper_index[var_out])]

                    if qubits_index[k]==0 and hyper_index[var_in]==0:
                        start_tensors[k]=ts
                    end_tensors[k]=ts                
                    qubits_index[k]+=1

                ts.index_set=var
                tn.tensors.append(ts)         

    for k in range(qubits_num):
        if k in start_tensors:
            last1=Index('x'+str(k)+'_'+str(0),0)
            new1=Index('x'+str(k),0)            
            start_tensors[k].index_set[start_tensors[k].index_set.index(last1)]=new1
        
        if k in end_tensors:
            last2=Index('x'+str(k)+'_'+str(qubits_index[k]),hyper_index['x'+str(k)+'_'+str(qubits_index[k])])
            new2=Index('y'+str(k),0)            
            end_tensors[k].index_set[end_tensors[k].index_set.index(last2)]=new2

    for k in range(qubits_num):
        U=np.eye(2)
        if qubits_index[k]==0 and not 'x'+str(k)+'_'+str(0) in hyper_index:
            var_in='x'+str(k)
            var=[Index('x'+str(k),0),Index('y'+str(k),0)]
            ts=Tensor(U,var,'nu_q',[k], 1)
            tn.tensors.append(ts)

    if output_s:
        U0=np.array([1,0])
        U1=np.array([0,1])
        for k in range(qubits_num):
            if input_s[k]==0:
                ts=Tensor(U0,[Index('y'+str(k))],'out',[k], k_layer+1)
            elif input_s[k]==1:
                ts=Tensor(U1,[Index('y'+str(k))],'out',[k], k_layer+1)
            else:
                print('Only support computational basis output')
            tn.tensors.append(ts)
    
    all_indexs=[]
    for k in range(qubits_num):
        all_indexs.append('x'+str(k))
        for k1 in range(qubits_index[k]+1): 
            all_indexs.append('x'+str(k)+'_'+str(k1))
        all_indexs.append('y'+str(k))
    
    return tn,all_indexs, k_layer

''' This function converts GRCS circuits in .txt files to QASM files '''
def grcs2qasm(grcs_file, qasm_file, bubble=False):
    # Create file I/Os
    file_in = open(grcs_file, 'r')
    file_out = open(qasm_file, 'w')

    # Read in GRCS as a whole
    grcs = file_in.readlines()

    # Write QASM header
    file_out.write('OPENQASM 2.0;\n')
    file_out.write('include "qelib1.inc";\n')

    # Specifiy qubit and cbit registers
    qubits_num = grcs[0][:-1]
    file_out.write('qreg q[' + qubits_num + '];\n')
    file_out.write('creg c[' + qubits_num + '];\n')

    # Write the circuit
    cycle_prev = 0
    qubits_involved = [0]*int(qubits_num)
    for k in range(1, len(grcs)):
        line = grcs[k][:-1].split(' ')

        cycle_next = int(line[0])
        name_grcs = line[1]
        qubits_grcs = line[2:]

        if cycle_next != cycle_prev:
            # Check which qubits are not involved in the previous layer and assign them an identity gate
            for q in range(int(qubits_num)):
                if (qubits_involved[q] != 1) and bubble:
                    file_out.write('id q[' + str(q) + '];\n')
            # Reset qubit involvement
            qubits_involved = [0]*int(qubits_num)
            file_out.write('\n')
        cycle_prev = cycle_next

        # Update qubit involvement for the current layer
        for i in qubits_grcs:
            qubits_involved[int(i)] = 1

        if name_grcs == 'cz':
            name_qasm = 'cz'
            qubits_qasm = 'q[' + qubits_grcs[0] +'],q[' + qubits_grcs[1] + ']'
        elif name_grcs == 't':
            name_qasm = 't'
            qubits_qasm = 'q[' + qubits_grcs[0] +']'
        elif name_grcs == 'h':
            name_qasm = 'h'
            qubits_qasm = 'q[' + qubits_grcs[0] +']'
        elif name_grcs == 'x_1_2':
            name_qasm = 'rx(pi*0.5)'
            qubits_qasm = 'q[' + qubits_grcs[0] +']'
        elif name_grcs == 'y_1_2':
            name_qasm = 'ry(pi*0.5)'
            qubits_qasm = 'q[' + qubits_grcs[0] +']'
        else:
            print("Error: Invalid qrcs gate!")
            return
        
        file_out.write(name_qasm + ' ' + qubits_qasm + ';\n')

''' This function convert TDD tensor network to input format for Cotengra, and considers hyper-edges '''
def TNtoCotInput(tn_lbl, n=0, prnt=False):
    tensor_list = []
    arrays = []
    oe_input = []
    size_dict = {}
    for ts in tn_lbl.tensors:
        # Reduce hyper-edges for each tensor
        indices, ts_data = HyperEdgeReduced(ts)

        # Size dictionary
        for ind in indices:
            if ind not in size_dict:
                size_dict[ind] = 2
        
        # Input for Cotengra
        tensor_list.append(indices)
        arrays.append(ts_data)

        # Input for opt_einsum
        oe_input.append(ts_data)
        oe_input.append(indices)
        
        # Print
        if prnt:
            print(ts.name)
            print(indices)
            print(ts_data.shape)
            print('\n')

    # Output indices
    open_indices = tuple(['y'+str(i) for i in range(n-1, -1, -1)])

    return tensor_list, open_indices, size_dict, arrays, oe_input

''' This function convert TDD tensor network to input format for Cotengra, and do not consider hyper-edges '''
def TNtoCotInput2(tn_lbl, n=0, prnt=False):
    tensor_list = []
    arrays = []
    oe_input = []
    size_dict = {}
    for ts in tn_lbl.tensors:
        # Reduce hyper-edges for each tensor
        ts_data = np.squeeze(ts.data)
        indices = tuple([ind.key + '_' + str(ind.idx) for ind in ts.index_set ])

        # Size dictionary
        for ind in indices:
            if ind not in size_dict:
                size_dict[ind] = 2
        
        # Input for Cotengra
        tensor_list.append(indices)
        arrays.append(ts_data)

        # Input for opt_einsum
        oe_input.append(ts_data)
        oe_input.append(indices)
        
        # Print
        if prnt:
            print(ts.name)
            print(indices)
            print(ts_data.shape)
            print('\n')

    # Output indices
    open_indices = tuple(['y'+str(i)+'_0' for i in range(n-1, -1, -1)])

    return tensor_list, open_indices, size_dict, arrays, oe_input

''' This function performs the Tetris-like TN rank simplification for single-qubit gates '''
def squeezeTN(tensors, qubit_num, depth, prnt=False):
    ''' Initialize the Tetris stack, one for each qubit line '''
    tetris_stack = [[] for i in range(qubit_num)]

    ''' Now build the Tetris stack, round-1: merge all the single-qubit gates into adjacent two-qubit gates '''
    for ts in tensors:
        if prnt:
            print('\n\n')
            ts.printTensor()

        # single-qubit gates
        if (len(ts.qubits) == 1): 
            # stack for the target qubit is not empty
            if tetris_stack[ts.qubits[0]]: 
                # Contract it with the stack top (popped), then push the new tensor back
                stack_top = tetris_stack[ts.qubits[0]][-1]
                stack_top_new = contTensor(stack_top, ts)
                for qubit in stack_top.qubits:
                    pos = tetris_stack[qubit].index(stack_top)
                    tetris_stack[qubit].pop(pos)
                    tetris_stack[qubit].insert(pos, stack_top_new)
            # stack is empty, just push the tensor
            else: 
                tetris_stack[ts.qubits[0]].append(ts)
        # two-qubit gates
        elif (len(ts.qubits) == 2):
            # stack for neither qubit is empty
            if tetris_stack[ts.qubits[0]] and tetris_stack[ts.qubits[1]]: 
                stack_top_0 = tetris_stack[ts.qubits[0]][-1]
                stack_top_1 = tetris_stack[ts.qubits[1]][-1]
                # if both stack_top are single-qubit gates
                if (len(stack_top_0.qubits) == 1) and (len(stack_top_1.qubits) == 1):
                    stack_top_new = contTensor(stack_top_0, ts)
                    stack_top_new = contTensor(stack_top_1, stack_top_new)
                    # Update stack of 1st qubit
                    for qubit in stack_top_0.qubits:
                        pos = tetris_stack[qubit].index(stack_top_0)
                        tetris_stack[qubit].pop(pos)
                        tetris_stack[qubit].insert(pos, stack_top_new)
                    # Update stack of 2nd qubit
                    for qubit in stack_top_1.qubits:
                        pos = tetris_stack[qubit].index(stack_top_1)
                        tetris_stack[qubit].pop(pos)
                        tetris_stack[qubit].insert(pos, stack_top_new)
                # if only the 1st stack_top is single-qubit gate
                elif (len(stack_top_0.qubits) == 1):
                    stack_top_new = contTensor(stack_top_0, ts)
                    # Update stack of 1st qubit
                    for qubit in stack_top_0.qubits:
                        pos = tetris_stack[qubit].index(stack_top_0)
                        tetris_stack[qubit].pop(pos)
                        tetris_stack[qubit].insert(pos, stack_top_new)    
                    # Update stack of 2nd qubit
                    tetris_stack[ts.qubits[1]].append(stack_top_new)
                # if only the 2nd stack_top is single-qubit gate
                elif (len(stack_top_1.qubits) == 1):
                    stack_top_new = contTensor(stack_top_1, ts)
                    # Update stack of 1st qubit
                    for qubit in stack_top_1.qubits:
                        pos = tetris_stack[qubit].index(stack_top_1)
                        tetris_stack[qubit].pop(pos)
                        tetris_stack[qubit].insert(pos, stack_top_new)    
                    # Update stack of 2nd qubit
                    tetris_stack[ts.qubits[0]].append(stack_top_new)  
                # None of the stack_top is single-qubit gate              
                else:
                    tetris_stack[ts.qubits[0]].append(ts)
                    tetris_stack[ts.qubits[1]].append(ts)
            # stack for 2nd qubit is empty
            elif tetris_stack[ts.qubits[0]]:
                stack_top_0 = tetris_stack[ts.qubits[0]][-1]
                # if the 1st stack_top is single-qubit gate
                if (len(stack_top_0.qubits) == 1):
                    stack_top_new = contTensor(stack_top_0, ts)
                    # Update stack of 1st qubit
                    for qubit in stack_top_0.qubits:
                        pos = tetris_stack[qubit].index(stack_top_0)
                        tetris_stack[qubit].pop(pos)
                        tetris_stack[qubit].insert(pos, stack_top_new)    
                    # Update stack of 2nd qubit
                    tetris_stack[ts.qubits[1]].append(stack_top_new)   
                # None of the stack_top is single-qubit gate            
                else:
                    tetris_stack[ts.qubits[0]].append(ts)
                    tetris_stack[ts.qubits[1]].append(ts) 
            # stack for 1st qubit is empty
            elif tetris_stack[ts.qubits[1]]: 
                stack_top_1 = tetris_stack[ts.qubits[1]][-1]
                # if the 2nd stack_top is single-qubit gate
                if (len(stack_top_1.qubits) == 1):
                    stack_top_new = contTensor(stack_top_1, ts)
                    # Update stack of 1st qubit
                    for qubit in stack_top_1.qubits:
                        pos = tetris_stack[qubit].index(stack_top_1)
                        tetris_stack[qubit].pop(pos)
                        tetris_stack[qubit].insert(pos, stack_top_new)    
                    # Update stack of 2nd qubit
                    tetris_stack[ts.qubits[0]].append(stack_top_new)    
                # None of the stack_top is single-qubit gate           
                else:
                    tetris_stack[ts.qubits[0]].append(ts)
                    tetris_stack[ts.qubits[1]].append(ts)
            # stacks are empty, just push the tensor
            else:
                tetris_stack[ts.qubits[0]].append(ts)
                tetris_stack[ts.qubits[1]].append(ts)
        else:
            print("Multi-qubit (> 2) gates are currently not supported for circuit simplification!")
            return False
        
        if prnt:
            for q in range(qubit_num):
                print("\nTetris stack for qubit ", q, ":")
                for tts in tetris_stack[q]:
                    tts.printTensor()

    ''' Now convert the Tetris stack back to a list of tensors, layer by layer '''
    ts_res = []
    for layer in range(1, depth+1):
        for qubit in range(qubit_num):
            if tetris_stack[qubit]:
                ts_to_add = tetris_stack[qubit].pop(0)
                if ts_to_add not in ts_res:
                    if ts_to_add.depth == layer:
                        ts_res.append(ts_to_add)
                    else:
                        tetris_stack[qubit].insert(0, ts_to_add)
    
    return ts_res

''' Based on output of the above function, this function further performs the Tetris-like TN rank simplification for two-qubit gates '''
def squeezeTN_ultra(tensors, qubit_num, depth, prnt=False):
    ''' Initialize the Tetris stack, one for each qubit line '''
    tetris_stack = [[] for i in range(qubit_num)]

    ''' Now build the Tetris stack, round-2: merge all the consecutive two-qubit gates shareing both qubit lines '''
    for ts in tensors:
        if prnt:
            print('\n\n')
            ts.printTensor()

        # single-qubit gates. There shouldn't be any, but we just push them.
        if (len(ts.qubits) == 1): 
            tetris_stack[ts.qubits[0]].append(ts)
        # two-qubit gates
        elif (len(ts.qubits) == 2):
            # stack for neither qubit is empty
            if tetris_stack[ts.qubits[0]] and tetris_stack[ts.qubits[1]]: 
                stack_top_0 = tetris_stack[ts.qubits[0]][-1]
                stack_top_1 = tetris_stack[ts.qubits[1]][-1]
                # if both stack_top are the same two-qubit gate
                if (stack_top_0 == stack_top_1) and (set(stack_top_1.qubits) == set(ts.qubits)) and (set(stack_top_0.qubits) == set(ts.qubits)):
                    stack_top_new = contTensor(stack_top_1, ts)
                    # Update stack of target qubits
                    for qubit in stack_top_1.qubits:
                        pos = tetris_stack[qubit].index(stack_top_1)
                        tetris_stack[qubit].pop(pos)
                        tetris_stack[qubit].insert(pos, stack_top_new)
                # Not the above case              
                else:
                    tetris_stack[ts.qubits[0]].append(ts)
                    tetris_stack[ts.qubits[1]].append(ts)
            # Not the above case
            else:
                tetris_stack[ts.qubits[0]].append(ts)
                tetris_stack[ts.qubits[1]].append(ts)
        else:
            print("Multi-qubit (> 2) gates are currently not supported for circuit simplification!")
            return False
        
        if prnt:
            for q in range(qubit_num):
                print("\nTetris stack for qubit ", q, ":")
                for tts in tetris_stack[q]:
                    tts.printTensor()    

    ''' Now convert the Tetris stack back to a list of tensors, layer by layer '''
    ts_res = []
    for layer in range(1, depth+1):
        for qubit in range(qubit_num):
            if tetris_stack[qubit]:
                ts_to_add = tetris_stack[qubit].pop(0)
                if ts_to_add not in ts_res:
                    if ts_to_add.depth == layer:
                        ts_res.append(ts_to_add)
                    else:
                        tetris_stack[qubit].insert(0, ts_to_add)
    
    return ts_res
