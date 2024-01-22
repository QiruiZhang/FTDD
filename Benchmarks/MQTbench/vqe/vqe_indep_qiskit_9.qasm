// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[9];
creg meas[9];
ry(pi) q[0];
ry(1.57261772004661) q[1];
ry(-pi) q[2];
ry(-3.01838803657747) q[3];
ry(-3.14153155413412) q[4];
ry(1.57081225587411) q[5];
ry(-0.000249300581520663) q[6];
ry(2.81553307757639) q[7];
ry(2.60349915626892) q[8];
cx q[7],q[8];
cx q[6],q[7];
cx q[5],q[6];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(-0.00404055380991485) q[0];
ry(2.87873523866084) q[1];
ry(-0.26287666309335) q[2];
ry(1.57064584408371) q[3];
ry(-1.57086999734911) q[4];
ry(-3.14138658100031) q[5];
ry(-3.14147879894335) q[6];
ry(1.74237293497798) q[7];
ry(-2.1331555266772) q[8];
cx q[7],q[8];
cx q[6],q[7];
cx q[5],q[6];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(0.0041151432205396) q[0];
ry(1.57273032004285) q[1];
ry(-3.14153820358691) q[2];
ry(1.57085774963396) q[3];
ry(1.44707754980487) q[4];
ry(-2.82870394249939) q[5];
ry(-5.22562245909442e-5) q[6];
ry(1.57075046259682) q[7];
ry(1.84942802319205) q[8];
