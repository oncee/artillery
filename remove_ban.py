#!/usr/bin/env python3
#
# simple remove banned ip
#
#
import sys
from src.core import *

try:
    ipaddress = sys.argv[1]
    if is_valid_ipv4(ipaddress):
        path = check_banlist_path()
        fileopen = open(path, "r")
        data = fileopen.read()
        data = data.replace(ipaddress + "\n", "")
        filewrite = open(path, "w")
        filewrite.write(data)
        filewrite.close()

        print("Listing all iptables looking for a match... if there is a massive amount of blocked IP's this could take a few minutes..")
        proc = subprocess.run(
            ["iptables", "-L", "ARTILLERY", "-n", "-v", "--line-numbers"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        output = proc.stdout.decode("utf-8", errors="ignore").splitlines()

        for line in output:
            if ipaddress in line:
                parts = line.split()
                if not parts:
                    continue
                rule_num = parts[0]
                if not rule_num.isdigit():
                    continue
                print(rule_num)
                # delete it
                subprocess.run(
                    ["iptables", "-D", "ARTILLERY", rule_num],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    check=False,
                )


    # if not valid then flag
    else:
        print("[!] Not a valid IP Address. Exiting.")
        sys.exit()

except IndexError:
    print("Description: Simple removal of IP address from banned sites.")
    print("[!] Usage: remove_ban.py <ip_address_to_ban>")
