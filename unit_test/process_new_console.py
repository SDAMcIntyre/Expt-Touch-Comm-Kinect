#!/usr/bin/env python3
import sys
import time
from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE

messages = 'This is Console1', 'This is Console2'

# open new consoles
processes = [Popen([sys.executable, "-c", """import sys
for line in sys.stdin: # poor man's `cat`
    sys.stdout.write(line)
    sys.stdout.flush()
"""],
    stdin=PIPE, bufsize=1, universal_newlines=True,
    # assume the parent script is started from a console itself e.g.,
    # this code is _not_ run as a *.pyw file
    creationflags=CREATE_NEW_CONSOLE)
             for _ in range(len(messages))]

# display messages
for proc, msg in zip(processes, messages):
    proc.stdin.write(msg + "\n")
    proc.stdin.flush()

time.sleep(10) # keep the windows open for a while

# close windows
for proc in processes:
    proc.communicate("bye\n")