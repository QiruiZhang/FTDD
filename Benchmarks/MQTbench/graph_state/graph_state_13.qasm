OPENQASM 2.0;
include "qelib1.inc";
qreg q[13];
creg meas[13];
h q[0];
h q[1];
cz q[0],q[1];
h q[2];
h q[3];
cz q[2],q[3];
h q[4];
h q[5];
cz q[4],q[5];
h q[6];
h q[7];
cz q[6],q[7];
h q[8];
cz q[2],q[8];
h q[9];
cz q[1],q[9];
cz q[7],q[9];
h q[10];
cz q[0],q[10];
cz q[8],q[10];
h q[11];
cz q[4],q[11];
cz q[6],q[11];
h q[12];
cz q[3],q[12];
cz q[5],q[12];
