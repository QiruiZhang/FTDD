// Benchmark was created by MQT Bench on 2022-12-15
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.2.2
// Qiskit version: {'qiskit-terra': '0.22.3', 'qiskit-aer': '0.11.1', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.2', 'qiskit': '0.39.3', 'qiskit-nature': '0.5.1', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.4.0', 'qiskit-machine-learning': '0.5.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[10];
creg meas[10];
creg meas7[10];
h q[0];
h q[1];
rzz(5.62745313017023) q[0],q[1];
h q[2];
h q[3];
rzz(5.62745313017023) q[1],q[3];
rx(10.6675751897493) q[1];
h q[4];
rzz(5.62745313017023) q[3],q[4];
rx(10.6675751897493) q[3];
h q[5];
h q[6];
rzz(5.62745313017023) q[0],q[6];
rx(10.6675751897493) q[0];
rzz(1.89875694625042) q[0],q[1];
rzz(1.89875694625042) q[1],q[3];
rx(-11.9105230837702) q[1];
rzz(5.62745313017023) q[2],q[6];
rx(10.6675751897493) q[6];
rzz(1.89875694625042) q[0],q[6];
rx(-11.9105230837702) q[0];
h q[7];
rzz(5.62745313017023) q[5],q[7];
h q[8];
rzz(5.62745313017023) q[2],q[8];
rx(10.6675751897493) q[2];
rzz(1.89875694625042) q[2],q[6];
rzz(5.62745313017023) q[4],q[8];
rx(10.6675751897493) q[4];
rzz(1.89875694625042) q[3],q[4];
rx(-11.9105230837702) q[3];
rx(-11.9105230837702) q[6];
rx(10.6675751897493) q[8];
rzz(1.89875694625042) q[2],q[8];
rx(-11.9105230837702) q[2];
rzz(1.89875694625042) q[4],q[8];
rx(-11.9105230837702) q[4];
rx(-11.9105230837702) q[8];
h q[9];
rzz(5.62745313017023) q[5],q[9];
rx(10.6675751897493) q[5];
rzz(5.62745313017023) q[7],q[9];
rx(10.6675751897493) q[7];
rzz(1.89875694625042) q[5],q[7];
rx(10.6675751897493) q[9];
rzz(1.89875694625042) q[5],q[9];
rx(-11.9105230837702) q[5];
rzz(1.89875694625042) q[7],q[9];
rx(-11.9105230837702) q[7];
rx(-11.9105230837702) q[9];
