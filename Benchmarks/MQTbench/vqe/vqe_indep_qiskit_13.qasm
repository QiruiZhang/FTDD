// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[13];
creg meas[13];
ry(8.47872152363211e-5) q[0];
ry(-1.6506288499806) q[1];
ry(1.57074783443878) q[2];
ry(-1.57071286721974) q[3];
ry(2.82020680552581) q[4];
ry(-1.57286667792795) q[5];
ry(0.000550943102259616) q[6];
ry(1.57063697088532) q[7];
ry(1.52939289711583) q[8];
ry(-pi) q[9];
ry(-2.51136526425652) q[10];
ry(3.03580612251713) q[11];
ry(-2.23818028818282) q[12];
cx q[11],q[12];
cx q[10],q[11];
ry(1.67359099392493) q[11];
ry(2.47689738997678) q[12];
cx q[11],q[12];
ry(1.63632558792906) q[12];
cx q[9],q[10];
ry(1.51042583861191) q[10];
cx q[10],q[11];
ry(-2.19865670571468) q[11];
cx q[8],q[9];
cx q[7],q[8];
cx q[6],q[7];
cx q[5],q[6];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(-3.14157994029671) q[0];
ry(-1.57080583155587) q[1];
ry(1.57058104699851) q[2];
ry(-1.57070283737176) q[3];
ry(-1.57069866538547) q[4];
ry(-1.57202040673608) q[5];
ry(1.56954124324391) q[6];
ry(-3.02021146568054) q[7];
ry(-3.13644421459758) q[8];
ry(3.14152425901778) q[9];
cx q[9],q[10];
ry(1.57079776909701) q[10];
cx q[8],q[9];
cx q[7],q[8];
cx q[6],q[7];
cx q[5],q[6];
cx q[4],q[5];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
ry(-3.14158717696147) q[0];
ry(1.57083506888811) q[1];
ry(-0.0797915870437049) q[2];
ry(-3.14156389486068) q[3];
ry(6.07037439007604e-5) q[4];
ry(-1.89229534057855) q[5];
ry(-0.00210120027167094) q[6];
ry(1.57025568843598) q[7];
ry(1.6123661124711) q[8];
ry(-1.44912713548782) q[9];
