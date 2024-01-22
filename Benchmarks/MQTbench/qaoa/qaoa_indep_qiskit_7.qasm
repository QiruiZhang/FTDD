// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[7];
creg meas[7];
creg meas4[7];
h q[0];
h q[1];
h q[2];
rzz(2.27943306873272) q[1],q[2];
h q[3];
rzz(2.27943306873272) q[0],q[3];
h q[4];
rzz(2.27943306873272) q[1],q[4];
rx(1.19793077650078) q[1];
rzz(2.27943306873272) q[2],q[4];
rx(1.19793077650078) q[2];
rzz(-1.1979309781134) q[1],q[2];
rx(1.19793077650078) q[4];
rzz(-1.1979309781134) q[1],q[4];
rx(-11.7042536894514) q[1];
rzz(-1.1979309781134) q[2],q[4];
rx(-11.7042536894514) q[2];
rx(-11.7042536894514) q[4];
h q[5];
rzz(2.27943306873272) q[0],q[5];
rx(1.19793077650078) q[0];
h q[6];
rzz(2.27943306873272) q[3],q[6];
rx(1.19793077650078) q[3];
rzz(-1.1979309781134) q[0],q[3];
rzz(2.27943306873272) q[5],q[6];
rx(1.19793077650078) q[5];
rzz(-1.1979309781134) q[0],q[5];
rx(-11.7042536894514) q[0];
rx(1.19793077650078) q[6];
rzz(-1.1979309781134) q[3],q[6];
rx(-11.7042536894514) q[3];
rzz(-1.1979309781134) q[5],q[6];
rx(-11.7042536894514) q[5];
rx(-11.7042536894514) q[6];
