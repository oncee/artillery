#!/usr/bin/env python3
#
# quick script for installing artillery
#
#
import subprocess,os,shutil
import sys
import stat
try:
    import grp
except ImportError:
    grp = None
from src.core import *

NON_INTERACTIVE = "--non-interactive" in sys.argv


def env_truthy(name):
    value = os.environ.get(name, "")
    return value.strip().lower() in ("1", "true", "yes", "y", "on")


ASSUME_YES = "--assume-yes" in sys.argv or env_truthy("ARTILLERY_ASSUME_YES")


def prompt_input(message, default_answer="n"):
    if ASSUME_YES:
        return "y"
    if NON_INTERACTIVE:
        return default_answer
    return input(message)


def copy_tree_contents(source_dir, target_dir):
    source_real = os.path.realpath(source_dir)
    target_real = os.path.realpath(target_dir)
    if source_real == target_real:
        raise ValueError("Source and target directories must be different.")
    if source_real.startswith(target_real + os.sep) or target_real.startswith(source_real + os.sep):
        raise ValueError("Source/target directory overlap is not allowed.")

    for entry in os.listdir(source_dir):
        src = os.path.join(source_dir, entry)
        dst = os.path.join(target_dir, entry)
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

print('''
Welcome to the Artillery installer. Artillery is a honeypot, file monitoring, and overall security tool used to protect your nix systems.

Written by: Dave Kennedy (ReL1K)
''')

if os.path.isfile("/etc/init.d/artillery"):
    answer = prompt_input("Artillery detected. Do you want to uninstall [y/n:] ")
    if answer.lower() == "yes" or answer.lower() == "y":
        answer = "uninstall"

if not os.path.isfile("/etc/init.d/artillery"):
    answer = prompt_input("Do you want to install Artillery and have it automatically run when you restart [y/n]: ")

if answer.lower() == "y" or answer.lower() == "yes":
    if is_posix():
        kill_artillery()

        print("[*] Beginning installation. This should only take a moment.")

        # if directories aren't there then create them
        if not os.path.isdir("/var/artillery/logs"):
            os.makedirs("/var/artillery/logs")
        if not os.path.isdir("/var/artillery/database"):
            os.makedirs("/var/artillery/database")
        if not os.path.isdir("/var/artillery/src/program_junk/"):
            os.makedirs("/var/artillery/src/program_junk/")

        # install to rc.local
        print("[*] Adding artillery into startup through init scripts..")
        if os.path.isdir("/etc/init.d"):
            if not os.path.isfile("/etc/init.d/artillery"):
                fileopen = open("src/startup_artillery", "r")
                config = fileopen.read()
                filewrite = open("/etc/init.d/artillery", "w")
                filewrite.write(config)
                filewrite.close()
                print("[*] Triggering update-rc.d on artillery to automatic start...")
                current_mode = os.stat("/etc/init.d/artillery").st_mode
                os.chmod("/etc/init.d/artillery", current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                result = subprocess.run(["update-rc.d", "artillery", "defaults"], check=False)
                if result.returncode != 0:
                    write_log("[!] %s: update-rc.d failed during setup." % (grab_time()))

            # remove old method if installed previously
            if os.path.isfile("/etc/init.d/rc.local"):
                fileopen = open("/etc/init.d/rc.local", "r")
                data = fileopen.read()
                data = data.replace("sudo python3 /var/artillery/artillery.py &", "")
                filewrite = open("/etc/init.d/rc.local", "w")
                filewrite.write(data)
                filewrite.close()

    if is_windows():
        program_files = os.environ["ProgramFiles"]
        os.makedirs(program_files + "\\Artillery\\logs")
        os.makedirs(program_files + "\\Artillery\\database")
        os.makedirs(program_files + "\\Artillery\\src\\program_junk")
        install_path = os.getcwd()
        shutil.copytree(install_path, program_files + "\\Artillery\\")


    if is_posix():
        choice = prompt_input("Do you want to keep Artillery updated? (requires internet) [y/n]: ")
        if choice == "y" or choice == "yes":
            print("[*] Checking out Artillery through github to /var/artillery")
            # if old files are there
            if os.path.isdir("/var/artillery/"):
                shutil.rmtree('/var/artillery')
            result = subprocess.run(["git", "clone", "https://github.com/trustedsec/artillery", "/var/artillery/"], check=False)
            if result.returncode != 0:
                write_log("[!] %s: git clone failed during setup." % (grab_time()))
                print("[!] Git clone failed. Artillery setup files were not updated from GitHub.")
            else:
                print("[*] Finished. If you want to update Artillery go to /var/artillery and type 'git pull'")
        else:
            print("[*] Copying setup files over...")
            try:
                copy_tree_contents(os.getcwd(), "/var/artillery/")
            except ValueError as e:
                write_log("[!] %s: setup copy path error: %s" % (grab_time(), str(e)))
                print("[!] Unable to copy setup files: %s" % str(e))

        # if os is Mac Os X than create a .plist daemon - changes added by contributor - Giulio Bortot
        if os.path.isdir("/Library/LaunchDaemons"):
            # check if file is already in place
            if not os.path.isfile("/Library/LaunchDaemons/com.artillery.plist"):
                print("[*] Creating com.artillery.plist in your Daemons directory")
                filewrite = open("/Library/LaunchDaemons/com.artillery.plist", "w")
                filewrite.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict>\n<key>Disabled</key>\n<false/>\n<key>ProgramArguments</key>\n<array>\n<string>/usr/bin/python3</string>\n<string>/var/artillery/artillery.py</string>\n</array>\n<key>KeepAlive</key>\n<true/>\n<key>RunAtLoad</key>\n<true/>\n<key>Label</key>\n<string>com.artillery</string>\n<key>Debug</key>\n<true/>\n</dict>\n</plist>')
                print("[*] Adding right permissions")
                if grp is not None:
                    wheel_gid = grp.getgrnam("wheel").gr_gid
                    os.chown("/Library/LaunchDaemons/com.artillery.plist", 0, wheel_gid)

    choice = prompt_input("Would you like to start Artillery now? [y/n]: ")
    if choice == "yes" or choice == "y":
        if is_posix():
            result = subprocess.run(["/etc/init.d/artillery", "start"], check=False)
            if result.returncode != 0:
                write_log("[!] %s: artillery init script failed to start." % (grab_time()))

    if is_posix():
        print("[*] Installation complete. Edit /var/artillery/config in order to config artillery to your liking..")

if answer == "uninstall":
    if is_posix():
        if os.path.isfile("/etc/init.d/artillery"):
            os.remove("/etc/init.d/artillery")
        shutil.rmtree("/var/artillery", ignore_errors=True)
        if os.path.isdir("/etc/init.d/artillery"):
            shutil.rmtree("/etc/init.d/artillery", ignore_errors=True)
        kill_artillery()
        print("[*] Artillery has been uninstalled. Manually kill the process if it is still running.")
