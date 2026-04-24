#!/usr/bin/env python3
#
# basic for now, more to come
#
#
import subprocess
from src.core import *

anti_dos_ports = read_config("ANTI_DOS_PORTS")
anti_dos_throttle = read_config("ANTI_DOS_THROTTLE_CONNECTIONS")
anti_dos_burst = read_config("ANTI_DOS_LIMIT_BURST")

if is_config_enabled("ANTI_DOS"):
    if not anti_dos_throttle.isdigit() or not anti_dos_burst.isdigit():
        raise ValueError("ANTI_DOS_THROTTLE_CONNECTIONS and ANTI_DOS_LIMIT_BURST must be numeric values.")

    throttle = int(anti_dos_throttle)
    burst = int(anti_dos_burst)
    if throttle <= 0 or burst <= 0:
        raise ValueError("ANTI_DOS throttle and burst values must be greater than zero.")

    # basic throttle for some ports
    anti_dos_ports = anti_dos_ports.split(",")
    for ports in anti_dos_ports:
        ports = ports.strip()
        if not ports.isdigit():
            raise ValueError("ANTI_DOS_PORTS entries must be numeric.")
        port_num = int(ports)
        if port_num < 1 or port_num > 65535:
            raise ValueError("ANTI_DOS_PORTS entries must be valid TCP port numbers (1-65535).")

        subprocess.run(
            [
                "iptables", "-A", "ARTILLERY", "-p", "tcp",
                "--dport", str(port_num),
                "-m", "limit",
                "--limit", f"{throttle}/minute",
                "--limit-burst", str(burst),
                "-j", "ACCEPT",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
