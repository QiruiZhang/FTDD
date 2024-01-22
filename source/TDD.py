'''
Original code from TDD (https://github.com/Veriqc/TDD), not modified
'''

import sys
import numpy as np
import copy
import random
from graphviz import Digraph
from IPython.display import Image

"""Define global variables"""
computed_table = dict()
unique_table = dict()
global_index_order = dict()
global_node_idx=0
add_find_time=0
add_hit_time=0
cont_find_time=0
cont_hit_time=0
node_find_time=0
node_hit_time=0
epi=0.000001

class Index:
    """The index, here idx is used when there is a hyperedge"""
    def __init__(self,key,idx=0):
        self.key = key
        self.idx = idx
        
    def __eq__(self,other):
        if self.key == other.key and self.idx == other.idx:
            return True
        else:
            return False
        
    ''' Operator overloading for '<' of Index. Used for the 'sort' in get_index_2_key() '''
    def __lt__(self,other):
        if global_index_order[self.key] < global_index_order[other.key]:
            return True
        elif self.key == other.key and self.idx<other.idx:
            return True
        
        return False
    
    def __str__(self):
        return str((self.key,self.idx))

class Node:
    """To define the node of TDD"""
    def __init__(self,key,num=2):
        self.idx = 0 
        self.key = key 
        self.succ_num=num
        self.out_weight=[1]*num 
        self.successor=[None]*num 
        self.meas_prob=[]

    def get_size(self) -> int:
        if self.key == -1:
            node_size = 0
        else:
            node_size   = sys.getsizeof(self.key) \
                        + sys.getsizeof(self.out_weight) \
                        + 2 * sys.getsizeof(self.out_weight[0]) \
                        + sys.getsizeof(self.successor) \
                        + sys.getsizeof(self.successor[0]) \
                        + sys.getsizeof(self.successor[1])

        return node_size

class TDD: 
    def __init__(self,node):
        """TDD"""
        self.weight=1
        
        self.index_set=[]
        
        self.key_2_index=dict()
        self.index_2_key=dict()

        self.key_width=dict() 
        
        if isinstance(node,Node):
            self.node=node
        else:
            self.node=Node(node)
    
    def get_size(self):
        return sys.getsizeof(self.weight) + sys.getsizeof(self.key_2_index) + sys.getsizeof(self.index_2_key)

    def node_number(self):
        node_set=set()
        node_set=get_node_set(self.node,node_set)
        return len(node_set)
    
    def self_copy(self):
        temp = TDD(self.node)
        temp.weight = self.weight
        temp.index_set = copy.copy(self.index_set)
        temp.key_2_index=copy.copy(self.key_2_index)
        temp.index_2_key=copy.copy(self.index_2_key)
        return temp
    
    def show(self,fname='output',real_label=True):
        edge=[]              
        dot=Digraph(name='reduced_tree')
        dot=layout(self.node,self.key_2_index,dot,edge,real_label)
        dot.node('-0','',shape='none')
        dot.edge('-0',str(self.node.idx),color="blue",label=str(complex(round(self.weight.real,2),round(self.weight.imag,2))))
        dot.format = 'png'
        return Image(dot.render(fname))
    
    def to_array(self,var=[]):
        split_pos=0
        key_repeat_num=dict()
        var_idx=dict()       
        
        if var:
            for idx in var:
                if not idx.key in var_idx:
                    var_idx[idx.key]=1
                else:
                    var_idx[idx.key]+=1
        elif self.index_set:
            for idx in self.index_set:
                if not idx.key in var_idx:
                    var_idx[idx.key]=1
                else:
                    var_idx[idx.key]+=1
        
        if var:
            split_pos=len(var_idx)-1
        elif self.key_2_index:
            split_pos=max(self.key_2_index)
        else:
            split_pos=self.node.key
        
        for k in range(split_pos+1):
            if k in self.key_2_index:
                if self.key_2_index[k] in var_idx:
                    key_repeat_num[k] = var_idx[self.key_2_index[k]]
            else:
                key_repeat_num[k]=1
        
        res = tdd_2_np(self,split_pos,key_repeat_num)
        return res

    def measure(self,split_pos=None): 
        res=[]
        get_measure_prob(self)
        if split_pos==None:
            if self.key_2_index:
                split_pos=max(self.key_2_index)
            else:
                split_pos=self.node.key
        
        if split_pos==-1:
            return ''
        else:
            if split_pos!=self.node.key:
                l=random.randint(0,1)
                temp_res=self.measure(split_pos-1)
                res=str(l)+temp_res
                return res
            l=random.uniform(0,sum(self.node.meas_prob))
            if l<self.node.meas_prob[0]:
                temp_tdd=Slicing(self,self.node.key,0)
                temp_res=temp_tdd.measure(split_pos-1)
                res='0'+temp_res
            else:
                temp_tdd=Slicing(self,self.node.key,1)
                temp_res=temp_tdd.measure(split_pos-1)
                res='1'+temp_res
        return res

    def get_amplitude(self,b):
        """b is the term for calculating the amplitude"""
        if len(b)==0:
            return self.weight
        
        if len(b)!=self.node.key+1:
            b.pop(0)
            return self.get_amplitude(b)
        else:
            temp_tdd=Slicing(self,self.node.key,b[0])
            b.pop(0)
            res=temp_tdd.get_amplitude(b)
            return res*self.weight
    
    def sampling(self,k):
        res=[]
        for k1 in range(k):
            temp_res=self.measure()
            res.append(temp_res )
        return res
    
    def __eq__(self,other): 
        if self.node==other.node and get_int_key(self.weight)==get_int_key(other.weight):
            return True
        else:
            return False

def layout(node,key_2_idx,dot=Digraph(),succ=[],real_label=True):
    col=['red','blue','black','green']
    if real_label and node.key in key_2_idx:
        if node.key==-1:
            dot.node(str(node.idx), str(1), fontname="helvetica",shape="circle",color="red")
        else:
            dot.node(str(node.idx), key_2_idx[node.key], fontname="helvetica",shape="circle",color="red")
    else:
        dot.node(str(node.idx), str(node.key), fontname="helvetica",shape="circle",color="red")
    for k in range(node.succ_num):
        if node.successor[k]:
            label1=str(complex(round(node.out_weight[k].real,2),round(node.out_weight[k].imag,2)))
            if not node.successor[k] in succ:
                dot=layout(node.successor[k],key_2_idx,dot,succ,real_label)
                dot.edge(str(node.idx),str(node.successor[k].idx),color=col[k%4],label=label1)
                succ.append(node.successor[k])
            else:
                dot.edge(str(node.idx),str(node.successor[k].idx),color=col[k%4],label=label1)
    return dot

def Ini_TDD(index_order=[]):
    """To initialize the unique_table,computed_table and set up a global index order"""
    global computed_table
    global unique_table
    global global_node_idx
    global add_find_time,add_hit_time,cont_find_time,cont_hit_time,node_find_time,node_hit_time
    global_node_idx=0
    unique_table = dict()
    computed_table = dict()
    add_find_time=0
    add_hit_time=0
    cont_find_time=0
    cont_hit_time=0
    node_find_time=0
    node_hit_time=0
    set_index_order(index_order)
    return get_identity_tdd()

def Clear_TDD():
    """To initialize the unique_table,computed_table and set up a global index order"""
    global computed_table
    global unique_table
    global global_node_idx
    global add_find_time,add_hit_time,cont_find_time,cont_hit_time,node_find_time,node_hit_time
    global_node_idx=0
    unique_table.clear()
    computed_table.clear()
    add_find_time=0
    add_hit_time=0
    cont_find_time=0
    cont_hit_time=0
    node_find_time=0
    node_hit_time=0
    global_node_idx=0

def get_identity_tdd():
    ''' Return a tdd with only a terminal node '''
    node = Find_Or_Add_Unique_table(-1)
    tdd = TDD(node)
    tdd.index_2_key={-1:-1}
    tdd.key_2_index={-1:-1}
    return tdd

def get_unique_table():
    return unique_table

def get_unique_table_num():
    return len(unique_table)

def get_computed_table_num():
    return len(computed_table)

def set_index_order(var_order):
    global global_index_order
    global_index_order=dict()
    if isinstance(var_order,list):
        for k in range(len(var_order)):
            global_index_order[var_order[k]]=k
    if isinstance(var_order,dict):
        global_index_order = copy.copy(var_order)
    global_index_order[-1] = float('inf')

def get_index_order():
    global global_index_order
    return copy.copy(global_index_order)

def get_int_key(weight):
    """To transform a complex number to a tuple with int values"""
    global epi
    return (int(round(weight.real/epi)) ,int(round(weight.imag/epi)))

def get_node_set(node,node_set=set()):
    """Only been used when counting the node number of a TDD"""
    if not node in node_set:
        node_set.add(node)
        for k in range(node.succ_num):
            if node.successor[k]:
                node_set = get_node_set(node.successor[k],node_set)
    return node_set

def Find_Or_Add_Unique_table(x,weigs=[],succ_nodes=[]):
    """To return a node if it already exist, creates a new node otherwise"""

    global global_node_idx,unique_table,node_find_time,node_hit_time

    if x==-1:
        if unique_table.__contains__(x):
            return unique_table[x]
        else:
            res=Node(x)
            res.idx=0
            unique_table[x]=res
        return res
    temp_key=[x]
    for k in range(len(weigs)):
        temp_key.append(get_int_key(weigs[k]))
        temp_key.append(succ_nodes[k])
    temp_key=tuple(temp_key)
    
    node_find_time += 1
    if temp_key in unique_table:
        node_hit_time +=1
        return unique_table[temp_key]
    else:
        res=Node(x,len(succ_nodes))
        global_node_idx+=1
        res.idx=global_node_idx
        res.out_weight=weigs
        res.successor=succ_nodes
        unique_table[temp_key]=res
    return res

def normalize(x,the_successors): 
    """The normalize and reduce procedure"""

    global epi
    all_equal=True
    for k in range(1,len(the_successors)):
        if the_successors[k]!=the_successors[0]:
            all_equal=False
            break
    if all_equal:
        return the_successors[0]
    
    weigs=[succ.weight for succ in the_successors]
    
    weigs_abs=[np.around(abs(weig)/epi) for weig in weigs]
    weig_max=weigs[weigs_abs.index(max(weigs_abs))]

    weigs=[weig/weig_max for weig in weigs]
    for k in range(len(the_successors)):
        if get_int_key(weigs[k])==(0,0):
            node=Find_Or_Add_Unique_table(-1)
            the_successors[k]=TDD(node)
            the_successors[k].weight=weigs[k]=0    
    succ_nodes=[succ.node for succ in the_successors]
    node=Find_Or_Add_Unique_table(x,weigs,succ_nodes)
    res=TDD(node)
    res.weight=weig_max
    return res

def get_count():
    global add_find_time,add_hit_time,cont_find_time,cont_hit_time,node_find_time,node_hit_time
    print("node:",node_hit_time,"/",node_find_time,"/",node_hit_time/node_find_time if node_find_time != 0 else 0)
    print("add:",add_hit_time,'/',add_find_time,'/',add_hit_time/add_find_time if add_find_time != 0 else 0)
    print("cont:",cont_hit_time,"/",cont_find_time,"/",cont_hit_time/cont_find_time if cont_find_time != 0 else 0)
    print("Final number of nodes: ", global_node_idx)

def find_computed_table(item):
    """To return the results that already exist"""
    global computed_table,add_find_time,add_hit_time,cont_find_time,cont_hit_time
    if item[0]=='s':
        temp_key=item[1].index_2_key[item[2]]
        the_key=('s',get_int_key(item[1].weight),item[1].node,temp_key,item[3])
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            return tdd
    elif item[0] == '+': 
        the_key=('+',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node)
        add_find_time+=1
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            add_hit_time+=1
            return tdd
        the_key=('+',get_int_key(item[2].weight),item[2].node,get_int_key(item[1].weight),item[1].node)
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            add_hit_time+=1
            return tdd
    else:
        the_key=('*',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node,item[3][0],item[3][1],item[4])
        cont_find_time+=1
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            cont_hit_time+=1            
            return tdd
        the_key=('*',get_int_key(item[2].weight),item[2].node,get_int_key(item[1].weight),item[1].node,item[3][1],item[3][0],item[4])
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            cont_hit_time+=1            
            return tdd
    return None

def insert_2_computed_table(item,res):
    """To insert an item to the computed table"""
    global computed_table,cont_time,find_time,hit_time
    if item[0]=='s':
        temp_key=item[1].index_2_key[item[2]]
        the_key = ('s',get_int_key(item[1].weight),item[1].node,temp_key,item[3])
    elif item[0] == '+':
        the_key = ('+',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node)
    else:
        the_key = ('*',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node,item[3][0],item[3][1],item[4])
    computed_table[the_key] = (res.weight,res.node)

def get_index_2_key(var):
    var_sort=copy.copy(var)

    var_sort.sort() 

    var_sort.reverse()
    idx_2_key={-1:-1}
    key_2_idx={-1:-1}
    n=0
    for idx in var_sort:
        if not idx.key in idx_2_key:
            idx_2_key[idx.key]=n
            key_2_idx[n]=idx.key
            n+=1
    return idx_2_key,key_2_idx

def get_tdd(U,var=[]):
    idx_2_key, key_2_idx = get_index_2_key(var)
    
    order=[]
    for idx in var:
        order.append(idx_2_key[idx.key])
    
    tdd = np_2_tdd(U,order)
    tdd.index_2_key=idx_2_key
    tdd.key_2_index=key_2_idx
    tdd.index_set=var
    
    return tdd

def np_2_tdd(U,order=[],key_width=True):
    U_dim=U.ndim
    U_shape=U.shape

    if sum(U_shape)==U_dim: 
        node=Find_Or_Add_Unique_table(-1)
        res=TDD(node)
        for k in range(U_dim):
            U=U[0]
        res.weight=U
        return res 
    
    if not order:
        order=list(range(U_dim))
    
    if key_width:
        the_width=dict()
        for k in range(max(order)+1):
            split_pos=order.index(k)
            the_width[k]=U.shape[split_pos]
       
    x=max(order)
    split_pos=order.index(x)
    order[split_pos]=-1
    split_U=np.split(U,U_shape[split_pos],split_pos)
    
    while x in order: 
        split_pos=order.index(x)
        for k in range(len(split_U)):
            split_U[k]=np.split(split_U[k],U_shape[split_pos],split_pos)[k]
        order[split_pos]=-1
    
    the_successors=[]
    for k in range(U_shape[split_pos]):
        res=np_2_tdd(split_U[k],copy.copy(order),False)
        the_successors.append(res)

    tdd = normalize(x,the_successors) 
    
    if key_width:
        tdd.key_width=the_width
    
    return tdd

def tdd_2_np(tdd,split_pos=None,key_repeat_num=dict()):
    if split_pos==None:
        split_pos=tdd.node.key
            
    if split_pos==-1:
        return tdd.weight
    else:
        the_succs=[]
        for k in range(tdd.key_width[split_pos]):
            succ=Slicing2(tdd,split_pos,k)
            succ.key_width=tdd.key_width
            temp_res=tdd_2_np(succ,split_pos-1,key_repeat_num)
            the_succs.append(temp_res)
        if not split_pos in key_repeat_num:
            r = 1
        else:
            r = key_repeat_num[split_pos]
            
        if r==1:
            res=np.stack(tuple(the_succs), axis=the_succs[0].ndim)
        else:
            new_shape=list(the_succs[0].shape)
            for k in range(r):
                new_shape.append(tdd.key_width[split_pos])
            res=np.zeros(new_shape)
            for k1 in range(tdd.key_width[split_pos]):
                f='res['
                for k2 in range(the_succs[0].ndim):
                    f+=':,'
                for k3 in range(r-1):
                    f+=str(k1)+','
                f=f[:-1]+']'
                eval(f)[k1]=the_succs[k1]
        return res

def get_measure_prob(tdd):
    if tdd.node.meas_prob:
        return tdd
    if tdd.node.key==-1:
        tdd.node.meas_prob=[0.5,0.5]
        return tdd
    if not tdd.node.succ_num==2:
        print("Only can be used for binary quantum state")
        return tdd

    get_measure_prob(Slicing(tdd,tdd.node.key,0))
    get_measure_prob(Slicing(tdd,tdd.node.key,1))
    
    tdd.node.meas_prob=[0]*2
    tdd.node.meas_prob[0]=abs(tdd.node.out_weight[0])**2 * sum(tdd.node.successor[0].meas_prob) * 2**(tdd.node.key-tdd.node.successor[0].key)
    tdd.node.meas_prob[1]=abs(tdd.node.out_weight[1])**2 * sum(tdd.node.successor[1].meas_prob) * 2**(tdd.node.key-tdd.node.successor[1].key)
    return tdd

def cont(tdd1,tdd2, debug=False):

    var_cont=[var for var in tdd1.index_set if var in tdd2.index_set]
    var_out1=[var for var in tdd1.index_set if not var in var_cont]
    var_out2=[var for var in tdd2.index_set if not var in var_cont]

    var_out=var_out1+var_out2
    var_out.sort()
    var_out_idx=[var.key for var in var_out]
    var_cont_idx=[var.key for var in var_cont]

    var_cont_idx=[var for var in var_cont_idx if not var in var_out_idx]
    
    idx_2_key={-1:-1}
    key_2_idx={-1:-1}
    n=0
    for k in range(len(var_out_idx)-1,-1,-1):
        if not var_out_idx[k] in idx_2_key:
            idx_2_key[var_out_idx[k]]=n
            key_2_idx[n]=var_out_idx[k]
            n+=1
    
    key_2_new_key=[[],[]]
    cont_order=[[],[]]
    for k in range(len(tdd1.key_2_index)-1):
        v=tdd1.key_2_index[k]
        if v in idx_2_key:
            key_2_new_key[0].append(idx_2_key[v])
        else:
            key_2_new_key[0].append('c')
        cont_order[0].append(global_index_order[v])  
    cont_order[0].append(float('inf'))
    
    for k in range(len(tdd2.key_2_index)-1):     
        v=tdd2.key_2_index[k]
        if v in idx_2_key:
            key_2_new_key[1].append(idx_2_key[v])
        else:
            key_2_new_key[1].append('c')
        cont_order[1].append(global_index_order[v])
    cont_order[1].append(float('inf'))

    tdd=contract(tdd1,tdd2,key_2_new_key,cont_order,len(set(var_cont_idx)))

    tdd.index_set=var_out
    tdd.index_2_key=idx_2_key
    tdd.key_2_index=key_2_idx

    key_width=dict()
    for k1 in range(len(key_2_new_key[0])):
        if not key_2_new_key[0][k1]=='c' and not key_2_new_key[0][k1] ==-1:
            key_width[key_2_new_key[0][k1]]=tdd1.key_width[k1]
    for k2 in range(len(key_2_new_key[1])):
        if not key_2_new_key[1][k2]=='c' and not key_2_new_key[1][k2] ==-1:
            key_width[key_2_new_key[1][k2]]=tdd2.key_width[k2]             
    tdd.key_width=key_width

    return tdd

def contract(tdd1,tdd2,key_2_new_key,cont_order,cont_num):
    """The contraction of two TDDs, var_cont is in the form [[4,1],[3,2]]"""

    k1=tdd1.node.key
    k2=tdd2.node.key
    w1=tdd1.weight
    w2=tdd2.weight
    
    if k1==-1 and k2==-1:
        if w1==0:
            tdd=TDD(tdd1.node)
            tdd.weight=0
            return tdd
        if w2==0:
            tdd=TDD(tdd1.node)
            tdd.weight=0
            return tdd
        tdd=TDD(tdd1.node)
        tdd.weight=w1*w2
        if cont_num>0:
            tdd.weight*=2**cont_num
        return tdd

    if k1==-1:
        if w1==0:
            tdd=TDD(tdd1.node)
            tdd.weight=0
            return tdd
        if cont_num ==0 and key_2_new_key[1][k2]==k2:
            tdd=TDD(tdd2.node)
            tdd.weight=w1*w2
            return tdd
            
    if k2==-1:
        if w2==0:
            tdd=TDD(tdd2.node)
            tdd.weight=0
            return tdd        
        if cont_num ==0 and key_2_new_key[0][k1]==k1:
            tdd=TDD(tdd1.node)
            tdd.weight=w1*w2
            return tdd
    
    tdd1.weight=1
    tdd2.weight=1
    
    temp_key_2_new_key=[]
    temp_key_2_new_key.append(tuple([k for k in key_2_new_key[0][:(k1+1)]]))
    temp_key_2_new_key.append(tuple([k for k in key_2_new_key[1][:(k2+1)]]))
    
    tdd=find_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num])
    if tdd:
        tdd.weight=tdd.weight*w1*w2
        tdd1.weight=w1
        tdd2.weight=w2
        return tdd
    
    if cont_order[0][k1]<cont_order[1][k2]:
        the_key=key_2_new_key[0][k1]
        if the_key!='c':
            the_successors=[]
            for k in range(tdd1.node.succ_num):
                res=contract(Slicing(tdd1,k1,k),tdd2,key_2_new_key,cont_order,cont_num)
                the_successors.append(res)
            tdd=normalize(the_key,the_successors)
            insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
            tdd.weight=tdd.weight*w1*w2
        else:
            tdd=TDD(Find_Or_Add_Unique_table(-1))
            tdd.weight=0
            for k in range(tdd1.node.succ_num):
                res=contract(Slicing(tdd1,k1,k),tdd2,key_2_new_key,cont_order,cont_num-1)           
                tdd=add(tdd,res)
            insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
            tdd.weight=tdd.weight*w1*w2
    elif cont_order[0][k1]==cont_order[1][k2]:
        the_key=key_2_new_key[0][k1]
        if the_key!='c':
            the_successors=[]
            for k in range(tdd1.node.succ_num):
                res=contract(Slicing(tdd1,k1,k),Slicing(tdd2,k2,k),key_2_new_key,cont_order,cont_num)
                the_successors.append(res)
            tdd=normalize(the_key,the_successors)
            insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
            tdd.weight=tdd.weight*w1*w2
        else:
            tdd=TDD(Find_Or_Add_Unique_table(-1))
            tdd.weight=0
            for k in range(tdd1.node.succ_num):
                res=contract(Slicing(tdd1,k1,k),Slicing(tdd2,k2,k),key_2_new_key,cont_order,cont_num-1)           
                tdd=add(tdd,res)
            insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
            tdd.weight=tdd.weight*w1*w2
    else:
        the_key=key_2_new_key[1][k2]
        if the_key!='c':
            the_successors=[]
            for k in range(tdd2.node.succ_num):
                res=contract(tdd1,Slicing(tdd2,k2,k),key_2_new_key,cont_order,cont_num)
                the_successors.append(res)
            tdd=normalize(the_key,the_successors)
            insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
            tdd.weight=tdd.weight*w1*w2
        else:
            tdd=TDD(Find_Or_Add_Unique_table(-1))
            tdd.weight=0
            for k in range(tdd2.node.succ_num):
                res=contract(tdd1,Slicing(tdd2,k2,k),key_2_new_key,cont_order,cont_num-1)           
                tdd=add(tdd,res)
            insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
            tdd.weight=tdd.weight*w1*w2

    tdd1.weight=w1
    tdd2.weight=w2
    
    return tdd

def Slicing(tdd,x,c):
    """Slice a TDD with respect to x=c"""

    k=tdd.node.key
    
    if k==-1:
        return tdd.self_copy()
    
    if k<x:
        return tdd.self_copy()
    
    if k==x:
        res=TDD(tdd.node.successor[c])
        res.weight=tdd.node.out_weight[c]
        return res
    else:
        print("Not supported yet!!!")

def Slicing2(tdd,x,c):
    """Slice a TDD with respect to x=c"""

    k=tdd.node.key
    
    if k==-1:
        return tdd.self_copy()
    
    if k<x:
        return tdd.self_copy()
    
    if k==x:
        res=TDD(tdd.node.successor[c])
        res.weight=tdd.node.out_weight[c]*tdd.weight
        return res
    else:
        print("Not supported yet!!!")        

def add(tdd1,tdd2):
    """The apply function of two TDDs. Mostly, it is used to do addition here."""
    global global_index_order  
    
    k1=tdd1.node.key
    k2=tdd2.node.key

    if tdd1.weight==0:
        return tdd2.self_copy()
    
    if tdd2.weight==0:
        return tdd1.self_copy()
    
    if tdd1.node==tdd2.node:
        weig=tdd1.weight+tdd2.weight
        if get_int_key(weig)==(0,0):
            term=Find_Or_Add_Unique_table(-1)
            res=TDD(term)
            res.weight=0
            return res
        else:
            res=TDD(tdd1.node)
            res.weight=weig
            return res

    tdd = find_computed_table(['+',tdd1,tdd2])
    if tdd:
        return tdd
    
    the_successors=[]
    if k1>k2:
        x=k1
        for k in range(tdd1.node.succ_num):
            res=add(Slicing2(tdd1,x,k),tdd2)
            the_successors.append(res)
    elif k1==k2:
        x=k1
        for k in range(tdd1.node.succ_num):
            res=add(Slicing2(tdd1,x,k),Slicing2(tdd2,x,k))
            the_successors.append(res)        
    else:
        x=k2
        for k in range(tdd2.node.succ_num):
            res=add(tdd1,Slicing2(tdd2,x,k))
            the_successors.append(res)
            
    res = normalize(x,the_successors)
    insert_2_computed_table(['+',tdd1,tdd2],res)
    return res
