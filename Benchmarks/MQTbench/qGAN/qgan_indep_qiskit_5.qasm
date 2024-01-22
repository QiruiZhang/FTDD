// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg meas[5];
u3(1.9437862,-pi,0) q[0];
u3(1.48411,0,-pi) q[1];
cz q[0],q[1];
u3(1.7482819,-pi,0) q[2];
cz q[0],q[2];
cz q[1],q[2];
u3(1.2414328,0,-pi) q[3];
cz q[0],q[3];
cz q[1],q[3];
cz q[2],q[3];
u3(2.1990288,0,-pi) q[4];
cz q[0],q[4];
ry(1.11436900645458) q[0];
cz q[1],q[4];
ry(5.39361118382088) q[1];
cz q[2],q[4];
ry(1.32503625768938) q[2];
cz q[3],q[4];
ry(1.31242645323765) q[3];
ry(1.79495550702094) q[4];
barrier q[0],q[1],q[2],q[3],q[4];
measure q[0] -> meas[0];
measure q[1] -> meas[1];
measure q[2] -> meas[2];
measure q[3] -> meas[3];
measure q[4] -> meas[4];
