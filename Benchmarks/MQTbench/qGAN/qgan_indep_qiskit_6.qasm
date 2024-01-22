// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[6];
creg meas[6];
u3(1.3500331,-pi,0) q[0];
u3(0.78625794,-pi,0) q[1];
cz q[0],q[1];
u3(0.22841666,0,-pi) q[2];
cz q[0],q[2];
cz q[1],q[2];
u3(1.0769188,-pi,0) q[3];
cz q[0],q[3];
cz q[1],q[3];
cz q[2],q[3];
u3(0.59782258,0,-pi) q[4];
cz q[0],q[4];
cz q[1],q[4];
cz q[2],q[4];
cz q[3],q[4];
u3(1.591018,0,-pi) q[5];
cz q[0],q[5];
ry(3.94248685615585) q[0];
cz q[1],q[5];
ry(4.63074690329306) q[1];
cz q[2],q[5];
ry(0.787631193173361) q[2];
cz q[3],q[5];
ry(1.58641526847451) q[3];
cz q[4],q[5];
ry(2.80130870428177) q[4];
ry(4.05354585996659) q[5];
barrier q[0],q[1],q[2],q[3],q[4],q[5];
measure q[0] -> meas[0];
measure q[1] -> meas[1];
measure q[2] -> meas[2];
measure q[3] -> meas[3];
measure q[4] -> meas[4];
measure q[5] -> meas[5];
