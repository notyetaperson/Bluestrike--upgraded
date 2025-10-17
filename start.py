#!/usr/bin/env python3
"""
Bluestrike - Advanced Bluetooth Security Tool
Startup script with warning suppression
"""

import warnings
import os
import sys

# Suppress all warnings before any imports
warnings.filterwarnings("ignore")
os.environ['SCAPY_DISABLE_WARNING'] = '1'
os.environ['PYTHONWARNINGS'] = 'ignore'

# Redirect stderr to suppress scapy warnings
from contextlib import redirect_stderr
from io import StringIO

# Backup original stderr
original_stderr = sys.stderr

try:
    # Redirect stderr during imports
    sys.stderr = StringIO()
    
    # Import main application
    from main import *
    
finally:
    # Restore stderr
    sys.stderr = original_stderr

if __name__ == "__main__":
    # Run the main application
    try:
        # Turns Bluetooth Adapter - ON (Windows compatible)
        import platform
        if platform.system() == "Windows":
            try:
                # Windows Bluetooth enable command
                os.system("powershell -Command \"Get-PnpDevice -Class Bluetooth | Enable-PnpDevice -Confirm:$false\"")
            except:
                print("[yellow] Note: Bluetooth adapter status unchanged")
        else:
            # Linux/Unix systems
            try:
                os.system("rfkill unblock bluetooth")
            except:
                print("[yellow] Note: Bluetooth adapter status unchanged")
        # ----------------------------------
        Main_Modules()
    except KeyboardInterrupt:
        try:
            console.clear()
        except:
            os.system("cls" if os.name == 'nt' else "clear")
        print("[red] User Quit")
        exit()
    except Exception as e:
        try:
            console.clear()
        except:
            os.system("cls" if os.name == 'nt' else "clear")
        print(f"[red] ERROR VALUE [{e} ]")
        exit()
