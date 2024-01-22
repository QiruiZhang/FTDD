// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg meas[5];
ry(-0.00441433244758622) q[0];
ry(-1.57110229841826) q[1];
ry(-0.276537508750218) q[2];
ry(-0.257067648634454) q[3];
ry(-2.04029266378391) q[4];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(-1.57623037380293) q[0];
ry(0.0021409237977971) q[1];
ry(-0.00170351404142829) q[2];
ry(1.03514045015308) q[3];
ry(-1.14753308483808) q[4];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(-1.5678166123219) q[0];
ry(-1.57085219428752) q[1];
ry(1.05052028471095) q[2];
ry(-1.57080876040874) q[3];
ry(1.53217556257542) q[4];
