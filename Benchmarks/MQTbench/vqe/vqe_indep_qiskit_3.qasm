// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg meas[3];
ry(3.00231423540239) q[0];
ry(-1.21899651342842) q[1];
ry(-1.72136960138738) q[2];
cx q[1],q[2];
cx q[0],q[1];
ry(-2.98984261049184) q[0];
ry(-2.07112433416928) q[1];
ry(-1.71950714088383) q[2];
cx q[1],q[2];
cx q[0],q[1];
ry(-0.12419233549569) q[0];
ry(0.38539577554438) q[1];
ry(0.248149363459937) q[2];
