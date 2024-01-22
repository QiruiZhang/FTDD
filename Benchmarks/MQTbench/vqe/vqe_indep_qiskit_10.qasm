// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[10];
creg meas[10];
ry(-0.89869742590367) q[0];
ry(-1.7409518121022) q[1];
ry(1.69754274749094) q[2];
ry(-2.71429658166189) q[3];
ry(2.22968269970067) q[4];
ry(1.38000054432379) q[5];
ry(3.14143296067184) q[6];
ry(0.00120081526650721) q[7];
ry(-2.14760523725085) q[8];
ry(-0.2303262710509) q[9];
cx q[8],q[9];
cx q[7],q[8];
cx q[6],q[7];
cx q[5],q[6];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(1.56990362690246) q[0];
ry(1.57054108112442) q[1];
ry(1.57075803635614) q[2];
ry(1.57077313979633) q[3];
ry(1.57080591201652) q[4];
ry(1.57056154992889) q[5];
ry(1.57062629635992) q[6];
ry(-1.57070839265365) q[7];
ry(-1.23332918019771) q[8];
ry(1.16478173025836) q[9];
cx q[8],q[9];
cx q[7],q[8];
cx q[6],q[7];
cx q[5],q[6];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(-1.5699218911028) q[0];
ry(0.671950021561325) q[1];
ry(2.9714723382717) q[2];
ry(0.127133625599676) q[3];
ry(-1.143256805346) q[4];
ry(-2.79097432437187) q[5];
ry(2.95091751067348) q[6];
ry(-1.5688701487246) q[7];
ry(-0.490866108304922) q[8];
ry(0.616054854040084) q[9];
