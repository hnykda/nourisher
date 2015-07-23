import subprocess
from time import sleep

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

parser = ArgumentParser(description="Watchdog.", formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument( "-a", "--argus", type=str, help = "Arguments for main function WITHOUT logfile path!" )
parser.add_argument("-l", "--logfile", type=str, help="Path to logfile")
parser.add_argument("-w", "--watch_time", type=str, help="Watchtime")
parser.add_argument("-m", "--main_path", type=str, default="nourisher/nourisher/main.py", help="Path to main.py")

args = parser.parse_args()

command = "python " + args.main_path + " " + args.argus + " --output_logfile {}".format(args.logfile)


def get_size():
    si = len(open(args.logfile, "r").readlines())
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

        sleep(args.watch_time)

except KeyboardInterrupt:
    killer(pid)
    print("Preruseno uzivatelem")
