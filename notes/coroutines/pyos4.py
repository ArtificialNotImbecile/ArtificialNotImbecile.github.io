# ------------------------------------------------------------
# pyos4.py  -  The Python Operating System
#
# Step 4: Introduce the idea of a "System Call"
# ------------------------------------------------------------

# ------------------------------------------------------------
#                       === Tasks ===
# ------------------------------------------------------------
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
#                      === Scheduler ===
# ------------------------------------------------------------
from queue import Queue

class Scheduler(object):
    def __init__(self):
        self.ready   = Queue()   
        self.taskmap = {}        

    def new(self,target):
        newtask = Task(target)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)
        return newtask.tid

    def exit(self,task):
        print("Task %d terminated" % task.tid)
        del self.taskmap[task.tid]

    def schedule(self,task):
        self.ready.put(task)

    def mainloop(self):
         while self.taskmap:
            task = self.ready.get()
            try:
                result = task.run()
                if isinstance(result,SystemCall):
                    result.task  = task
                    result.sched = self
                    result.handle()
                    continue
            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)

# ------------------------------------------------------------
#                   === System Calls ===
# ------------------------------------------------------------

class SystemCall(object):
    def handle(self):
        pass

# Return a task's ID number
class GetTid(SystemCall):
    def handle(self):
        self.task.sendval = self.task.tid
        self.sched.schedule(self.task)

# ------------------------------------------------------------
#                      === Example ===
# ------------------------------------------------------------
if __name__ == '__main__':

    def foo():
        mytid = yield GetTid()
        for i in range(5):
            print("I'm foo", mytid)
            yield

    def bar():
        # 我懂了，这种表达式: yield的值会先返回给send，且mytid准备好接受下一次的赋值了！也就是这一个yield的GetTid部分是前一个send call的，赋值部分是后一个send call的，这样StopIteration就会在没有后半部分yield的时候Raise！
        mytid = yield GetTid()
        for i in range(10):
            print("I'm bar", mytid)
            yield

    sched = Scheduler()
    sched.new(foo())
    sched.new(bar())
    sched.mainloop()
