GEN_SRC := gen-cpp/Redirection.cpp gen-cpp/clientprotocol_constants.cpp gen-cpp/clientprotocol_types.cpp
GEN_OBJ := $(patsubst %.cpp,%.a, $(GEN_SRC))

THRIFT_DIR := /usr/local/include/thrift
BOOST_DIR := /usr/local/include

INC := -I$(THRIFT_DIR) -I$(BOOST_DIR) -Igen-cpp

.PHONY: all clean

all: libshim.so

%.a: %.cpp
	$(CXX) -std=c++11 -fPIC -Wall -DHAVE_INTTYPES_H -DHAVE_NETINET_IN_H $(INC) -c $< -o $@

libshim.so: proxy.a $(GEN_OBJ)
	$(CXX) -shared -ldl -fPIC $^ -o libshim.so -L/usr/local/lib -Lgen-cpp -lthrift

clean:
	$(RM) *.a *.so libshim.so
	rm -rf gen-cpp
