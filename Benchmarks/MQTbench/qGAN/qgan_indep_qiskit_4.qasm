// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg meas[4];
u3(2.3785177,0,-pi) q[0];
u3(2.1163024,0,-pi) q[1];
cz q[0],q[1];
u3(1.9092638,0,-pi) q[2];
cz q[0],q[2];
cz q[1],q[2];
u3(1.3988232,0,-pi) q[3];
cz q[0],q[3];
ry(3.70292529015534) q[0];
cz q[1],q[3];
ry(5.33480089540019) q[1];
cz q[2],q[3];
ry(3.61888275109019) q[2];
ry(4.08909515046414) q[3];
barrier q[0],q[1],q[2],q[3];
measure q[0] -> meas[0];
measure q[1] -> meas[1];
measure q[2] -> meas[2];
measure q[3] -> meas[3];
