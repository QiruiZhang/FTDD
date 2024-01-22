// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg meas[5];
creg meas2[5];
h q[0];
h q[1];
rzz(-3.66638380291587) q[0],q[1];
h q[2];
rzz(-3.66638380291587) q[0],q[2];
rx(-2.03854567383379) q[0];
h q[3];
rzz(-3.66638380291587) q[1],q[3];
rx(-2.03854567383379) q[1];
rzz(2.03847737548037) q[0],q[1];
h q[4];
rzz(-3.66638380291587) q[2],q[4];
rx(-2.03854567383379) q[2];
rzz(2.03847737548037) q[0],q[2];
rx(-12.0417655497439) q[0];
rzz(-3.66638380291587) q[3],q[4];
rx(-2.03854567383379) q[3];
rzz(2.03847737548037) q[1],q[3];
rx(-12.0417655497439) q[1];
rx(-2.03854567383379) q[4];
rzz(2.03847737548037) q[2],q[4];
rx(-12.0417655497439) q[2];
rzz(2.03847737548037) q[3],q[4];
rx(-12.0417655497439) q[3];
rx(-12.0417655497439) q[4];