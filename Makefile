
all: adapter shim env/calculator

clean: clean-shim clean-env

adapter:
	make env/adapter
	./src/adapter/update-stubs.sh

env/adapter:
	virtualenv env/adapter
	source ./env/adapter/bin/activate; pip install -r src/adapter/requirements.txt

env/calculator:
	virtualenv env/calculator
	source ./env/calculator/bin/activate; pip install -r examples/calculator/requirements.txt

clean-shim:
	cd src/shim/mac; make clean

clean-env:
	rm -rf env/*

shim: adapter
	cd src/shim/mac; make

