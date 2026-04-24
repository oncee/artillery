Artillery is a combination of a honeypot, monitoring tool, and alerting system. Eventually this will evolve into a hardening monitoring platform as well to detect insecure configurations from nix systems. It's relatively simple, run ```./setup.py``` and hit yes, this will install Artillery in ```/var/artillery``` and edit your ```/etc/init.d/rc.local``` to start artillery on boot up.

For non-interactive CI/testing runs, use ```python3 setup.py --non-interactive``` to skip blocking prompts.
Use ```python3 setup.py --non-interactive --assume-yes``` to run unattended installation prompts with yes defaults.
For non-TTY bootstrap from `artillery.py`, set `ARTILLERY_ASSUME_YES=true` only when you explicitly want unattended yes-default behavior.

### Python 3 update and compatibility fixes

Artillery now targets **Python 3**.

- Run setup with: ```python3 setup.py```
- Interactive mode remains available for manual installs.
- Non-interactive mode is available for CI/automation:
  - ```python3 setup.py --non-interactive```
  - ```python3 setup.py --non-interactive --assume-yes```

Recent Python 3 migration fixes include:

- Updated legacy Python 2 syntax and modules (`print`, exception syntax, `_thread`, `socketserver`, `urllib.request`, `email.mime`, `open()`).
- Improved bytes/string handling for hashing, diff output parsing, and networking/logging code paths.
- Improved installer behavior in non-TTY environments and synchronization logic for existing iptables bans.

### Contributions in this update

The following contributions were added in this update:

- Migrated the project runtime and scripts from Python 2 style code to Python 3 compatible syntax and modules.
- Added installer automation support for CI/non-interactive environments using:
  - `--non-interactive`
  - `--assume-yes`
- Updated startup/setup behavior so non-TTY bootstrap flows can proceed without blocking prompts.
- Added environment-variable parity for unattended installs so `ARTILLERY_ASSUME_YES` is honored the same as `--assume-yes` in `setup.py`.
- Improved compatibility and reliability in monitor/sync flows by fixing bytes/str handling and iptables IP parsing logic.
- Hardened command execution paths by replacing interpolated shell calls in critical flows with validated arguments and `subprocess.run(..., shell=False)`.

### Patch follow-up updates

- Installer auto-confirm now supports both mechanisms:
  - CLI flag: `--assume-yes`
  - Environment variable: `ARTILLERY_ASSUME_YES=true`
- This keeps non-interactive behavior consistent across direct installer usage and automation/bootstrap contexts.

### Validation checklist (recommended)

Run the validation script from the repository root:

```bash
./scripts/validate_python3.sh
```

This performs:

- Python 3 compile checks across top-level and `src/` modules
- Focused integration tests:
  - installer non-interactive flow (`tests/test_setup_non_interactive.py`)
  - iptables parsing behavior (`tests/test_iptables_parsing.py`)
- Non-interactive setup smoke check (`python3 setup.py --non-interactive`)
- Scan for common Python 2 legacy patterns
- Diff hygiene check (`git diff --check`)

### Features

1. It sets up multiple common ports that are attacked. If someone connects to these ports, it blacklists them forever (to remove blacklisted ip's, remove them from ```/var/artillery/banlist.txt```)

2. It monitors what folders you specify, by default it checks ```/var/www``` and ```/etc``` for modifications.

3. It monitors the SSH logs and looks for brute force attempts.

4. It will email you when attacks occur and let you know what the attack was.

Be sure to edit the ```/var/artillery/config``` to turn on mail delivery, brute force attempt customizations, and what folders to monitor.

### Bugs and enhancements

For bug reports or enhancements, please open an issue here https://github.com/trustedsec/artillery/issues

### Project structure

For those technical folks you can find all of the code in the following structure:

- ```src/core.py``` - main central code reuse for things shared between each module
- ```src/monitor.py``` - main monitoring module for changes to the filesystem
- ```src/ssh_monitor.py``` - main monitoring module for SSH brute forcing
- ```src/honeypot.py``` - main module for honeypot detection
- ```src/harden.py``` - check for basic hardening to the OS
- ```database/integrity.data``` - main database for maintaining sha512 hashes of filesystem
- ```setup.py``` - copies files to ```/var/artillery/``` then edits ```/etc/init.d/artillery``` to ensure artillery starts per each reboot

### Supported platforms

- Linux
- Windows


Project Artillery - A project by Binary Defense Systems (https://www.binarydefense.com).

Binary Defense Systems (BDS) is a sister company of TrustedSec, LLC
