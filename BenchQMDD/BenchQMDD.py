''' This script benchmarks QMDD '''
# System
import sys
import signal
import time
from math import ceil
import pandas as pd

# Import Qiskit
from qiskit import QuantumCircuit, execute

# Import QMDD
from mqt.ddsim.qasmsimulator import QasmSimulatorBackend
from mqt.ddsim.unitarysimulator import UnitarySimulatorBackend


''' Import benchmarks '''
try:
    case = sys.argv[1]
    print(case)
except:
    print("Please provide the case you want to test!")
    sys.exit()

if case == "GHZ":
    import TestCases.TestGHZ as TestCases 
elif case == "GraphState":
    import TestCases.TestGraphState as TestCases
elif case == "QFT":
    import TestCases.TestQFT as TestCases
elif case == "EQFT":
    import TestCases.TestEQFT as TestCases
elif case == "QAOA":
    import TestCases.TestQAOA as TestCases
elif case == "VQE":
    import TestCases.TestVQE as TestCases
elif case == "GRQC":
    import TestCases.TestGRQC as TestCases
else:
    print("Please provide a valid case!")
    sys.exit()


"""
    Utility
"""
# Function to handle the alarm
def handle_alarm(signum, frame):
    raise TimeoutError()

# Set the signal handler
signal.signal(signal.SIGALRM, handle_alarm)

# Logger
class Logger(object):
    def __init__(self, filename="logfile.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

sys.stdout = Logger("./BenchQMDD/log/BenchQMDD_" + case + ".log")


"""
    Global Initializations
"""
qubit_num_limit = 30
perf_meas_time = 2
meas_max_iter = 20
time_limit = 3600

list_circuit_name = []
list_qmdd_time = []


"""
    Loop all the benchmarks
"""
path = TestCases.path
for file in TestCases.benchmarks:
    error = False
    print("Benchmarking " + file[0] + "......")
    file_name = path + file[0]
    open_input = file[1]

    list_circuit_name.append(file[0])


    '''
        Run QMDD qasm mode 
    '''
    if (not open_input):
        print("Simulating circuit with QMDDs......")

        # Transpile circuit 
        cir = QuantumCircuit.from_qasm_file(file_name)
        backend = QasmSimulatorBackend()

        # Simulate
        signal.alarm(time_limit)
        try:
            # first time meas
            t1 = time.perf_counter()
            result = execute(cir, backend, approximation_step_fidelity=0.999999, approximation_steps=1, shots=1).result()
            t2 = time.perf_counter()
            dt = t2 - t1
            # refine time meas
            if dt < perf_meas_time:
                N = min(ceil(perf_meas_time/dt), meas_max_iter)
                t1 = time.perf_counter()
                for i in range(N):
                    result = execute(cir, backend, approximation_step_fidelity=0.999999, approximation_steps=1, shots=1).result()
                t2 = time.perf_counter()
                dt = (t2 - t1)/N
            print("QMDD simulation finished with time, ", dt, "s")
            list_qmdd_time.append(dt)
        except TimeoutError:
            list_qmdd_time.append('T.O.')
            print("QMDD simulation timed out!")
        except Exception as e:
            list_qmdd_time.append('R.E.')
            print(f"Caught an exception: {e}")
        finally:
            signal.alarm(0)
    else:
        print("Simulating circuit with QMDDs......")

        # Transpile circuit 
        cir = QuantumCircuit.from_qasm_file(file_name)
        backend = UnitarySimulatorBackend()

        # Simulate
        signal.alarm(time_limit)
        try:
            # first time meas
            t1 = time.perf_counter()
            result = execute(cir, backend, mode='sequential').result()
            t2 = time.perf_counter()
            dt = t2 - t1
            # refine time meas
            if dt < perf_meas_time:
                N = min(ceil(perf_meas_time/dt), meas_max_iter)
                t1 = time.perf_counter()
                for i in range(N):
                    result = execute(cir, backend, mode='sequential').result()
                t2 = time.perf_counter()
                dt = (t2 - t1)/N
            print("QMDD simulation finished with time, ", dt, "s")
            list_qmdd_time.append(dt)
        except TimeoutError:
            list_qmdd_time.append('T.O.')
            print("QMDD simulation timed out!")
        except Exception as e:
            list_qmdd_time.append('R.E.')
            print(f"Caught an exception: {e}")
        finally:
            signal.alarm(0)
    
    print('\n')


''' Generate the benchmarking results and save to .csv '''
dict_bench = {
    "Circuit Name":                 list_circuit_name,
    "QMDD CPU Time (s)":             list_qmdd_time  
}

res_path = "./BenchQMDD/data/"
res_csv_name = (
            res_path
            + "BenchQMDD_" + case
            + ".csv"
        )
df_bench = pd.DataFrame(dict_bench)
df_bench.to_csv(res_csv_name)
