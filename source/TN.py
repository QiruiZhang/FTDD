'''
Original code from TDD (https://github.com/Veriqc/TDD)

Modifications by Qirui Zhang (qiruizh@umich.edu) for FTDD (https://github.com/QiruiZhang/FTDD)
    - See comments in the TensorNetwork class for added functions
    - Line #143 and beyond
'''

import numpy as np
from TDD import Index, get_tdd,get_identity_tdd, cont

# import Google TensorNetwork
import tensornetwork as gtn
gtn.set_default_backend("pytorch")


class Tensor:
    def __init__(self,data=[],index=[],name=None,qubits=None,depth=0):
        self.data=data
        self.index_set=index
        self.name=name
        self.qubits=qubits 
        self.depth=depth 
    
    def tdd(self): 
        return get_tdd(self.data,self.index_set)   

    def __eq__(self,other): 
        if self.index_set == other.index_set:
            return True
        else:
            return False     

    def printTensor(self):
        print(self.name, self.qubits, ', depth ', self.depth, ', indices ', str([str(ind) for ind in self.index_set]))

class TensorNetwork:
    def __init__(self,tensors=dict(),tn_type='tn',qubits_num=0):
        self.tensors=tensors
        self.tn_type=tn_type
        self.qubits_num=qubits_num

    def cont(self,optimizer=None, prnt=False):
        tdd=get_identity_tdd()
        i=0
        for ts in self.tensors: # The most basic case
            if prnt:
                print("Contracting the ", i, "-th tensor")
            temp_tdd=ts.tdd()
            tdd=cont(tdd,temp_tdd)
            i += 1
        return tdd
    
    ''' 
        Generate the sequential contraction path
        Added by Qirui Zhang (qiruizh@umich.edu) 
    '''
    def get_seq_path(self):
        path = [] 
        tensor_list = self.tensors.copy()

        # The very first pair is (0,1)
        path.append((0, 1))
        tensor_list.pop(0)
        tensor_list.pop(0)
        tensor_list.append(1)

        while len(tensor_list) > 1:
            path.append((0, len(tensor_list)-1))
            tensor_list.pop(0)
            tensor_list.pop()
            tensor_list.append(1)

        return tuple(path)

    ''' 
        PyTDD Contraction with a given order
        Added by Qirui Zhang (qiruizh@umich.edu) 
    '''
    def cont_TN(self, path_cot, debug=False):
        path_list = list(path_cot)
        tdd_list = [ts.tdd() for ts in self.tensors]

        for i in range(len(path_list)):
            pair = path_list[i]

            if debug:
                print("Contracting the ", i, "-th pair ", str(pair))
            
            # Acquire the tensors pointed to by the pair
            tdd_a = tdd_list[pair[0]]
            tdd_b = tdd_list[pair[1]]

            # Perform contraction
            tdd_c = cont(tdd_a, tdd_b)

            # Update tensor list
            tdd_list.pop(max(pair))
            tdd_list.pop(min(pair))
            tdd_list.append(tdd_c)

        if len(tdd_list) != 1:
            print("Error: Resulted TDD list length is ", len(tdd_list), " but not one!")
            return False
        
        tdd = tdd_list[0]
        return tdd

    ''' 
        Contraction using GTN with a given order
        Added by Qirui Zhang (qiruizh@umich.edu) 
    '''
    def cont_GTN(self, path_cot, debug=False): 
        path_list = list(path_cot)
        tensor_list = [(gtn.Node(np.squeeze(ts.data).astype(np.complex128), name = ts.name), ts.index_set) for ts in self.tensors]

        for i in range(len(path_list)):
            pair = path_list[i]

            if debug:
                print("Contracting the ", i, "-th pair ", str(pair))
            
            # Acquire the tensors pointed to by the pair
            ts_a = tensor_list[pair[0]]
            ts_b = tensor_list[pair[1]]

            # Perform contraction
            ts_c = contTensorGTN(ts_a, ts_b)

            # Update tensor list
            tensor_list.pop(max(pair))
            tensor_list.pop(min(pair))
            tensor_list.append(ts_c)

        if len(tensor_list) != 1:
            print("Error: Resulted TDD list length is ", len(tensor_list), " but not one!")
            return False
        
        ts = tensor_list[0]
        return ts
    

''' 
    Below are functions added by Qirui Zhang (qiruizh@umich.edu) for FTDD (https://github.com/QiruiZhang/FTDD) 
'''

''' This function takes in a Tensor and reduce all the hyper-edges, then return the index set and data array '''
def HyperEdgeReduced(ts):
    indices = tuple([ind.key for ind in ts.index_set])
    if len(ts.data.shape) == 6: # two-qubit gates
        ts_data = ts.data[:, :, :, :, 0, 0]
    else:
        ts_data = ts.data

    if (len(ts_data.shape) == 2) and (indices[0] == indices[1]): # single qubit gates
        indices_new = (indices[0], )
        ts_data_new = np.sum(ts_data, axis = 1)
        return indices_new, ts_data_new
    
    if (len(ts_data.shape) == 4) and (indices[0] == indices[1]) and (indices[2] == indices[3]): # two qubit gates, both qubits being hyper-edges
        indices_new = (indices[0], indices[2])
        ts_data_new = np.sum(ts_data, axis = (1,3))
        return indices_new, ts_data_new
    elif (len(ts_data.shape) == 4) and (indices[0] == indices[1]): # two qubit gates, top qubit being hyper-edge
        indices_new = (indices[0], indices[2], indices[3])
        ts_data_new = np.sum(ts_data, axis = 1)
        return indices_new, ts_data_new
    elif (len(ts_data.shape) == 4) and (indices[2] == indices[3]): # two qubit gates, bottom qubit being hyper-edge
        indices_new = (indices[0], indices[1], indices[2])
        ts_data_new = np.sum(ts_data, axis = 3)
        return indices_new, ts_data_new

    indices_new = indices
    ts_data_new = ts_data
    return indices_new, ts_data_new

''' 
    This function simply contracts two tensors as dense arrays
'''
def contTensor(ts_A, ts_B):
    ''' Get index list of A and B and take the intersection as indices to be contracted '''
    ''' Hyper-edges are not handled here, i.e., indices are treated as different if their '.idx' fields are different '''
    var_A = ts_A.index_set
    var_B = ts_B.index_set
    varCont = [var for var in var_A if var in var_B] # indices to be contracted
    varOut_A = [var for var in var_A if not var in varCont]
    varOut_B = [var for var in var_B if not var in varCont]

    ''' Positions of indices to be contracted in A and B index lists. To be used as inputs to np.tensordot() '''
    varContPos_A = tuple([var_A.index(var) for var in varCont]) # position of varCont in tensor A index list
    varContPos_B = tuple([var_B.index(var) for var in varCont]) # position of varCont in tensor B index list

    ''' Perform the contraction '''
    data_C = np.tensordot(np.squeeze(ts_A.data), np.squeeze(ts_B.data), (varContPos_A, varContPos_B) )
    
    ''' Create the new tensor C '''
    ts_C = Tensor(data_C)
    ts_C.index_set = varOut_A + varOut_B # Append open indices of B to those of A
    ts_C.qubits = list(set(ts_A.qubits + ts_B.qubits))
    ts_C.name = ts_A.name + '-' + ts_B.name

    if len(var_A) > len(var_B):
        ts_C.depth = ts_A.depth
    elif len(var_A) < len(var_B):
        ts_C.depth = ts_B.depth
    else:
        ts_C.depth = min(ts_A.depth, ts_B.depth)

    return ts_C

''' This function contract two tensors using Google TensorNetwork '''
def contTensorGTN(ts_A, ts_B):
    ''' Get index list of A and B and take the intersection as indices to be contracted '''
    var_A = ts_A[1]
    var_B = ts_B[1]
    varCont = [var for var in var_A if var in var_B] # indices to be contracted
    varOut_A = [var for var in var_A if not var in varCont]
    varOut_B = [var for var in var_B if not var in varCont]

    ''' Positions of indices to be contracted in A and B index lists. To be used as inputs to np.tensordot() '''
    varContPos_A = tuple([var_A.index(var) for var in varCont]) # position of varCont in tensor A index list
    varContPos_B = tuple([var_B.index(var) for var in varCont]) # position of varCont in tensor B index list

    ''' Set-up edges for GTN '''
    edges = []
    for i in range(len(varCont)):
        edges.append(ts_A[0][varContPos_A[i]] ^ ts_B[0][varContPos_B[i]])

    ''' Perform the contraction '''
    ts_C_node = gtn.contract_between(ts_A[0], ts_B[0], allow_outer_product=True)

    ''' Create the new tensor C '''
    ts_C_index_set = varOut_A + varOut_B # Append open indices of B to those of A
    ts_C_node.name = ts_A[0].name + '-' + ts_B[0].name

    ts_C = (ts_C_node, ts_C_index_set)
    return ts_C

'''
    This function takes the array from cTDD.TDD.to_array() and transpose it from the global order to the order of indices given
    The order of indices out of TDD obeys global order set by Ini_TDD(), however, for the original tensors, they
    come with user-assigned orders, thus this function is helpful for checking whether a user-provided tensor has been properly
    converted to TDD and back.
'''
def tdd_to_tensor(arr, index_set):
    arr_ = arr.reshape(tuple([2 for i in range(len(index_set))]))

    index_set_sort = index_set.copy()
    index_set_sort.sort()

    perm = []
    for ind in index_set:
        perm.append(index_set_sort.index(ind))
    perm = tuple(perm)

    tdd_ToTensor = np.transpose(arr_, perm)
    return tdd_ToTensor

'''
    This function takes the array from GTN and transpose from the order of indices given to the global order, reverse of above
'''
def reorder_gts(gts):
    index_set_sort = gts[1].copy()
    index_set_sort.sort()

    perm = []
    for ind in index_set_sort:
        perm.append(gts[1].index(ind))
    perm = tuple(perm)

    res_gts = gtn.Node(np.transpose(gts[0].tensor, perm), name = gts[0].name)
    res_index_set = index_set_sort

    return (res_gts, res_index_set)
