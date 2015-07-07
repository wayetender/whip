
all: adapter shim env/calculator env/chess env/calculator_thrift env/evernote

clean: clean-shim clean-env

adapter: env/adapter src/adapter/parsetab.py
	./src/adapter/update-stubs.sh

src/adapter/parsetab.py: src/adapter/parser.py
	./src/adapter/regen-parser.sh

env/adapter:
	virtualenv env/adapter
	source ./env/adapter/bin/activate; pip install -r src/adapter/requirements.txt

env/calculator:
	virtualenv env/calculator
	source ./env/calculator/bin/activate; pip install -r examples/calculator/requirements.txt

env/chess:
	virtualenv env/chess
	source ./env/chess/bin/activate; pip install -r examples/chess/requirements.txt

env/calculator_thrift:
	virtualenv env/calculator_thrift
	source ./env/calculator_thrift/bin/activate; pip install -r examples/calculator_thrift/requirements.txt

env/evernote:
	virtualenv env/evernote
	source ./env/evernote/bin/activate; pip install -r examples/evernote/requirements.txt

clean-shim:
	cd src/shim/mac; make clean

clean-env:
	rm -rf env/*

shim: adapter
	cd src/shim/mac; make

