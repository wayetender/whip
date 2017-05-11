import os
f = open('clientcalls')
f2 = open('times')
BUCKET=250
CASE=os.getenv('CASE')
sums = []
cnt = 0
tmp = 0
try:
    for s in f:
        parts = s.split(',')
        if len(parts) != 2: continue
        v_total = float(parts[1])
        v_off = float(f2.next())
        v = v_total - v_off
        tmp += v
        cnt += 1
        if cnt % BUCKET == 0:
            sums.append(tmp / BUCKET)
            tmp = 0
except StopIteration:
    pass

f.close()
f = open('starts_timing_%s.txt' % CASE, 'w')
f.truncate()
i = 1
for p in sums:
    f.write("%d\t%s\n" % (i * BUCKET, p))
    i += 1

f.close()

f = open('bytes')
def conf_int_native(x, ci=0.95):
    if len(x) == 0: return (0,0,0)
    ci2 = (1-ci)*.5
    low_idx = int(ci2*x.size)
    high_idx = int((1-ci2)*x.size)
    x.sort()
    return x.mean(), x[low_idx], x[high_idx]

xs = f.readlines()
f.close()
xs = [int(x) for x in xs]
import numpy
a=numpy.array(xs)
print "Byte sizes: ", conf_int_native(a)


f = open('memory')
sums = []
cnt = 0.
tmp = 0
buf = 0
buf2 = 0
try:
    for s in f:
        parts = s.split(',')
        if len(parts) != 4: continue
        req = int(parts[3])
        mem = float(parts[1])
        store = float(parts[2])

        buf += mem
        buf2 += store
        cnt += 1.
        if req - tmp > BUCKET:
            sums.append((tmp, buf / cnt, buf2 / cnt))
            tmp = req
            cnt = 0
            buf = 0
            buf2 = 0

except StopIteration:
    pass

f.close()
f = open('starts_mem_%s.txt' % CASE, 'w')
f.truncate()
for (i,p,s) in sums:
    f.write("%d\t%s\t%s\n" % (i, p, s))
    i += 1

f.close()
