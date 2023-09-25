#!/usr/bin/env python3
from disk_relations import *
from transactions import *
import sys
import time
import shutil
import subprocess
from exampletransactions import *

#####################################################################################################
####
#### Some testing code
####
#####################################################################################################
# Initial Setup

testno = 1
if len(sys.argv) > 1:
    testno = sys.argv[1]

rname = "recoverytest{}_relation".format(testno)
shutil.copyfile("recoverytests-original/{}".format(rname), rname)
shutil.copyfile("recoverytests-original/recoverytest{}_logfile".format(testno), 'logfile')


print("Trying test '{}'\n".format(rname))
bpool = BufferPool()
r = Relation(rname)
LogManager.setAndAnalyzeLogFile('logfile')

print("{} diff:".format(rname))
subprocess.call(["diff", "-w", rname, "recoverytests-answers/{}".format(rname)])

print("logfile{} diff:".format(testno))
subprocess.call(["diff", "-w", "logfile", "recoverytests-answers/recoverytest{}_logfile".format(testno)])
