/**
 * Autogenerated by Thrift Compiler (0.9.1)
 *
 * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
 *  @generated
 */
#ifndef clientprotocol_TYPES_H
#define clientprotocol_TYPES_H

#include <thrift/Thrift.h>
#include <thrift/TApplicationException.h>
#include <thrift/protocol/TProtocol.h>
#include <thrift/transport/TTransport.h>

#include <thrift/cxxfunctional.h>


namespace ClientProxy {

typedef struct _RedirectionInfo__isset {
  _RedirectionInfo__isset() : is_proxied(false), address(false), port(false) {}
  bool is_proxied;
  bool address;
  bool port;
} _RedirectionInfo__isset;

class RedirectionInfo {
 public:

  static const char* ascii_fingerprint; // = "F130B12EADB6306680A7C9A72370EAE1";
  static const uint8_t binary_fingerprint[16]; // = {0xF1,0x30,0xB1,0x2E,0xAD,0xB6,0x30,0x66,0x80,0xA7,0xC9,0xA7,0x23,0x70,0xEA,0xE1};

  RedirectionInfo() : is_proxied(0), address(), port(0) {
  }

  virtual ~RedirectionInfo() throw() {}

  bool is_proxied;
  std::string address;
  int32_t port;

  _RedirectionInfo__isset __isset;

  void __set_is_proxied(const bool val) {
    is_proxied = val;
  }

  void __set_address(const std::string& val) {
    address = val;
  }

  void __set_port(const int32_t val) {
    port = val;
  }

  bool operator == (const RedirectionInfo & rhs) const
  {
    if (!(is_proxied == rhs.is_proxied))
      return false;
    if (!(address == rhs.address))
      return false;
    if (!(port == rhs.port))
      return false;
    return true;
  }
  bool operator != (const RedirectionInfo &rhs) const {
    return !(*this == rhs);
  }

  bool operator < (const RedirectionInfo & ) const;

  uint32_t read(::apache::thrift::protocol::TProtocol* iprot);
  uint32_t write(::apache::thrift::protocol::TProtocol* oprot) const;

};

void swap(RedirectionInfo &a, RedirectionInfo &b);

} // namespace

#endif
