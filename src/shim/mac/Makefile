GEN_SRC := gen-cpp/Redirection.cpp gen-cpp/clientprotocol_constants.cpp gen-cpp/clientprotocol_types.cpp
GEN_OBJ := $(patsubst %.cpp,%.o, $(GEN_SRC))

THRIFT_DIR := /usr/local/include/thrift
BOOST_DIR := /usr/local/include

INC := -I$(THRIFT_DIR) -I$(BOOST_DIR) -Igen-cpp

.PHONY: all clean

all: libshim.dylib dumbserver

%.o: %.cpp
	$(CXX) -std=c++11 -stdlib=libc++ -Wall -DHAVE_INTTYPES_H -DHAVE_NETINET_IN_H $(INC) -c $< -o $@

libshim.dylib: proxy.o $(GEN_OBJ)
	$(CXX) -dynamiclib $^ -o libshim.dylib -L/usr/local/lib -Lgen-cpp -lthrift

dumbserver: DumbServer.o $(GEN_OBJ)
	$(CXX) $^ -o dumbserver -L/usr/local/lib -Lgen-cpp -lthrift

clean:
	$(RM) *.o gen-cpp/*.o libshim.dylib dumbserver
