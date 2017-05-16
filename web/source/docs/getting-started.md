---
layout: "docs"
page_title: "Getting Started"
sidebar_current: "getting-started"
description: A getting started guide
---

# Getting Started

We will highlight the features of Whip with a simple tutorial for the features of Whip with a simple microservices application.

=> **Tired of switching between tutorial documentation and your terminal?** 
Try using the online version of this demo at 
[Katacoda](https://katacoda.com/wayetender/scenarios/whip-calculator-quickstart)!

In particular, it will highlight:

1. Whip can be deployed on an application with no code changes. Additionally, Whip can operate under partial deployment (i.e., only one of the services will have a Whip adapter).
2. Whip can detect first-order contract failures.
3. Whip can detect higher-order contract failures. Whip blames correctly. Under partial deployment though, Whip uses the same blame label for all non Whip-enhanced services.
4. Whip leverages other adapters in enhanced communication to transmit blame labels for services.
5. Whip can detect indexed contract violations.


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

### Calculator App


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


## Installing a Whip Adapter

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
to preload the interposition library to intercept on new network connections.

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


Note the line coming from the error:

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


### Enhanced Communication

We now install an adapter on all services.
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


### Indexed Contracts

We show how Whip tracks indexed contracts with a special indexed contract
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
was caught in the `adder` service's Whip adapter. This is because  when using enhanced communication adapters will share
the burden of contract checking. Note though that still the client was blamed.

