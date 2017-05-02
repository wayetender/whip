
Getting Started
---
1. These install instructions only work for MacOSX currently (Linux instructions forthcoming). 
2. Install Thrift (https://thrift.apache.org/). 
3. Make sure you have Apple Command-Line tools installed, including gcc and make.
4. Make sure you have Python 2.6 or 2.7 and virtualenv (https://virtualenv.pypa.io/en/latest/) installed. 
5. Run the following command: ```make```
6. For convenience, add ``bin`` to your path: ```export PATH=$PATH:`pwd`/bin```

The **adapter** program can be run by running the command ```adapter``` and the **shim** (connection interposition) preload command can be run on a program by prepending ``shim`` before the command you wish to run. For example to interpose on the ``ping`` command, one would perform the following command: ```shim ping google.com```.

Testing
---

To test that everything works, go to the ``examples/calculator`` directory. Then, activate the calculator Python virtual environment by running ``source ../../env/calculator/bin/activate``. Now you can run the Deacon calculator tests by executing: ``../../bin/shim nosetests test_deacon.py``.

All tests should pass, according to nose. This test suite will do the following for each test case:
 * Create a new calculator server instance (code in ``server.py``)
 * Create a new Deacon network adapter (according to the configuration file in ``adapter.yaml``)
 * Run the test case (each one is in ``test_deacon.py``)
 * Tear down the server instance and network adapter

