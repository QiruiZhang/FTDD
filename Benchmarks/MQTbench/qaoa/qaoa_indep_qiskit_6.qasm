// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[6];
creg meas[6];
creg meas3[6];
h q[0];
h q[1];
h q[2];
rzz(5.62724885812889) q[0],q[2];
h q[3];
rzz(5.62724885812889) q[0],q[3];
rx(-5.04047412391158) q[0];
h q[4];
rzz(5.62724885812889) q[1],q[4];
rzz(5.62724885812889) q[2],q[4];
rx(-5.04047412391158) q[2];
rzz(-4.38434633329271) q[0],q[2];
rx(-5.04047412391158) q[4];
h q[5];
rzz(5.62724885812889) q[1],q[5];
rx(-5.04047412391158) q[1];
rzz(-4.38434633329271) q[1],q[4];
rzz(-4.38434633329271) q[2],q[4];
rx(-5.62738622902127) q[2];
rzz(5.62724885812889) q[3],q[5];
rx(-5.04047412391158) q[3];
rzz(-4.38434633329271) q[0],q[3];
rx(-5.62738622902127) q[0];
rx(-5.62738622902127) q[4];
rx(-5.04047412391158) q[5];
rzz(-4.38434633329271) q[1],q[5];
rx(-5.62738622902127) q[1];
rzz(-4.38434633329271) q[3],q[5];
rx(-5.62738622902127) q[3];
rx(-5.62738622902127) q[5];
