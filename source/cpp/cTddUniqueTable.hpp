/*
 * Original code from MQT DD Package (https://github.com/cda-tum/dd_package)
 * License: MIT license
 * 
 * Modifications by Qirui Zhang (qiruizh@umich.edu) for FTDD (https://github.com/QiruiZhang/FTDD)
 *   - Adapted for TDD
 *   - Changed hash function to FNV
 */


#ifndef CTDDUNIQUETABLE_HPP
#define CTDDUNIQUETABLE_HPP

#include "cTDD.hpp"

#include <numeric>

// Data structure for providing and uniquely storing TDD nodes
template<class Node>
class UniqueTable {

public:
    /*
        Construction/Destruction related functions
    */
    // Construction
    UniqueTable() {}
    explicit UniqueTable(const std::size_t initialGcLimit, const dataType initialGcLur, const std::size_t Nbucket) {
        INITIAL_GC_LIMIT = initialGcLimit;
        INITIAL_GC_LUR = initialGcLur;
        NBUCKET = Nbucket;

        MASK = NBUCKET - 1;
        gcLimit = INITIAL_GC_LIMIT;
    }

    // resize the unique table
    void resize() {
        tables.resize(NBUCKET);
    }
    
    // Release node memory on the available list
    void releaseAvail() {
        // Release available
        Node* current = available;
        while (current) {
            Node* temp = current;
            current = current->next;
            delete temp;
        }
        available = nullptr;
    }

    // Release node memory of the tables
    void releaseTables() {
        for (auto& bucket: tables) { // a bucket in the table
            // Release bucket
            Node* current = bucket;
            while (current) {
                Node* temp = current;
                current = current->next;
                delete temp;
            }
            bucket = nullptr;  
        }
    }

    // Clear everything
    void clear() {
        // clear unique table buckets
        releaseTables();

        // clear available list
        releaseAvail();

        // Reset garbage collection info
        gcRuns  = 0;
        gcLimit = INITIAL_GC_LIMIT;

        // Reset size statistics
        nodeCount     = 0;
        activeNodeCount = 0;
          // Resize lookup statistics
        hits       = 0;
        lookups    = 0;
    };

    // Destruction - release node memory
    ~UniqueTable() {
        releaseTables();
        releaseAvail();
    };
    

    /*
        access functions
    */    
    // Statistics
      // Sizes
    [[nodiscard]] std::size_t   getNodeCount() const                    { return nodeCount; }
    [[nodiscard]] std::size_t   getActiveNodeCount() const              { return activeNodeCount; }
      // Lookup
    [[nodiscard]] std::size_t   getHit() const                          { return hits;}
    [[nodiscard]] std::size_t   getLookups() const                      { return lookups;}
    [[nodiscard]] dataType      hitRatio() const                        { return static_cast<dataType>(hits) / static_cast<dataType>(lookups); }
      // Garbage collection
    [[nodiscard]] std::size_t   getGcruns() const                       { return gcRuns;}
    [[nodiscard]] std::size_t   getGcLimit() const                      { return gcLimit;}


    /*
        Hash functions
    */
    // cTDD hash function: FNV-1a 
    std::size_t hash(const keyType& v, const std::vector<Edge>& edges) {
        hashType hash = fnv_offset_basis;
        
        // hash the integer key
        hash = hash ^ static_cast<hashType>(v);
        hash = hash * fnv_prime;
        
        for (const auto& edge : edges) {
            // hash the out weights
            std::tuple<int, int> weight = get_int_key(edge.weight);
            const unsigned char* bytes = reinterpret_cast<const unsigned char*>(&weight);
            for (std::size_t i = 0; i < sizeof(std::tuple<int, int>); i++) {
                hash = hash ^ static_cast<hashType>(bytes[i]);
                hash = hash * fnv_prime;
            }

            // hash the successor shared pointers
            std::uintptr_t val = reinterpret_cast<std::uintptr_t>(edge.node);
            bytes = reinterpret_cast<const unsigned char*>(&val);
            for (std::size_t i = 0; i < sizeof(std::uintptr_t); i++) {
                hash = hash ^ static_cast<hashType>(bytes[i]);
                hash = hash * fnv_prime;
            }
        }

        return static_cast<std::size_t>(hash & MASK);
    }


    /* 
        Functions for the unique table look up
    */
    // Searches for a node in the hash table with the given key.
    Node* searchTable(const keyType& v, const std::vector<Edge>& edges, const std::size_t& hashVal) {
        Node* pNode = tables[hashVal];
        while (pNode != nullptr) {
            if ((edges == pNode->edges) && (v == pNode->key)) { // if nodes are equal 
                return pNode; 
            }
            pNode = pNode->next;
        }
        // Node not found in bucket
        return nullptr;
    }
    
    // lookup a node in the unique table for the appropriate variable; insert it, if it has not been found
    Node* Find_Or_Add_Unique_table(const keyType& v, const std::vector<Edge>& edges) {
        ++lookups;
        std::size_t hashVal = hash(v, edges);

        // search bucket in table corresponding to hashed value for the given node and return it if found.
        Node* find_node = searchTable(v, edges, hashVal);

        if (find_node != nullptr) { // if found
            ++hits;
            return find_node;
        } else { // if node not found
            // Get a new node
            Node* res = new Node();
            res->key = v;
            res->edges = edges;
            res->refCnt = 0;

            // add the new node to the front of unique table bucket
            res->next = tables[hashVal];
            tables[hashVal] = res;

            ++nodeCount;            
            return res;
        }
    }


    /*
        Functions for garbage collection
    */
    // increment reference counter for node e points to and recursively increment reference counter for each child if this is the first reference
    void incr_ref_count(const Edge& edge) {
        // Check if node is terminal or if ref count already hits max: not proceed in these cases
        if ((edge.node == node_n1) || (edge.node->refCnt == std::numeric_limits<refCntType>::max())) { return; }

        // Increment reference count
        edge.node->refCnt += 1;

        // Increment the reference count of children if it is the first reference for this node 
        if (edge.node->refCnt == 1) {
            for (const auto& edge: edge.node->edges) { incr_ref_count(edge); }
            activeNodeCount++;
        }
    }

    // decrement reference counter for node e points to and recursively decrement reference counter for each child if this is the last reference
    void decr_ref_count(const Edge& edge) {
        // Check if node is terminal or if ref count already hits max: not proceed in these cases
        if ((edge.node == node_n1) || (edge.node->refCnt == std::numeric_limits<refCntType>::max())) { return; }

        // Decrement reference count
        edge.node->refCnt -= 1;

        // Decrement the reference count of children if it is the last reference for this node 
        if (edge.node->refCnt == 0) {
            for (const auto& edge: edge.node->edges) { decr_ref_count(edge); }
            activeNodeCount--;
        }
    }

    // return collected node to the available list
    void returnNode(Node* p) {
        p->next   = available;
        available = p;
    }
    
    // Garbage collection
    std::size_t garbageCollection() {
        // Not collecting if unique table size is still small
        if (nodeCount < gcLimit) { return 0; }
        
        // Start garbage collection for unique table
        gcRuns++;
        std::size_t collected = 0; std::size_t remaining = 0;
        for (auto& bucket: tables) { // a bucket in the table
            Node* pNode = bucket;
            Node* prev = nullptr;
            while (pNode != nullptr) {
                if (pNode->refCnt == 0) { // Collect this node
                    Node* next = pNode->next;
                    if (prev == nullptr) { // head of list
                        bucket = next;
                    } else { // in the middle
                        prev->next = next;
                    }
                    returnNode(pNode);
                    pNode = next;
                    collected++;
                } else { // walk the list
                    prev = pNode;
                    pNode = pNode->next;
                    remaining++;
                }
            }
        }
        
        // Dynamically change the garbage collection limit based on certain heuristics
        if (remaining > gcLimit * INITIAL_GC_LUR) {
            gcLimit = remaining + INITIAL_GC_LIMIT;
        }

        nodeCount = remaining;
        return collected;
    }

private:
    /*
        Initial Parameters
    */
    std::size_t INITIAL_GC_LIMIT; // number of nodes initially used as garbage collection threshold
    dataType INITIAL_GC_LUR; // when 'remained' is larger than this ratio of gcLimit, increase gcLimit with heuristics
    std::size_t NBUCKET; // Number of bucket for the unique table
    std::size_t MASK; // Mask for the hash function

    /*
        unique tables (one per input variable)
    */
    std::vector<Node*> tables{std::vector<Node*>(1, nullptr)}; // unique table

    /*
        The available list
    */
    Node*   available{};

    /* 
        garbage collection statistics and parameters
    */
    std::size_t gcRuns  = 0;
    std::size_t gcLimit;

    /*
        unique table statistics
    */
    std::size_t nodeCount     = 0;
    std::size_t activeNodeCount = 0;
    std::size_t hits       = 0;
    std::size_t lookups    = 0;
};

// Declare the global unique table here
UniqueTable<Node> unique_table;

#endif //CTDDUNIQUETABLE_HPP