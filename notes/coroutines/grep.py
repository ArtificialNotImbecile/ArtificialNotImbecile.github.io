# grep.py
#
# A very simple coroutine
def grep(pattern):
    print("Looking for %s" % pattern)
    while True:
        line = (yield)
        if pattern in line:
            print(line, end=' ')

# Example use
if __name__ == '__main__':
    g = grep("python")
    print('finish def')
    next(g)
    print('finish next')
    g.send("Yeah, but no, but yeah, but no")
    g.send("A series of tubes")
    g.send("python generators rock!")
