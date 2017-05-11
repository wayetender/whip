# Whip [![Docker Build](https://img.shields.io/docker/build/wayetender/whip.svg?maxAge=25920)](https://hub.docker.com/r/wayetender/whip/)

This is the source code for the Whip adapter and Whip shim library.

You can build the code with Docker by running:

	docker build -t wayetender/whip .

The `Dockerfile.dev` is suitable for development purposes as it first
installs the Thrift dependencies in a separate layer. This, however, has
the downside of being a larger image, which is not suitable for distribution.

For more information see the website at 
[http://whip.services/docs](http://whip.services/docs).
