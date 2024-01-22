// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[8];
creg meas[8];
ry(1.25285343840218) q[0];
ry(-1.7364882536441) q[1];
ry(1.48530489896399) q[2];
ry(-1.56345308205886) q[3];
ry(-1.43462973146741) q[4];
ry(0.000196693154659744) q[5];
ry(-0.738011849323879) q[6];
ry(1.79766289832113) q[7];
cx q[6],q[7];
cx q[5],q[6];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(-1.5707581944127) q[0];
ry(-1.57083702707998) q[1];
ry(1.57074690210627) q[2];
ry(-1.57083897165193) q[3];
ry(-1.57087469514084) q[4];
ry(1.57080717788588) q[5];
ry(2.29568506902468) q[6];
ry(2.97241303170004) q[7];
cx q[6],q[7];
cx q[5],q[6];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(1.57075762197243) q[0];
ry(-0.318012063710521) q[1];
ry(2.97595298759499) q[2];
ry(3.05609214172374) q[3];
ry(-3.13420365273286) q[4];
ry(-3.00543700498182) q[5];
ry(-1.57076084399012) q[6];
ry(-1.41892726504756) q[7];

