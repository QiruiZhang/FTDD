// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[6];
creg meas[6];
ry(0.0969221017129248) q[0];
ry(0.168468438035128) q[1];
ry(0.0354650220605822) q[2];
ry(1.17710803918365) q[3];
ry(-0.0700233921310761) q[4];
ry(0.908058648702977) q[5];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(1.1269721682698) q[0];
ry(1.52486483649232) q[1];
ry(1.56539099168023) q[2];
ry(1.70233809584903) q[3];
ry(1.7136285725121) q[4];
ry(-2.47803995388745) q[5];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(-2.0125964746234) q[0];
ry(1.46337859736903) q[1];
ry(1.40213462496913) q[2];
ry(1.53545289005977) q[3];
ry(-2.74477512583519) q[4];
ry(-1.61354600013194) q[5];
