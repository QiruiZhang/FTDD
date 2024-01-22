// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg meas[4];
creg meas1[4];
h q[0];
h q[1];
rzz(1.57074150607871) q[0],q[1];
h q[2];
rzz(1.57074150607871) q[0],q[2];
rx(7.06858114132728) q[0];
h q[3];
rzz(1.57074150607871) q[1],q[3];
rx(7.06858114132728) q[1];
rzz(5.4978691098325) q[0],q[1];
rzz(1.57074150607871) q[2],q[3];
rx(7.06858114132728) q[2];
rzz(5.4978691098325) q[0],q[2];
rx(-1.57079888179546) q[0];
rx(7.06858114132728) q[3];
rzz(5.4978691098325) q[1],q[3];
rx(-1.57079888179546) q[1];
rzz(5.4978691098325) q[2],q[3];
rx(-1.57079888179546) q[2];
rx(-1.57079888179546) q[3];
