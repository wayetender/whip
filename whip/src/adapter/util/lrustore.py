from lru import LRU
import shelve

class LruStore(object):
    def __init__(self, size = 400, filename='/tmp/lru3.dat'):
        self.cache = LRU(size)
        self.max = size
        self.filename = filename

    def _tryload(self, k):
        d = shelve.open(self.filename, writeback=True)
        v = d.get(k)
        if v:
            self._checkevict()
            self.cache[k] = v
            del d[k]
        d.close()

    def _checkevict(self):
        if self.cache.get_size() == len(self.cache):
            d = shelve.open(self.filename, writeback=True)
            (to_evict, v) = self.cache.items()[-1]
            d[to_evict] = v
            d.close()

    def __delitem__(self, k):
        if k not in self.cache:
            self._tryload(k)
            del self.cache[k]

    def __getitem__(self, k):
        if k not in self.cache.keys():
            self._tryload(k)
        return self.cache[k]

    def __contains__(self, k):
        if k not in self.cache.keys():
            self._tryload(k)
        return k in self.cache.keys()

    def __setitem__(self, k, v):
        if k not in self.cache.keys():
            self._tryload(k)
        self._checkevict()
        self.cache[k] = v

    def get(self, k, default=None):
        if k not in self.cache.keys():
            self._tryload(k)
        return self.cache.get(k, default)


if __name__ == '__main__':
    blah = LruStore(3)

    d = shelve.open('lru.dat')
    print "initial file items:"
    print d.items()
    d.close()
    blah['a'] = 1
    blah['b'] = 2
    blah['c'] = 3
    blah['d'] = 4

    print "cache after insert of a,b,c,d="
    print blah.cache.items()

    print "file after insert of a,b,c,d="
    d = shelve.open('lru.dat')
    print d.items()
    d.close()

    assert 'a' in blah

    print "cache after checking contains a"
    print blah.cache.items()

    print "file after checking contains a"
    d = shelve.open('lru.dat')
    print d.items()
    d.close()
