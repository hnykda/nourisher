import subprocess
from time import sleep
import sys

command=sys.argv[1]
watch_time = sys.argv[2]
logfile_path = sys.argv[3]

def get_size():
    si = len(open(logfile_path, "r").readlines())    
    #print("Aktualni delka: {}".format(si))
    return si

import shlex
splc = shlex.split(command)

def run_that():
    print("Spoustim prikaz: {}".format(command))
    p = subprocess.Popen(splc)
    print("Spusteno pod pid: {}".format(p.pid))
    return p.pid

pid = run_that()

with open(logfile_path, "w") as of:
    of.write(" ")

def killer(pid):
    import os
    import signal
    os.kill(pid, signal.SIGINT)
    sleep(1)
    os.kill(pid, signal.SIGINT)

prev_size= -1
try:
    while True:
        cur_size = get_size()
        if cur_size ==  prev_size:
            #print("Resetuji")
            killer(pid)
            print("Process se zasekl. Spoustim znova!")
            pid = run_that()
        else:
            #print("Vse ok")
            pass

        prev_size = cur_size

        #print("Spim")

        sleep(int(watch_time))

except KeyboardInterrupt:
    killer(pid)
    print("Preruseno uzivatelem")