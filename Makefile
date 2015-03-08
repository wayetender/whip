
all: shim adapter

clean: clean-shim

adapter:
	rm -rf env/adapter
	make env/adapter

env/adapter:
	virtualenv env/adapter
	sh ./env/adapter/bin/activate
	pip install -r src/adapter/requirements.txt

clean-shim:
	cd src/shim/mac; make clean

shim: 
	cd src/shim/mac; make

