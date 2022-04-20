# ------------------------------------------------------------
# pyos1.py  -  The Python Operating System
# 
# Step 1: Tasks
# ------------------------------------------------------------

# This object encapsulates a running task.
from coroutine import coroutine
class Task(object):
    taskid = 0
    def __init__(self,target):
        Task.taskid += 1
        self.tid     = Task.taskid   # Task ID
        self.target  = target        # Target coroutine
        self.sendval = None          # Value to send

    # Run a task until it hits the next yield statement
    def run(self):
        return self.target.send(self.sendval)

# ------------------------------------------------------------
#                       == Example ==
# ------------------------------------------------------------
if __name__ == '__main__':
    
    # A simple generator/coroutine function
    # we don't need @coroutine since sendval=None, this is equal to call next(foo())
    def foo():
        print("Part 1")
        yield  # 遇见yield则停住，等待send再执行这行, 即第二次run(), 第一次run是prime
        print("Part 2")
        yield
        print('Finish')
        # 后面没有yield了，会有一个StopIteration信号
    t1 = Task(foo())
    print("Running foo()")
    t1.run()
    print("Resuming foo()")
    t1.run()

    # If you call t1.run() one more time, you get StopIteration.
    # Uncomment the next statement to see that.

    t1.run()

