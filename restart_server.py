#!/usr/bin/env python3
#
# restart artillery
#
#
import subprocess
import os
from src.core import *

# kill running instance of artillery
kill_artillery()

print("[*] %s: Restarting Artillery Server..." % (grab_time()))
if os.path.isfile("/var/artillery/artillery.py"):
    write_log("[*] %s: Restarting the Artillery Server process..." % (grab_time()))
    subprocess.Popen(["python3", "/var/artillery/artillery.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
