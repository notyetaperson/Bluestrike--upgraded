import time 
import os
import asyncio

from utils.logo import print_logo
from utils.kick import _kick_
from utils.scanner import main
from utils.hijack import hijack_main
from utils.packet_sniffer import start_packet_sniffer
from utils.visualizer import start_visualizer
from utils.terminal_visualizer import start_terminal_visualizer
from utils.persistent_hijacker import start_persistent_hijacker
from utils.applejuice_prank import start_applejuice_prank
from utils.bluetooth_crasher import start_bluetooth_crasher

from rich import print
from rich.prompt import Prompt
from rich.console import Console

console = Console()

modules = """[bright_white] [1] Scan for Bluetooth Devices
 [2] Kick Out Bluetooth Devices
 [3] Hijack Bluetooth Connections
 [4] Packet Sniffer & Analysis
 [5] Advanced Visualizer (GUI)
 [6] Terminal Visualizer
 [7] Persistent Connection Hijacking
 [8] Apple Juice Prank
 [9] Bluetooth Device Crasher
[red] [Q] Exit (Ctrl + c)
"""

def Main_Modules():
    print_logo()
    print(modules)

    try:
        user_choice = Prompt.ask("[cyan] Enter your choice")
    except (EOFError, KeyboardInterrupt):
        console.print("\n[yellow] Input interrupted. Exiting...")
        return

    if user_choice == "1":
        mac_address = asyncio.run(main())
        print("Selected MAC address:", mac_address)
        
        try:
            scan_again = Prompt.ask("[green] Do you want to perform the scan again (y/n)").lower() == "y"
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow] Input interrupted. Continuing...")
            scan_again = False
        if scan_again:
            Main_Modules()

        try:
            kick_ard = Prompt.ask("[red] Do you want to kick the user").lower() == "y"
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow] Input interrupted. Skipping kick option...")
            kick_ard = False
        
        if kick_ard:
            try:
                start_time = Prompt.ask("[red] In how many seconds do you want to start the attack")
            except (EOFError, KeyboardInterrupt):
                console.print("\n[yellow] Input interrupted. Using default time...")
                start_time = "5"
        
        if kick_ard:
            from utils.kick import deauth_Method_1
            _kick_(deauth_Method_1, mac_address, 600, 10, int(start_time))
        else:
            print("Exiting...")
    elif user_choice == "2":
        try:
            mac_address = Prompt.ask("[red] Enter the Mac Address")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow] Input interrupted. Using default MAC...")
            mac_address = "AA:BB:CC:DD:EE:FF"
        
        try:
            start_time = Prompt.ask("[red] In how many seconds do you want to start the attack")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow] Input interrupted. Using default time...")
            start_time = "5"
        from utils.kick import deauth_Method_1
        _kick_(deauth_Method_1, mac_address, 600, 20, int(start_time))
        
    elif user_choice == "3":
        console.print("[red] Starting Bluetooth Connection Hijacker...")
        hijack_main()
        
    elif user_choice == "4":
        console.print("[cyan] Starting Bluetooth Packet Sniffer...")
        start_packet_sniffer()
        
    elif user_choice == "5":
        console.print("[magenta] Starting Advanced Visualizer (GUI)...")
        start_visualizer()
        
    elif user_choice == "6":
        console.print("[cyan] Starting Terminal Visualizer...")
        start_terminal_visualizer()
        
    elif user_choice == "7":
        console.print("[red] Starting Persistent Connection Hijacker...")
        start_persistent_hijacker()
        
    elif user_choice == "8":
        console.print("[red] Starting Apple Juice Prank...")
        start_applejuice_prank()
        
    elif user_choice == "9":
        console.print("[red] Starting Bluetooth Device Crasher...")
        start_bluetooth_crasher()
        
    elif user_choice.lower() == "q":
        try:
            console.clear()
        except:
            os.system("cls" if os.name == 'nt' else "clear")
        exit()
    else:
        print("[red] Invalid Option")
        time.sleep(1)
        Main_Modules()


if __name__ == "__main__":
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
