// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[12];
creg meas[12];
ry(3.14153545257561) q[0];
ry(0.000226703978131976) q[1];
ry(pi) q[2];
ry(0.00012024018637239) q[3];
ry(1.57078499759457) q[4];
ry(-1.57061923266505) q[5];
ry(1.57093634522112) q[6];
ry(pi) q[7];
ry(-1.57062660946303) q[8];
ry(1.23250959259517) q[9];
ry(-2.25771157312621) q[10];
ry(-0.82572227056113) q[11];
cx q[10],q[11];
ry(2.379960205758) q[11];
cx q[9],q[10];
ry(0.505941497412654) q[10];
cx q[10],q[11];
ry(0.977076511044131) q[11];
cx q[8],q[9];
cx q[7],q[8];
cx q[6],q[7];
cx q[5],q[6];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(-1.57095149983023) q[0];
ry(1.57075590435464) q[1];
ry(1.57092103325607) q[2];
ry(1.57075453051658) q[3];
ry(-0.000113827444642108) q[4];
ry(4.58063856985872e-5) q[5];
ry(-8.91330576574898e-5) q[6];
ry(pi) q[7];
ry(-1.47520771549156e-5) q[8];
ry(pi) q[9];
cx q[9],q[10];
ry(-1*pi/2) q[10];
cx q[8],q[9];
cx q[7],q[8];
cx q[6],q[7];
cx q[5],q[6];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(1.57085062525908) q[0];
ry(1.57079966071963) q[1];
ry(1.57064599552246) q[2];
ry(1.57081045625029) q[3];
ry(1.57085214735697) q[4];
ry(-0.40925908897565) q[5];
ry(-1.57071543533121) q[6];
ry(-2.73232467081104) q[7];
ry(1.57056980246295) q[8];
ry(1.02789334753149) q[9];

