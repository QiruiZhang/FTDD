// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[7];
creg meas[7];
u3(1.8759022,-pi,0) q[0];
u3(0.95171291,0,-pi) q[1];
cz q[0],q[1];
u3(2.4383797,-pi,0) q[2];
cz q[0],q[2];
cz q[1],q[2];
u3(0.56063141,-pi,0) q[3];
cz q[0],q[3];
cz q[1],q[3];
cz q[2],q[3];
u3(0.81865609,0,-pi) q[4];
cz q[0],q[4];
cz q[1],q[4];
cz q[2],q[4];
cz q[3],q[4];
u3(1.5713159,0,-pi) q[5];
cz q[0],q[5];
cz q[1],q[5];
cz q[2],q[5];
cz q[3],q[5];
cz q[4],q[5];
u3(1.5610757,-pi,0) q[6];
cz q[0],q[6];
ry(2.09289131011357) q[0];
cz q[1],q[6];
ry(3.67515491196704) q[1];
cz q[2],q[6];
ry(6.06198943432309) q[2];
cz q[3],q[6];
ry(5.59792636151934) q[3];
cz q[4],q[6];
ry(4.27886201355312) q[4];
cz q[5],q[6];
ry(5.72927798681584) q[5];
ry(2.07940629659558) q[6];
barrier q[0],q[1],q[2],q[3],q[4],q[5],q[6];
measure q[0] -> meas[0];
measure q[1] -> meas[1];
measure q[2] -> meas[2];
measure q[3] -> meas[3];
measure q[4] -> meas[4];
measure q[5] -> meas[5];
measure q[6] -> meas[6];
