#ifndef __PROXY_H__
#define __PROXY_H__

#include "clientprotocol_constants.h"
#include "clientprotocol_types.h"
#include "Redirection.h"

#define DYLD_INTERPOSE(_replacment,_replacee) \
   __attribute__((used)) static struct{ const void* replacment; const void* replacee; } _interpose_##_replacee \
            __attribute__ ((section ("__DATA,__interpose"))) = { (const void*)(unsigned long)&_replacment, (const void*)(unsigned long)&_replacee };


#endif
