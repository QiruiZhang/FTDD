// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[7];
creg meas[7];
ry(-3.70395916395932e-5) q[0];
ry(-0.00442170039621071) q[1];
ry(-1.55897493542046) q[2];
ry(-0.170617652126909) q[3];
ry(0.0010625623385633) q[4];
ry(1.80257271848602) q[5];
ry(-1.61289835045308) q[6];
cx q[5],q[6];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(8.63071429435558e-5) q[0];
ry(0.0369544539206155) q[1];
ry(-1.11372231178174) q[2];
ry(1.107852001637) q[3];
ry(-0.139147581576273) q[4];
ry(0.230032295980412) q[5];
ry(-0.00956505160530256) q[6];
cx q[5],q[6];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(pi) q[0];
ry(2.81042969370367) q[1];
ry(1.12422995166413) q[2];
ry(0.0767570835250667) q[3];
ry(1.80145346752936) q[4];
ry(-1.57291053028464) q[5];
ry(-1.52970951586615) q[6];
