OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg meas[2];
h q[1];
cx q[1],q[0];
h q[1];
cp(pi/2) q[1],q[0];
h q[0];
swap q[0],q[1];