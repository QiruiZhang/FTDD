/*
 * Original code from MQT DD Package (https://github.com/cda-tum/dd_package)
 * License: MIT license
 * 
 * Modifications by Qirui Zhang (qiruizh@umich.edu) for FTDD (https://github.com/QiruiZhang/FTDD)
 *   - Adapted for TDD
 *   - Changed hash function to FNV
 */


#ifndef CTDDCOMPUTEDTABLE_HPP
#define CTDDCOMPUTEDTABLE_HPP

#include "cTDD.hpp"


/*
    Data structure for caching addition computed results
*/
class AddComputedCache {

public:
    /*
        Construction/Destruction related functions
    */
    // Construction
    AddComputedCache() {}
    AddComputedCache(std::size_t Nbucket) {
        NBUCKET = Nbucket;
        MASK = NBUCKET - 1;
        table.resize(NBUCKET);
    }

    // clear everything
    void clear() {
        for (auto& entry: table) {
            entry.res.node = nullptr;
        }
    }


    /*
        access functions
    */
    [[nodiscard]] std::size_t   getCount() const        { return NBUCKET; }
    [[nodiscard]] std::size_t   getHit() const          { return hits; }
    [[nodiscard]] std::size_t   getLookups() const      { return lookups; }
    [[nodiscard]] dataType      hitRatio() const        { return static_cast<dataType>(hits) / static_cast<dataType>(lookups); }


    /*
        Hash functions
    */
    // FNV-1a
    std::size_t hash(const Edge& edge1, const Edge& edge2) {
        hashType hash = fnv_offset_basis;

        // hash the out weights
        std::tuple<int, int> weight = get_int_key(edge1.weight);
        const unsigned char* bytes = reinterpret_cast<const unsigned char*>(&weight);
        for (std::size_t i = 0; i < sizeof(std::tuple<int, int>); i++) { hash = ( hash ^ static_cast<hashType>(bytes[i]) ) * fnv_prime; }
        weight = get_int_key(edge2.weight);
        bytes = reinterpret_cast<const unsigned char*>(&weight);
        for (std::size_t i = 0; i < sizeof(std::tuple<int, int>); i++) { hash = ( hash ^ static_cast<hashType>(bytes[i]) ) * fnv_prime; }

        // hash the successor shared pointers
        std::uintptr_t val = reinterpret_cast<std::uintptr_t>(edge1.node);
        bytes = reinterpret_cast<const unsigned char*>(&val);
        for (std::size_t i = 0; i < sizeof(std::uintptr_t); i++) { hash = ( hash ^ static_cast<hashType>(bytes[i]) ) * fnv_prime; }
        val = reinterpret_cast<std::uintptr_t>(edge2.node);
        bytes = reinterpret_cast<const unsigned char*>(&val);
        for (std::size_t i = 0; i < sizeof(std::uintptr_t); i++) { hash = ( hash ^ static_cast<hashType>(bytes[i]) ) * fnv_prime; }

        return static_cast<std::size_t>(hash & MASK);
    }


    /* 
        Functions for the computed cache look up
    */
    // Insert an entry to the computed cache
    void insert(const Edge& edge1, const Edge& edge2, const Edge& res) {
        std::size_t hashVal = hash(edge1, edge2);
        table[hashVal]     = {edge1, edge2, res};
    }

    // Find an entry in the computed cache
    Edge find(const Edge& edge1, const Edge& edge2) {
        lookups++;
        
        // Find edge1 op edge2
        std::size_t hashVal = hash(edge1, edge2);
        Entry      entry = table[hashVal];
        if ((entry.res.node != nullptr) && (entry.edge1 == edge1) && (entry.edge2 == edge2)) { // found 
            hits++;
            return entry.res;
        }

        // Find edge2 op edge1
        hashVal = hash(edge2, edge1);
        entry = table[hashVal];
        if ((entry.res.node != nullptr) && (entry.edge1 == edge2) && (entry.edge2 == edge1)) { // found 
            hits++;
            return entry.res;
        }

        return Edge();
    }

private:
    // Cache entry
    struct Entry {
        Edge    edge1;
        Edge    edge2;
        Edge    res;
    };

    // computed cache
    std::size_t NBUCKET;
    std::vector<Entry> table{std::vector<Entry>(0)};
    std::size_t MASK;

    // lookup statistics
    std::size_t hits    = 0;
    std::size_t lookups = 0;
};


/*
    Data structure for caching contraction computed results
*/
class ContComputedCache {

public:
    /*
        Construction/Destruction related functions
    */
    // Construction
    ContComputedCache() {}
    ContComputedCache(std::size_t Nbucket) {
        NBUCKET = Nbucket;
        MASK = NBUCKET - 1;
        table.resize(NBUCKET);
    }

    // clear everything
    void clear() {
        for (auto& entry: table) {
            entry.res.node = nullptr;
        }
    }


    /*
        access functions
    */
    [[nodiscard]] std::size_t   getCount() const        { return NBUCKET; }
    [[nodiscard]] std::size_t   getHit() const          { return hits; }
    [[nodiscard]] std::size_t   getLookups() const      { return lookups; }
    [[nodiscard]] dataType      hitRatio() const        { return static_cast<dataType>(hits) / static_cast<dataType>(lookups); }


    /*
        Hash functions
    */
    // FNV-1a
    std::size_t hash(Node* node1, Node* node2, const std::vector<keyType>& key_2_new_key_1, const std::vector<keyType>& key_2_new_key_2) {
        hashType hash = fnv_offset_basis;

        // hash the node shared pointers
        std::uintptr_t val = reinterpret_cast<std::uintptr_t>(node1);
        const unsigned char* bytes = reinterpret_cast<const unsigned char*>(&val);
        for (std::size_t i = 0; i < sizeof(std::uintptr_t); i++) { hash = ( hash ^ static_cast<hashType>(bytes[i]) ) * fnv_prime; }
        val = reinterpret_cast<std::uintptr_t>(node2);
        bytes = reinterpret_cast<const unsigned char*>(&val);
        for (std::size_t i = 0; i < sizeof(std::uintptr_t); i++) { hash = ( hash ^ static_cast<hashType>(bytes[i]) ) * fnv_prime; }

        // hash key_2_new_key_1
        for (const auto& val : key_2_new_key_1) { hash = ( hash ^ static_cast<hashType>(val) ) * fnv_prime; }

        // hash_key_2_new_key_2
        for (const auto& val : key_2_new_key_2) { hash = ( hash ^ static_cast<hashType>(val) ) * fnv_prime; }

        return static_cast<std::size_t>(hash & MASK);
    }


    /* 
        Functions for the computed cache look up
    */
    // Insert an entry to the computed cache
    void insert(Node* node1, Node* node2, const std::vector<keyType>& key_2_new_key_1, const std::vector<keyType>& key_2_new_key_2, const Edge& res) {
        std::size_t hashVal = hash(node1, node2, key_2_new_key_1, key_2_new_key_2);
        table[hashVal]     = {node1, node2, key_2_new_key_1, key_2_new_key_2, res};
    }

    // Find an entry in the computed cache
    Edge find(Node* node1, Node* node2, const std::vector<keyType>& key_2_new_key_1, const std::vector<keyType>& key_2_new_key_2) {
        lookups++;
        
        // Find edge1 op edge2
        std::size_t hashVal = hash(node1, node2, key_2_new_key_1, key_2_new_key_2);
        Entry      entry = table[hashVal];
        if ((entry.res.node != nullptr) && (entry.node1 == node1) && (entry.node2 == node2) && (entry.key_2_new_key_1 == key_2_new_key_1) && (entry.key_2_new_key_2 == key_2_new_key_2)) { // found 
            hits++;
            return entry.res;
        }

        // Find edge2 op edge1
        hashVal = hash(node2, node1, key_2_new_key_2, key_2_new_key_1);
        entry = table[hashVal];
        if ((entry.res.node != nullptr) && (entry.node2 == node1) && (entry.node1 == node2) && (entry.key_2_new_key_2 == key_2_new_key_1) && (entry.key_2_new_key_1 == key_2_new_key_2)) { // found 
            hits++;
            return entry.res;
        }

        return Edge();
    }

private:
    // Cache entry
    struct Entry {
        Node*   node1;
        Node*   node2;
        std::vector<keyType> key_2_new_key_1;
        std::vector<keyType> key_2_new_key_2;
        Edge    res;
    };

    // computed cache
    std::size_t NBUCKET;
    std::vector<Entry> table{std::vector<Entry>(0)};
    std::size_t MASK;

    // lookup statistics
    std::size_t hits    = 0;
    std::size_t lookups = 0;
};


/*
    Declare the global computed caches here
*/
AddComputedCache add_computed_table;
ContComputedCache cont_computed_table;

#endif //CTDDCOMPUTEDTABLE_HPP
