/*
 * File: cTDD.hpp
 * Author: Qirui Zhang (qiruizh@umich.edu)
 * Description: C++ backend for FTDD (https://github.com/QiruiZhang/FTDD)
 * 
 * Copyright (c) 2024 Qirui Zhang
 * All rights reserved.
 */

#ifndef CTDD_HPP
#define CTDD_HPP

#include <iostream>
#include <sstream>
#include <iomanip>
#include <cstdlib>
#include <ctime>
#include <random>

#include <string>
#include <cmath>
#include <limits>
#include <complex>

#include <vector>
#include <set>
#include <map>
#include <unordered_map>
#include <algorithm>
#include <Eigen/Dense>

#include <graphviz/gvc.h>

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/numpy.h>

namespace py = pybind11;
constexpr auto byref = py::return_value_policy::reference_internal;

typedef double dataType;
typedef int8_t keyType;
typedef uint16_t refCntType;
typedef Eigen::VectorXcd complexArrayType;
typedef std::uint32_t hashType;


/*
    Global Variables
*/

// 32-bit FNV hash parameters
const hashType fnv_prime = 0x01000193;
const hashType fnv_offset_basis = 0x811c9dc5;

dataType epi = 0.000001;
dataType epi_inv = 1 / epi;

// two-level quantum system
uint succ_num = 2;

// the global index order
std::unordered_map<std::string, int> global_index_order;

// Randomization
  // Distribution 1: uniform disbribution for 0 and 1
std::random_device rd1;
std::mt19937 gen1(rd1());
std::uniform_int_distribution<int> dist1(0, 1);
  // For distribution 2: uniform distribution for [0, sum(meas_prob))
std::random_device rd2;
std::mt19937 gen2(rd2());

/* 
    Implementation of TDD.Index in C++
*/
class Index {

public:
    std::string key;
    int idx;

    Index(std::string key_, int idx_=0) {
        key = key_;
        idx = idx_;
    }

    bool operator==(const Index& other) const {
        if (key == other.key && idx == other.idx) {
            return true;
        } else {
            return false;
        }
    }

    bool operator<(const Index& other) const {
        if (global_index_order[key] < global_index_order[other.key]) {
            return true;
        } else if (key == other.key && idx < other.idx) {
            return true;
        } else {
            return false;
        }
    }

    std::string str() const {
        return "(" + key + ", " + std::to_string(idx) + ")";
    }
};


/*
    Implementation of TDD.Node in C++
*/
class Edge; // Forward declaration of Edge

class Node {
public:
    keyType key; // The level of the node (not edge name in Index)
    refCntType refCnt; // reference count
    std::vector<Edge> edges;
    Node* next{}; // pointer to the next node in unique table

    std::vector<dataType> meas_prob;

    Node() {
        key = -1;
        refCnt = 0;
        next = nullptr;
    }
    Node(keyType key_) {
        key = key_;
        refCnt = 0;
        next = nullptr;
    }
};

// The terminal node (with a value of one) at level -1 
Node* node_n1 = new Node(-1);


/*
    Implementation of Edge in C++
*/
class Edge {

public:
    std::complex<dataType> weight;
    Node* node;

    Edge() {
        weight = 0;
        node = nullptr;
    }
    Edge(Node* node_) {
        weight = 1.0;
        node = node_;
    }

    bool operator==(const Edge& other) const;

    std::complex<dataType> get_amplitude_recur(std::vector<int>& index_values);

    void get_measure_prob_recur();

    std::string measure_recur(int split_pos);
};


/*
    Implementation of TDD.TDD in C++
*/
class TDD {

public:
    std::vector<Index> index_set;
    std::map<keyType, std::string> key_2_index;
    std::map<std::string, keyType> index_2_key;
    Edge root;

    TDD() {
        root = Edge();
    }
    TDD(Edge root_) {
        root = root_;
    }

    bool operator==(const TDD& other) const;

    std::string str() {
        std::ostringstream ss;
        ss << "TDD of weight " << root.weight << ", pointing to node at " << root.node;
        ss << "\nkey_2_index: {\n";
        for (auto const& pair : key_2_index) {
            ss << "    (" << std::to_string(pair.first) << ": " << pair.second << ")\n";
        }
        ss << "}";
        return ss.str();
    }

    int node_number();

    complexArrayType to_array();

    std::complex<dataType> get_amplitude(py::list index_values);
    
    void get_measure_prob();

    std::string measure();
};


/* 
    Implementation of TN.Tensor in C++
*/
class TensorArray {

public:
    complexArrayType vec;
    std::vector<uint> shape; std::vector<uint> stride;
    uint ndim;

    TensorArray() {ndim = 0;}
    TensorArray(const complexArrayType& vec_, const std::vector<uint>& shape_, uint ndim_) {
        vec = vec_;
        shape = shape_;
        ndim = ndim_;

        stride = std::vector<uint>(shape.size());
        stride[shape.size()-1] = shape[shape.size()-1];
        for (int k = shape.size()-2; k >= 0; k--) { 
            stride[k] = shape[k] * stride[k+1];
        }
    }

    std::complex<dataType> at(const std::vector<uint>& slice) {
        uint addr = slice[slice.size()-1];
        for (int k = slice.size()-2; k >= 0; k--) {
            addr += slice[k] * stride[k+1];
        }
        return vec[addr];
    }
    
    void update(const std::vector<uint>& slice, const std::complex<dataType>& val) {
        uint addr = slice[slice.size()-1];
        for (int k = slice.size()-2; k >= 0; k--) {
            addr += slice[k] * stride[k+1];
        }
        vec[addr] = val;
    }
};

class Tensor {

public:
    TensorArray data;
    std::vector<Index> index_set;
    std::string name;
    std::vector<int> qubits;
    int depth;

    Tensor(py::object data_, py::list shape_, py::list index_key, py::list index_idx, std::string name_, py::list qubits_list, int depth_ = 0) {
        name = name_;
        depth = depth_;

        // Initialize data
        complexArrayType vec = data_.cast<complexArrayType>();
        std::vector<uint> shape;
        for (uint k = 0; k < shape_.size(); k++) {
            int rank = shape_[k].cast<uint>();
            shape.push_back(rank);
        }
        data = TensorArray(vec, shape, shape.size());

        // Initialize index_set
        for (uint k = 0; k < index_key.size(); k++) {
            std::string key = index_key[k].cast<std::string>();
            int idx = index_idx[k].cast<int>();
            index_set.push_back(Index(key, idx));
        }

        // Initialize qubits_list
        for (uint k = 0; k < qubits_list.size(); k++) {
            qubits.push_back(qubits_list[k].cast<int>());
        }
    }

    std::string str() {
        std::string res;
        
        res = name + " [";
        for (auto qubit : qubits) {
            res += std::to_string(qubit) + " ";
        }
        res += "], depth " + std::to_string(depth) + ", indices [";
        for (auto ind : index_set) {
            res += ind.str() + " ";
        }
        res += "], shape (";
        for (auto rank : data.shape) {
            res += std::to_string(rank) + " ";
        }
        res += ")";

        return res;
    }

    complexArrayType get_data() {
        return data.vec;
    }

    TDD tdd();
};


/* 
    Implementation of TN.TensorNetwork in C++
*/
class TensorNetwork {

public:
    int qubits_num;
    std::string tn_type;
    std::vector<Tensor> tensors;

    TensorNetwork(std::string tn_type_, int qubits_num_) {
        tn_type = tn_type_;
        qubits_num = qubits_num_;
    }

    std::string str() {
        return "A tensor network of type " + tn_type + ", for " + std::to_string(qubits_num) + " qubits, with " + std::to_string(tensors.size()) + " tensors.";
    }

    void add_tensor(Tensor ts, bool debug=false) { 
        tensors.push_back(ts);
        if (debug) {
            std::cout << ts.str() << std::endl;
        }
    }

    TDD cont_TN(py::tuple path, bool debug=false);
};


/*
    Utility Functions: not core TDD functions
*/

// Get the number of unique nodes
int get_unique_table_num();

// Get the size of computed tables
int get_add_computed_table_num();
int get_cont_computed_table_num();
int get_gc_runs();

// Report TDD statistics
std::string get_count();

// Scale a weight up to reduce numerical instability
std::tuple<int, int> get_int_key(const std::complex<dataType>& weight);

// Set global_index_order with all_indexs
void set_index_order(py::list var_order, bool debug);

// Get the set of nodes for a TDD
void get_node_set(Node* node, std::set<Node*>& node_set);

// Create TDD's index_2_key and key_2_index based on index_set of a tensor
std::pair<std::map<std::string, keyType>, std::map<keyType, std::string>> get_index_2_key(const std::vector<Index>& var);


/*
    Core TDD functions
*/

// Initialize global variables
TDD Ini_TDD(py::list index_order, py::list uniqTabConfig, bool debug);
// Clear global variables
void Clear_TDD();


// Get identity TDD
TDD get_identity_tdd();


// The unique table query
Node* Find_Or_Add_Unique_table(const keyType& x, const std::vector<Edge>& edges);
// Normalization
Edge normalize(const keyType& x, const std::vector<Edge>& the_successors);


// The get_tdd() function 
TDD get_tdd(TensorArray& U, const std::vector<Index>& var);
// Array to TDD conversion
Edge np_2_tdd(TensorArray* U, const std::vector<uint>& slice, const std::vector<bool>& sliced, const std::vector<keyType>& order);


// TDD to Array conversion
void tdd_2_np(TensorArray* U, const Edge& edge, const keyType& split_pos, const std::vector<uint>& slice, const uint& slice_ptr, std::map<keyType, int>& key_repeat_num);


// Slicing: Simply return the slice as a sub-graph, not changing any weight
Edge Slicing(const Edge& edge, const keyType& x, const int& c);
// Slicing2: Return the sub-graph with weight inherited from father. This way the sub-graph still has accurate amplitude for each leaf
Edge Slicing2(const Edge& edge, const keyType& x, const int& c);


// TDD Addition
Edge add(const Edge& edge1, const Edge& edge2);


// TDD contraction
TDD cont(TDD& tdd1, TDD& tdd2);
Edge contract(const Edge& edge1_in, const Edge& edge2_in, const std::vector<keyType>& key_2_new_key_0, const std::vector<keyType>& key_2_new_key_1, const std::vector<int>& cont_order_0, const std::vector<int>& cont_order_1, const int& cont_num);

#endif //CTDD_HPP
