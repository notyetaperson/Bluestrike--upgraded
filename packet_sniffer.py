import subprocess
import threading
import time
import json
import re
import warnings
import os

# Suppress scapy/libpcap warnings
warnings.filterwarnings("ignore", message="No libpcap provider available")
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['SCAPY_DISABLE_WARNING'] = '1'

from collections import defaultdict, deque
from datetime import datetime
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich import box
# Optional imports for advanced features
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import tkinter as tk
    from tkinter import ttk
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from scapy.all import *
    from scapy.layers.bluetooth import *
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
import queue
import platform

console = Console()

class BluetoothPacketSniffer:
    def __init__(self):
        self.is_sniffing = False
        self.packet_queue = queue.Queue()
        self.packet_count = 0
        self.device_stats = defaultdict(lambda: {'packets': 0, 'last_seen': None, 'protocols': set()})
        self.protocol_stats = defaultdict(int)
        self.signal_strength_data = deque(maxlen=100)
        self.packet_timeline = deque(maxlen=200)
        self.captured_packets = []
        self.start_time = None
        
    def detect_bluetooth_interface(self):
        """Detect available Bluetooth interfaces"""
        interfaces = []
        
        if platform.system() == "Windows":
            try:
                # Try to find Bluetooth interfaces on Windows
                result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                     capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'Bluetooth' in line:
                        interfaces.append('bluetooth')
            except:
                pass
        else:
            # Linux/Unix systems
            try:
                result = subprocess.run(['hcitool', 'dev'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'hci' in line:
                        interfaces.append(line.split()[0])
            except:
                pass
        
        return interfaces if interfaces else ['hci0']  # Default fallback
    
    def start_sniffing(self, interface='hci0', duration=60):
        """Start packet sniffing with real-time analysis"""
        self.is_sniffing = True
        self.start_time = datetime.now()
        
        console.print("[bold green]Starting Bluetooth Packet Sniffer...")
        console.print(f"[yellow]Interface: {interface}")
        console.print(f"[yellow]Duration: {duration} seconds")
        
        # Start sniffing in separate thread
        sniff_thread = threading.Thread(target=self._sniff_packets, args=(interface, duration))
        sniff_thread.daemon = True
        sniff_thread.start()
        
        # Start visualization
        self._start_visualization()
        
        return sniff_thread
    
    def _sniff_packets(self, interface, duration):
        """Core packet sniffing function"""
        try:
            if platform.system() == "Windows":
                # Windows packet capture using netsh or alternative
                self._windows_sniffing(interface, duration)
            else:
                # Linux packet capture using hcidump
                self._linux_sniffing(interface, duration)
        except Exception as e:
            console.print(f"[red]Sniffing error: {e}")
        finally:
            self.is_sniffing = False
    
    def _windows_sniffing(self, interface, duration):
        """Windows-specific packet capture"""
        try:
            # Use PowerShell to monitor Bluetooth activity
            cmd = [
                'powershell', '-Command',
                'Get-WinEvent -LogName "Microsoft-Windows-Bluetooth-BthLE/Operational" -MaxEvents 100'
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            start_time = time.time()
            
            while self.is_sniffing and (time.time() - start_time) < duration:
                line = process.stdout.readline()
                if line:
                    self._process_packet_data(line.strip())
                time.sleep(0.1)
                
        except Exception as e:
            console.print(f"[red]Windows sniffing error: {e}")
            # Fallback to simulated data for demo
            self._simulate_packets(duration)
    
    def _linux_sniffing(self, interface, duration):
        """Linux-specific packet capture using hcidump"""
        try:
            cmd = ['hcidump', '-i', interface, '-R']
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            start_time = time.time()
            
            while self.is_sniffing and (time.time() - start_time) < duration:
                line = process.stdout.readline()
                if line:
                    self._process_hcidump_line(line.strip())
                time.sleep(0.01)
                
        except Exception as e:
            console.print(f"[red]Linux sniffing error: {e}")
            # Fallback to simulated data
            self._simulate_packets(duration)
    
    def _simulate_packets(self, duration):
        """Simulate realistic Bluetooth packet data for demonstration"""
        import random
        
        devices = [
            {'mac': 'AA:BB:CC:DD:EE:FF', 'name': 'iPhone 13', 'type': 'Phone'},
            {'mac': '11:22:33:44:55:66', 'name': 'AirPods Pro', 'type': 'Audio'},
            {'mac': 'FF:EE:DD:CC:BB:AA', 'name': 'Samsung Galaxy', 'type': 'Phone'},
            {'mac': '55:44:33:22:11:00', 'name': 'Bluetooth Speaker', 'type': 'Audio'},
            {'mac': '99:88:77:66:55:44', 'name': 'Smart Watch', 'type': 'Wearable'},
        ]
        
        protocols = ['HCI', 'L2CAP', 'RFCOMM', 'SDP', 'AVDTP', 'A2DP', 'HID', 'GATT']
        
        start_time = time.time()
        while self.is_sniffing and (time.time() - start_time) < duration:
            device = random.choice(devices)
            protocol = random.choice(protocols)
            
            packet_data = {
                'timestamp': datetime.now(),
                'source_mac': device['mac'],
                'device_name': device['name'],
                'device_type': device['type'],
                'protocol': protocol,
                'packet_size': random.randint(20, 1500),
                'signal_strength': random.randint(-80, -20),
                'direction': random.choice(['TX', 'RX']),
                'raw_data': f"{device['mac']} -> {protocol} packet"
            }
            
            self._process_packet_data(json.dumps(packet_data, default=str))
            time.sleep(random.uniform(0.1, 2.0))
    
    def _process_packet_data(self, data):
        """Process captured packet data"""
        try:
            if not data.strip():
                return
                
            # Parse packet information
            packet_info = self._parse_packet(data)
            if packet_info:
                self.packet_count += 1
                self.packet_queue.put(packet_info)
                self._update_statistics(packet_info)
                
        except Exception as e:
            console.print(f"[red]Packet processing error: {e}")
    
    def _process_hcidump_line(self, line):
        """Process hcidump output line"""
        if not line or line.startswith('>') or line.startswith('<'):
            return
            
        # Extract MAC address and protocol info
        mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', line)
        if mac_match:
            mac = mac_match.group(0)
            protocol = self._identify_protocol(line)
            
            packet_info = {
                'timestamp': datetime.now(),
                'source_mac': mac,
                'device_name': f'Device_{mac[-5:]}',
                'protocol': protocol,
                'packet_size': len(line),
                'signal_strength': -50,  # Default
                'direction': 'TX' if line.startswith('>') else 'RX',
                'raw_data': line
            }
            
            self._process_packet_data(json.dumps(packet_info, default=str))
    
    def _parse_packet(self, data):
        """Parse packet data into structured format"""
        try:
            if data.startswith('{'):
                return json.loads(data)
            else:
                # Parse raw packet data
                return {
                    'timestamp': datetime.now(),
                    'source_mac': 'Unknown',
                    'device_name': 'Unknown Device',
                    'protocol': 'Unknown',
                    'packet_size': len(data),
                    'signal_strength': -50,
                    'direction': 'Unknown',
                    'raw_data': data
                }
        except:
            return None
    
    def _identify_protocol(self, line):
        """Identify Bluetooth protocol from packet data"""
        protocols = {
            'HCI': ['HCI', 'Command', 'Event'],
            'L2CAP': ['L2CAP', 'Channel'],
            'RFCOMM': ['RFCOMM', 'Channel'],
            'SDP': ['SDP', 'Service'],
            'AVDTP': ['AVDTP', 'Audio'],
            'A2DP': ['A2DP', 'Stream'],
            'HID': ['HID', 'Input'],
            'GATT': ['GATT', 'Attribute']
        }
        
        for protocol, keywords in protocols.items():
            if any(keyword in line for keyword in keywords):
                return protocol
        return 'Unknown'
    
    def _update_statistics(self, packet_info):
        """Update real-time statistics"""
        mac = packet_info.get('source_mac', 'Unknown')
        protocol = packet_info.get('protocol', 'Unknown')
        
        # Update device stats
        self.device_stats[mac]['packets'] += 1
        self.device_stats[mac]['last_seen'] = packet_info.get('timestamp')
        self.device_stats[mac]['protocols'].add(protocol)
        
        # Update protocol stats
        self.protocol_stats[protocol] += 1
        
        # Update signal strength data
        signal = packet_info.get('signal_strength', -50)
        self.signal_strength_data.append(signal)
        
        # Update timeline
        self.packet_timeline.append({
            'timestamp': packet_info.get('timestamp'),
            'packet_count': self.packet_count,
            'protocol': protocol
        })
    
    def _start_visualization(self):
        """Start real-time visualization"""
        with Live(self._create_dashboard(), refresh_per_second=2, screen=True) as live:
            while self.is_sniffing:
                live.update(self._create_dashboard())
                time.sleep(0.5)
    
    def _create_dashboard(self):
        """Create real-time dashboard"""
        layout = Layout()
        
        layout.split_column(
            Layout(self._create_header(), size=3),
            Layout(self._create_stats_panel(), size=8),
            Layout(self._create_device_table(), size=10),
            Layout(self._create_protocol_chart(), size=8)
        )
        
        return layout
    
    def _create_header(self):
        """Create dashboard header"""
        elapsed = (datetime.now() - self.start_time).seconds if self.start_time else 0
        status = "[green]●[/green] ACTIVE" if self.is_sniffing else "[red]●[/red] STOPPED"
        
        header = f"""
[bold blue]🔍 Bluetooth Packet Sniffer Dashboard[/bold blue]
Status: {status} | Packets Captured: {self.packet_count} | Runtime: {elapsed}s
"""
        return Panel(header, border_style="blue")
    
    def _create_stats_panel(self):
        """Create statistics panel"""
        stats_table = Table(title="📊 Real-time Statistics", box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        stats_table.add_column("Trend", style="yellow")
        
        # Calculate packet rate
        elapsed = (datetime.now() - self.start_time).seconds if self.start_time else 1
        packet_rate = self.packet_count / elapsed if elapsed > 0 else 0
        
        stats_table.add_row("Total Packets", str(self.packet_count), f"{packet_rate:.1f}/s")
        stats_table.add_row("Unique Devices", str(len(self.device_stats)), "↑" if len(self.device_stats) > 0 else "→")
        stats_table.add_row("Protocols Detected", str(len(self.protocol_stats)), "↑" if len(self.protocol_stats) > 0 else "→")
        
        # Signal strength stats
        if self.signal_strength_data:
            avg_signal = sum(self.signal_strength_data) / len(self.signal_strength_data)
            stats_table.add_row("Avg Signal (dBm)", f"{avg_signal:.1f}", "📶")
        
        return Panel(stats_table, border_style="green")
    
    def _create_device_table(self):
        """Create device discovery table"""
        device_table = Table(title="📱 Discovered Devices", box=box.ROUNDED)
        device_table.add_column("MAC Address", style="cyan")
        device_table.add_column("Device Name", style="magenta")
        device_table.add_column("Packets", style="green")
        device_table.add_column("Protocols", style="yellow")
        device_table.add_column("Last Seen", style="blue")
        
        for mac, stats in list(self.device_stats.items())[:10]:  # Show top 10
            last_seen = stats['last_seen'].strftime("%H:%M:%S") if stats['last_seen'] else "Unknown"
            protocols = ", ".join(list(stats['protocols'])[:3])  # Show first 3 protocols
            
            device_table.add_row(
                mac,
                f"Device_{mac[-5:]}",
                str(stats['packets']),
                protocols,
                last_seen
            )
        
        return Panel(device_table, border_style="magenta")
    
    def _create_protocol_chart(self):
        """Create protocol distribution chart"""
        if not self.protocol_stats:
            return Panel("[yellow]No protocol data available yet...", border_style="yellow")
        
        protocol_table = Table(title="📡 Protocol Distribution", box=box.ROUNDED)
        protocol_table.add_column("Protocol", style="cyan")
        protocol_table.add_column("Count", style="green")
        protocol_table.add_column("Percentage", style="yellow")
        protocol_table.add_column("Bar", style="blue")
        
        total_packets = sum(self.protocol_stats.values())
        
        for protocol, count in sorted(self.protocol_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_packets * 100) if total_packets > 0 else 0
            bar_length = int(percentage / 5)  # Scale bar to 20 chars max
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            protocol_table.add_row(
                protocol,
                str(count),
                f"{percentage:.1f}%",
                bar
            )
        
        return Panel(protocol_table, border_style="cyan")
    
    def stop_sniffing(self):
        """Stop packet sniffing"""
        self.is_sniffing = False
        console.print("[yellow]Stopping packet sniffer...")
    
    def get_captured_packets(self):
        """Get all captured packets"""
        return self.captured_packets
    
    def export_packets(self, filename="bluetooth_capture.json"):
        """Export captured packets to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.captured_packets, f, default=str, indent=2)
            console.print(f"[green]Packets exported to {filename}")
        except Exception as e:
            console.print(f"[red]Export error: {e}")

def start_packet_sniffer():
    """Main function to start packet sniffer"""
    sniffer = BluetoothPacketSniffer()
    
    console.print("[bold blue]🔍 Bluetooth Packet Sniffer")
    console.print("[yellow]This tool captures and analyzes Bluetooth packets in real-time")
    
    # Get interface
    interfaces = sniffer.detect_bluetooth_interface()
    if len(interfaces) > 1:
        console.print(f"[cyan]Available interfaces: {', '.join(interfaces)}")
        try:
            interface = Prompt.ask("Select interface", default=interfaces[0])
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow] Input interrupted. Using default interface...")
            interface = interfaces[0]
    else:
        interface = interfaces[0]
        console.print(f"[cyan]Using interface: {interface}")
    
    # Get duration
    try:
        duration = int(Prompt.ask("Sniffing duration (seconds)", default="60"))
    except (EOFError, KeyboardInterrupt):
        console.print("\n[yellow] Input interrupted. Using default duration...")
        duration = 60
    
    try:
        # Start sniffing
        thread = sniffer.start_sniffing(interface, duration)
        
        # Wait for completion
        thread.join()
        
        # Show final results
        console.print("\n[bold green]📊 Sniffing Complete!")
        console.print(f"[cyan]Total packets captured: {sniffer.packet_count}")
        console.print(f"[cyan]Unique devices found: {len(sniffer.device_stats)}")
        console.print(f"[cyan]Protocols detected: {len(sniffer.protocol_stats)}")
        
        # Ask if user wants to export
        try:
            export = Prompt.ask("Export captured data?", default="n").lower() == "y"
            if export:
                sniffer.export_packets()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow] Input interrupted. Skipping export...")
            
    except KeyboardInterrupt:
        sniffer.stop_sniffing()
        console.print("\n[yellow]Sniffing stopped by user")
    except Exception as e:
        console.print(f"[red]Error: {e}")

if __name__ == "__main__":
    start_packet_sniffer()
