// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg meas[4];
ry(-3.06308642559242) q[0];
ry(2.72340535390947) q[1];
ry(0.265311444342159) q[2];
ry(0.514277021350485) q[3];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(-0.626185121622286) q[0];
ry(-1.50946128815491) q[1];
ry(-1.47510618895348) q[2];
ry(-2.08850927511392) q[3];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(0.626161051104292) q[0];
ry(-1.70448256544942) q[1];
ry(1.15402592474415) q[2];
ry(-1.8017500381226) q[3];
