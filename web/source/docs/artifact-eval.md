---
layout: "docs"
page_title: "Overview of the Artifact"
sidebar_current: "artifact-eval"
description: ICFP Paper Artifact Evaluation
---

# Overview of the Artifact

This is the overview document for the Whip artifact (paper #58).
This document's intended audience is the ICFP 2017 artifact evaluators.

As prescribed by the Artifact Submission instructions, we have broken this 
document in two sections: a [Getting Started](#getting-started) guide, which 
describes the setup instructions and basic testing, and an [Evaluation](#evaluation)
section, which gives step-by-step instructions for how to evaluate the artifact.

## Getting Started

The artifact provided to you contains the following assets:

* `whip` subdirectory: `v0.1.0` tag of the Whip Git repository, which includes: 
	* the static documentation website, located in the `web` subdirectory. You can 
		view this document on your browser by opening 
		`web/build/docs/artifact-eval.html` in your browser.
	* the Whip source code, located in the `whip` subdirectory.
	* the Whip benchmarks located in the `benchmarks` subdirectory` 
		as described in Sections 6 and 7 of the paper.
* `docker-images` subdirectory: the pre-built Docker container for the Whip source
	code.
* `whip-calculator-example` subdirectory: a simple Thrift microservices application 
	used to show how Whip works in a simplified setting and in particular to 
	demonstrate high-order contract checking as described in the paper.
* `overview.html`: this document, in simplified HTML format.

### Online Resources

For the latest version of Whip, feel free to look at the following online resources:

* **[Whip Github Repository](https://github.com/wayetender/whip)** which
	hosts the Whip Git repository. The code provided in the artifact can be found
	online in the `v0.1.0` tag.
* **[Docker Hub Whip Repository](https://hub.docker.com/r/wayetender/whip/)** 
	which contains automatically-built Docker images based on the above Github repo.
* **[Whip Calculator Quickstart](https://github.com/wayetender/whip-calculator-example)**
	which hosts the Calculator quickstart tutorial described above.
* **[Whip website](http://whip.services)** which is Whip's website that is simply
	an easily-accessible version of the `web` directory of the Git repository.

### Prerequisites

To run the benchmarks, you will need to have a recent version of Docker installed 
on your computer. The artifact was developed using
Docker version 17.03.1-ce, build c6d412e. For instructions on downloading
and installing Docker, please see 
[https://www.docker.com/get-docker](https://www.docker.com/get-docker).

You must also be comfortable using a UNIX-like terminal with a modern shell (e.g.,
bash). Though the steps should reasonably work on a Windows-based operating system
(as most of the functionality of Whip is contained in a Docker container), it has 
not been tested on one.

### Installation

To start using Whip you must first create the Whip base image. The base image
contains the Whip adapter and interposition library described in the 
beginning of Section 6 of the paper. We refer to the interposition library
in this document and in the source code simply as the _shim_. 

We provide you with three ways to create the Whip base image: either by building
the container manually from source, or by importing the image directly, or
by pulling from the Docker Hub.
We note that building the container manually, which can be done in one command,
is computationally intensive and can take upwards of 30 minutes. In contrast,
importing the image directly takes seconds.

* **Option 1:** Manually building the base image

	Change your working directory to the `whip/whip` subdirectory (i.e.,
	where the `Dockerfile` file is contained) and perform the following command:

	```
	docker build -t wayetender/whip .
	```

* **Option 2:** Importing the supplied base image

	Change your working directory to the `docker-images` subdirectory (i.e.,
	where the `whip.tar` file is contained) and perform the following command:

	```
	docker load -i whip.tar
	```

* **Option 3:** From the Docker Hub

	Though seemingly not recommended by the AEC (as it is an online resource), 
	the preferred technique to load a Docker container is to pull the image 
	from the Docker Hub.

	```
	docker pull wayetender/whip:v0.1.0 
	```

You can test the image was installed correctly by running the `adapter`
command inside the container. That is, you should see be able to reproduce
the following output on your computer.

```
$ docker run wayetender/whip adapter
usage: adapter [adapterconfigfile.yaml]
```

Once the base image is installed, you can now _evaluate_ the artifact, which
we describe in the next section.

## Evaluation

In this section we propose how to evalute this artifact. 

We believe that the artifact should be evaluated with two criteria. First, it should
be evaluated on its ability to monitor services with the contract language 
described in Section 2. In particular, it should demonstrate transparent 
interception and inspection on the contents of messages 
(i.e., treating the services as black boxes without requiring code changes) and
also the ability to correctly report blame. Second, the artifact should faithfully
demonstrate the performance evaluation result trends described in Figure 11 
and Section 7 of the paper. 

To show the first criterion, we will perform a step-by-step tutorial of the
Whip adapter using a simple microservices toy app. In particular, it will 
concretely demonstrate the following in order (with each feature's
description in the ICFP paper given in parentheses):

1. Whip can be deployed on an application with no code changes (bottom of p2).
	Additionally, Whip can operate under partial deployment (i.e., only
	one of the services will have a Whip adapter) (bottom of p2).
2. Whip can capture first-order contract failures (bottom of p4).
3. Whip can capture higher-order contract failures (top of p5). In particular,
	Whip uses imprecise blame under partial deployment (end of Section 3.3).
4. Whip uses precise blame under full deployment (Section 3.4)
5. Whip uses precise blame for indexed contracts (end of Section 2)

To show the second criterion, we provide a command to generate the benchmarks
and images from Figure 11.

### Calculator Example

In this section we provide a simple tutorial for the features of Whip with a 
simple microservices application.

<!-- => **Tired of switching between the documentation and your terminal?** 
Try using the online version of this demo at 
[Katacoda](https://katacoda.com/wayetender/scenarios/whip-calculator-quickstart)!
 -->

The microservices application is a simple distributed calculator. It
consists of three services: an _adder_, which performs numeric addition
(which you could imagine being an extremely computationally expensive 
operation that must be distributed), a _discovery_ service for adders,
and a _client_ which issues addition commands. The workflow of the application
is:

1. An adder joins the set of available adders by invoking the 
	`register_adder` operation on the adder service that includes the 
	address where the adder can be invoked.
2. A client requests the address of an available adder by invoking
	the `get_adder_info`. The discovery service returns a random available
	adder to the client.
3. With the given adder service address, the client invokes the
	`add` operation on the adder. The adder performs the computation and 
	returns the result to the client.

The source code for this application is in the `whip-calculator-example`.
The Thrift network protocol is defined in `src/calc.thrift`.

The first step is to build the containers. This can be done with the 
`docker-compose build` command.

```
$ docker-compose build
Building adder
...
```

We can then run the client by using the `docker-compose run client` command.
When run, we will be presented with the calculator client. This command will
also start up the adder and discovery service. For now, let's just use
the `quit` command.

```
$ docker-compose run client
Creating whipcalculatorexample_adder_1
Creating whipcalculatorexample_discovery_1
connected to discovery service discovery:8000
Available Commands:
add [n1] [n2]                   - Get a random adder and compute n1+n2
register_adder [host] [port]    - Register new adder service
quit                            - Exits the program
> quit
```

We can use the `logs` docker-compose command to check the status of the 
adder and discovery service.

```
$ docker-compose logs 
Attaching to whipcalculatorexample_discovery_1, whipcalculatorexample_adder_1
adder_1      | 05/14/2017 12:25:49 PM INFO adder service listening on 8001
adder_1      | 05/14/2017 12:25:49 PM INFO registered with adder discovery on discovery:8000 as adder-8001
discovery_1  | 05/14/2017 12:25:46 PM INFO adder discovery service listening on 7999
discovery_1  | 05/14/2017 12:25:49 PM DEBUG registering adder service adder:8001
```

Note that the adder and discovery services are still running. To view
their status, run the `docker-compose ps` command. To stop them,
run `docker-compose down`.

```
$ docker-compose ps
              Name                       Command         State                        Ports                       
-----------------------------------------------------------------------------------------------------------------
whipcalculatorexample_adder_1       ./run_adder.sh       Up      0.0.0.0:38001->38001/tcp, 0.0.0.0:8001->8001/tcp 
whipcalculatorexample_discovery_1   ./run_discovery.sh   Up      0.0.0.0:38000->38000/tcp, 0.0.0.0:8000->8000/tcp 
$ docker-compose down
Stopping whipcalculatorexample_discovery_1 ... done
Stopping whipcalculatorexample_adder_1 ... done
Removing whipcalculatorexample_client_run_1 ... done
Removing whipcalculatorexample_discovery_1 ... done
Removing whipcalculatorexample_adder_1 ... done
Removing network whipcalculatorexample_default
```

Let's now run the client to perform the third step of the workflow.

```
% docker-compose run client
connected to discovery service discovery:8000
Available Commands:
add [n1] [n2]                   - Get a random adder and compute n1+n2
register_adder [host] [port]    - Register new adder service
quit                            - Exits the program
> add 2 2
2 + 2 = 3
> quit
$
```

_Uh oh._ Two plus two does not equal three. Let's use Whip to pinpoint the error.
(Though, it should be no surprise, the adder has not held up its part of the bargain
to perform the addition correctly.)


> **Objective 1:** Whip can be deployed on an application with no code changes (bottom of p2).
Additionally, Whip can operate under partial deployment (i.e., only
one of the services will have a Whip adapter) (bottom of p2).


We will start by installing an adapter on the client to catch the error.

To do this we will need a Whip contract and a Whip adapter configuration. For the 
tutorial, we have provided both: the contract is located in `whip/calculator.whip`
and the configuration file for the client is located in `adapter_client.yaml`.

Of particular interest in the client proxy string:

```
  - discovery:8000 mapstoservice AdderDiscovery
```

This states that that there is an `AdderDiscovery` 
service at the `discovery` host with port `8000`.

In order to deploy the client with the Whip adater with the above configuration,
we need to create an adapter and use the shim library on the client.
The `shim` command is a shell script that instructs the operating system
to preload the interposition library to intercept on new network connections
(described in more detail in Section 3).

The entry point of the client application is in the `run_client.sh` script.
Inspecting the file, we can see that the adapter is already created in the first
line of the script. The only remaining step is to add the shim library.
We can do that by modifying the last line of the `run_client.sh` script from:

```
python src/client.py discovery 8000
```

to

```
shim python src/client.py discovery 8000
```

This will successfully install the Whip adapter on the client, without any
code changes to the client itself.


> **Objective 2:** Whip can capture first-order contract failures (bottom of p4).

With the adapter installed we can bring down the application, rebuild the 
containers (note: not the service applications themselves), and run the client again:

```
$ docker-compose down
...
$ docker-compose build
...
$ docker-compose run cient
...
$ docker-compose run client ./run_client.sh
connected to discovery service discovery:8000
Available Commands:
add [n1] [n2]                   - Get a random adder and compute n1+n2
register_adder [host] [port]    - Register new adder service
quit                            - Exits the program
> add 2 2
[Whip] Contract Failure: Failed postcondition  result == a + b 
	 Occurring at: service Adder with default index at adder:8001 vouched for by unknown
	 Variables: 
	   - a = 2
	   - b = 2
	   - result = 3
2 + 2 = 3
> 
```

Success! I mean, failure! We have a contract failure, that is. We have successfully
captured a first-order contract failure (i.e., that `2 + 2` is not equal to `3`).

> **Objective 3:** Whip can capture higher-order contract failures (top of p5).
In particular, Whip uses imprecise blame under partial deployment (end of Section 3.3).


For our next objective (achieving higher-order blame), we simply need to inspect
the blame labels in the previous report and the given contract.

The line of interest is:

```
Occurring at: service Adder with default index at adder:8001 vouched for by unknown
```

In this line, we can see that the error came from the adder service. By inspecting
the `adapter_client.yaml` file, we can see that the client is not initially
configured to know about the location of adder service. Instead, Whip only knows
about the adder service through the call to `get_adder_info`. (If you are curious,
you can remove the `@identifies` tag for the `get_adder_info` Whip contract
and the contract would not be checked.)

Additionally, the service was `vouched for by unknown`. That is, the imprecise 
blame label was used. 


> **Objective 4:** Whip uses precise blame under full deployment (Section 3.4)


To show the last objective, we must install an adapter on all services.
It turns out that the other services were already enhanced and we only
need to make the client aware of the discovery service (which
can be confirmed by inspecting the `run_adder.sh` and `run_discovery.sh`
scripts). We can make the client aware of the discovery Whip adapter
with a simple configuration change for the client adapters.

Change the last line of `adapter_client.yaml` file from 

```
  - discovery:8000 mapstoservice AdderDiscovery
```

to:

```
  - discovery:8000 proxiedby discovery:38000 mapstoservice AdderDiscovery
```

With this we can bring down the application, rebuild the containers (note:
not the applications themselves), and run the client again:

```
$ docker-compose down
...
$ docker-compose build
...
$ % docker-compose run client
Creating network "whipcalculatorexample_default" with the default driver
Creating whipcalculatorexample_adder_1
Creating whipcalculatorexample_discovery_1
connected to discovery service discovery:8000
Available Commands:
add [n1] [n2]                   - Get a random adder and compute n1+n2
register_adder [host] [port]    - Register new adder service
quit                            - Exits the program
> add 2 2
[Whip] Contract Failure: Failed postcondition  result == a + b 
	 Occurring at: service Adder with default index at adder:8001 vouched for by adder
	 Variables: 
	   - a = 2
	   - b = 2
	   - result = 3

2 + 2 = 3
> quit
```

We can see now in this case the adder service was vouched for by the adder
adapter (the name "adder" comes from the `whip/adapter_adder.yaml` configuration
file).

> **Objective 5:** Whip uses precise blame for indexed contracts (end of Section 2)


Finally, we show how Whip tracks indexed contracts with a special indexed contract
form given in `whip/calculator.indexed.whip`. This indexed contract provides adder
services only when the first operand (`a`) is exactly equal to 1. In all other cases,
the adder service and discovery service do not vouch for its behavior. In other words,
if the client provides an `a` operand to the adder that is not exactly `1` then
it will vouch for the behavior of the adder service.

Modify each Whip configuration file (`adapter_adder.yaml`, `adapter_client.yaml`,
and `adapter_discovery.yaml`) to have the `spec` field be `whip/calculator.indexed.whip`
instead of `whip/calculator.whip`.

Once the configuration files are modified, we can rebuild the containers and try
running the client with different arguments for `a`:

```
$ docker-compose down
...
$ docker-compose build
...
$ docker-compose run client
connected to discovery service discovery:8000
Available Commands:
add [n1] [n2]                   - Get a random adder and compute n1+n2
register_adder [host] [port]    - Register new adder service
quit                            - Exits the program
> add 1 1
[Whip] Contract Failure: Failed postcondition  result == a + b 
	 Occurring at: service Adder with index 1 at adder:8001 vouched for by adder
	 Variables: 
	   - a = 1
	   - b = 1
	   - result = 1

1 + 1 = 1
> add 2 2
[Whip] Contract Failure: Failed postcondition  result == a + b 
	 Occurring at: service Adder with index 2 at adder:8001 vouched for by client
	 Variables: 
	   - a = 2
	   - b = 2
	   - result = 3

2 + 2 = 3
> quit
```

Note that the `adder` service was blamed in the first run but not in the second,
as the client introduced the new Adder service in the second run (as `a` was not
equal to 1).


---

#### Bonus (fixing the adder and pre-condition errors)


If you are so interested, you can also fix the broken adder by inspecting and
modifing Line 18 of `src/adder.py`. Just change `return a + b - 1` to `return a + b`.
By bringing down the services and bringing them back (as was done above), the 
error will go away.

You can also see client-side errors as follows:

```
$ docker-compose down
...
$ docker-compose build
...
$ docker-compose run client
connected to discovery service discovery:8000
Available Commands:
add [n1] [n2]                   - Get a random adder and compute n1+n2
register_adder [host] [port]    - Register new adder service
quit                            - Exits the program
> add 0 0
0 + 0 = 0
> quit
$ docker-compose logs --tail 7 adder
Attaching to whipcalculatorexample_adder_1
adder_1      | [Whip] Contract Failure: Failed precondition for RPC add ( a > 0 and b > 0 )
adder_1      | 	 Blaming: client (precondition failure)
adder_1      | 	 Occurring at: service Adder with default index at adder:8001 vouched for by adder
adder_1      | 	 Variables: 
adder_1      | 	   - a = 0
adder_1      | 	   - b = 0
adder_1      | 
```

Note that in this case, the precondition error (providing a nonpositive integer) 
was caught in the `adder` service's Whip adapter. This is because,
as described in Section 3.4, when using enhanced communication adapters will share
the burden of contract checking. Note though that still the client was blamed.


### Benchmarks

In this section we describe how to run the benchmarks (don't worry; it's just
one Docker command).


Whip comes with a benchmark test suite that contains three real-world
case studies as described in Section 6. The case studies are:

* **Evernote**: an Evernote Thrift API client.
	You can find more information about the Evernote API at 
	[https://dev.evernote.com/doc/](https://dev.evernote.com/doc/).
* **Chess**: a SOAP-based Xfcc correspondence chess program. 
	You can find more information about the Xfcc protocol at
	[http://xfcc.org/](http://xfcc.org/).
* **Twitter**: a REST-like Twitter API client.
	You can find more information about the Twitter API at
	[https://dev.twitter.com/overview/api](https://dev.twitter.com/overview/api).

The benchmarks are contained in the `whip/benchmarks` directory.
The `benchmarks` directory is structured as follows:

```
.
├── docker-compose.yml
├── README.md
├── evernote
│   └── ...
├── chess
│   └── ...
├── twitter
│   └── ...
└── parse_results
    └── ...
```

The benchmarks are run through [Docker Compose](https://docs.docker.com/compose/).
The `docker-compose.yml` file describes the containers that will be run. In
this suite, there are four containers:

* **evernote**: the Evernote test benchmark
* **chess**: the Chess test benchmark
* **twitter**: the Twitter test benchmark
* **parse_results:** produces human-readable plots from raw benchmark data


#### Running with Docker Compose

To run the benchmarks, simply set the `NUM_OPS` environmental variable to the
number of operations you want the benchmarks to perform and then run the
`docker-compose up --build` command in the `benchmarks` directory. 
The `docker-compose.yml` file is parameterized by the `NUM_OPS` variable, which
sets the number of operations to run per benchmark.
In the "[Anatomy of the Benchmarks](#anatomy-of-the-benchmarks)" section, 
we describe the benchmark's operation in more detail.

Below is an example run in the `benchmarks` directory and its output
with 3,000 operations per benchmark (9,000 operations in total). 


```bash
$ NUM_OPS=3000 docker-compose up --build
Building parse_results
...
Attaching to benchmarks_parse_results_1, benchmarks_twitter_1, benchmarks_evernote_1, benchmarks_chess_1
evernote_1       | Starting tests
evernote_1       | Done
benchmarks_evernote_1 exited with code 0
chess_1          | Starting tests
chess_1          | Done
benchmarks_chess_1 exited with code 0
twitter_1        | Starting tests
twitter_1        | Done
benchmarks_twitter_1 exited with code 0
parse_results_1  | 
parse_results_1  | ---------------------------------
parse_results_1  |       Benchmarks Complete!       
parse_results_1  | ---------------------------------
parse_results_1  | 
parse_results_1  | Please check the results/images directory.
benchmarks_parse_results_1 exited with code 0
```

After running the benchmark, you can check the `results/images` directory inside 
the `benchmarks` directory to find the following generated images:

<div align="center">
<img src="benchmarks_images/memorychart.png" alt="memorychart.png" style="width: 200px;"/>
<img src="benchmarks_images/throughputchart.png" alt="throughputchart.png" style="width: 200px;"/> 
<img src="benchmarks_images/networkchart.png" alt="Drawing" style="width: 200px;"/> 
</div>

* `memorychart.png`: 
 	This chart shows the resident set size of the
	adapter and the dashed lines show the sizes of the store on disk.
	In general, the memory usage of the adapters should level off to be
	constant, while the store size (shown in dashed lines) should increase
	linearly.
		
* `throughputchart.png`: This chart shows the latency of the adapter as
	the number of requests increases. Each point is the average of the 250 
	requests around it. In general, the latency of all three benchmarks
	should not increase as the number of requests increases. The variance,
	however, may be high depending on the Docker host machine setup.
* `networkchart.png`: This chart shows the average amount of adapter traffic 
	per operation call. Vertical bars indicate 95% confidence intervals.
	This chart should remain relatively fixed, with Evernote producing roughly 
	75 bytes of overhead on average per operation, and Twitter and Chess producing 
	roughly 50 bytes of overhead per operation.

With the exception of the `networkchart.png` chart, the generated
results will vary dramatically in absolute numbers depending on the number
of resources given. 

-> **Note:** In the ICFP paper, the number of operations chosen was 10,000 (i.e., `NUM_OPS=10000`).
That trial will take about 45 minutes to an hour to complete, depending on the 
resources available to the Docker containers.

!> **Warning:** Due to bucketing of the raw output data, it is recommended to run the
benchmarks with **at least** 1,00 operations per benchmark (i.e., `NUM_OPS=1000`), 
otherwise there will not be enough aggregate data to plot an image.

#### Anatomy of the Benchmarks

In this section, we describe the structure and operation of the benchmarks.

Each benchmark has a common file structure, comprised of the following files:

* `Dockerfile`: This is the description of how to build the benchmark container.
Each container starts from a base Whip container image, and installs benchmark-specific
libraries and copies the source code needed to run the benchmark into the container.
* `run.sh`: This is the script that runs the benchmark. In general, the 
script will wait for a previous benchmark to complete, then start the server
and adapter, then run the test client.
Finally the raw benchmark telemetry is copied to the `results` volume.
* `server.py`: This file contains the mock server implementation and also
starts the adapter in a subprocess (so that it can track its memory usage). 
* `test.py`: This is the test client which which will initiate the client requests
and track end-to-end latency.
* `adapter.yaml`: This is the Whip adapter configuration file. Inspect it to
see what proxies are being set up and how the contracts are wired together
to their network protocols.
* `{BENCHMARK_NAME}.whip`: This is the Whip contract file.

~> **Caution:** For convenience, TLS verification has been disabled on the test clients as it
can be difficult to install certificates on Docker hosts. For more information, 
see the _[Docker documentation on the topic](https://docs.docker.com/engine/security/certificates/)_.
Once the certificate is installed (and placed in the `server.pem` file for the mock server), 
you can remove the verification bypass options in the `test.py` file. 

Each benchmark produces a variety of telemetry data, scattered between multiple programs.
The raw data files are stored centrally in the `results` directory when the benchmark
completes. Within each results subdirectory (given by the name of the benchmark),
the following benchmark raw data files are created:

* `bytes`: Each line corresponds to the number of bytes of Whip-specific information
in an enhanced message. The adapter computes this information (i.e., in 
`whip/src/adapter/proxy.py`) by computing the byte size difference
between the original unenhanced message and the Whip-enhanced message.
* `clientcalls`: Each line corresponds to the number of milliseconds it took
for a client request to complete from beginning to end. The `test.py` test client
computes this information by measuring the delay of invoking an RPC.
* `memory`: Each line corresponds to a periodic reading of the adapter process's 
resident set size (memory usage) and the size of the store file. The file is
comma separated and the columns are, in order, the memory usage of the adapter, 
the file size of the store file, and the number of requests received at the time
of the reading. The `server.py` file computes this information.
* `times`: Each line corresponds to the number of milliseconds it took for
the mock server to respond to a Whip-proxied request. It is similar to the data
in the `clientcalls` file but is only the portion of time the Whip adapter spent
waiting for the server to respond. The adapter computes this information by
measuring the delay of invoking the RPC on the mock server while it is proxying
a client request.

With this information, the `parse_results` container uses the `parse.py` script
to compute the final aggregated and joined data that makes up the resulting
images (computed by the `gen_charts.sh` script). 


