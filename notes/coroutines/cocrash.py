# cocrash.py
#
# An example of hooking coroutines up in a way that might cause a potential
# crash.   Basically, there are two threads feeding data into the
# printer() coroutine.    

from cobroadcast import *
from cothread import threaded

p = printer()
target = broadcast([threaded(grep('foo',p)),
                    threaded(grep('bar',p))])

# no-threaded version won't crash since each send will block util pipeline finish? nope, 
# (send() doesn't return until the target yields) -- page 91, but it will block continue run function util right before **yield**, this is exactly where blocking happens!!!
# target = broadcast([grep('foo', p),
#                     grep('bar', p)])

import time
# Adjust the count if this doesn't cause a crash
for i in range(10):
    target.send("foo is nice\n")
    print('Return send foo')
    target.send("bar is bad\n")
    print('Return send bar')
del target
del p

