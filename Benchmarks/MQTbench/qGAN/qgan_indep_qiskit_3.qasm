// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg meas[3];
u3(2.7702916,-pi,0) q[0];
u3(0.26055497,0,-pi) q[1];
cz q[0],q[1];
u3(3.0295952,-pi,0) q[2];
cz q[0],q[2];
ry(1.85578983194329) q[0];
cz q[1],q[2];
ry(4.54167162188708) q[1];
ry(2.28793740781859) q[2];
barrier q[0],q[1],q[2];
measure q[0] -> meas[0];
measure q[1] -> meas[1];
measure q[2] -> meas[2];
