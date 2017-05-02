

# [nprev] <- [n] -> [nnext]
# [secondprev] <- [second] -> [secondnext]


# [nprev] <- -> [nnext]
# [secondprev] <- -> [second] <- -> [n] <- -> [secondnext]

class LruStore(object):
    class Node(object):
        def __init__(self, v):
            self.v = v
            self.next = None
            self.prev = None
        def __str__(self):
            print "%s <- %s -> %s" % (self.prev.v, self.v, self.next.v)

    def __init__(self, size = 100):
        self.max = size
        self.count = 0
        self.backing = {}
        self.usedfirst = None

    def _setfirst(self, n):
        if self.usedfirst:
            nprev = n.prev
            nnext = n.next
            second = self.usedfirst
            nprev.next = nnext
            nnext.prev = nprev
            n.next = second.next
            n.next.prev = n
            second.next = n
            n.prev = second
        else:
            n.next = n
            n.prev = n
        self.usedfirst = n
        print self.usedfirst

    def _evictoldest(self):
        oldest = self.usedfirst.next
        oldestnext = oldest.next
        oldestprev = oldest.prev
        oldestnext.prev = oldestprev
        oldestprev.next = oldestnext
        del self.backing[oldest]

    def __delitem__(self, k):
        n = self.backing[k]
        nnext = n.next
        nprev = n.prev
        nnext.prev = nprev
        nprev.next = nnext
        self.count -= 1

    def __getitem__(self, k):
        if k not in self.backing:
            print 'lru store needs to check backing store'
        n = self.backing[k]
        self._setfirst(n)
        return n.v

    def __setitem__(self, k, v):
        if k in self.backing:
            n = self.backing[k]
            self._setfirst(n)
            n.v = v
        else:
            if self.count >= self.max:
                self.evictoldest()
            n = LruStore.Node(v)
            self._setfirst(n)
            self.count += 1

    def get(self, k, default=None):
        return self.backing.get(k, default)


if __name__ == '__main__':
    blah = LruStore(3)
    blah['a'] = 1
    blah['b'] = 2
    blah['c'] = 3
    blah['d'] = 4

    print 'a' in blah


