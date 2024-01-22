demo:
	python ./TestFTDD/DemoFTDD.py

verify:
	python ./TestFTDD/VerifyFTDD.py > ./TestFTDD/log/VerifyFTDD.log

benchGTN:
	python ./BenchFTDD/BenchGTN.py QAOA
	python ./BenchFTDD/BenchGTN.py VQE
	python ./BenchFTDD/BenchGTN.py EQFT
	python ./BenchFTDD/BenchGTN.py GRQC
	python ./BenchFTDD/BenchGTN.py GHZ
	python ./BenchFTDD/BenchGTN.py GraphState
	python ./BenchFTDD/BenchGTN.py QFT

benchPyTDD:
	python ./BenchFTDD/BenchPyTDD.py GHZ
	python ./BenchFTDD/BenchPyTDD.py GraphState
	python ./BenchFTDD/BenchPyTDD.py QFT
	python ./BenchFTDD/BenchPyTDD.py EQFT
	python ./BenchFTDD/BenchPyTDD.py QAOA
	python ./BenchFTDD/BenchPyTDD.py GRQC

benchQMDD:
	python ./BenchQMDD/BenchQMDD.py GHZ
	python ./BenchQMDD/BenchQMDD.py GraphState
	python ./BenchQMDD/BenchQMDD.py QFT
	python ./BenchQMDD/BenchQMDD.py GRQC
	python ./BenchQMDD/BenchQMDD.py EQFT
	python ./BenchQMDD/BenchQMDD.py VQE

benchFTDD:
	python ./BenchFTDD/BenchFTDD.py GHZ
	python ./BenchFTDD/BenchFTDD.py GraphState
	python ./BenchFTDD/BenchFTDD.py QAOA
	python ./BenchFTDD/BenchFTDD.py VQE
	python ./BenchFTDD/BenchFTDD.py EQFT
	python ./BenchFTDD/BenchFTDD.py QFT
	python ./BenchFTDD/BenchFTDD.py GRQC
