import time
import threading
import random
from collections import deque, defaultdict
from datetime import datetime
import math
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich import box
from rich.columns import Columns
from rich.progress import Progress

console = Console()

class TerminalPacketVisualizer:
    def __init__(self):
        self.packet_data = deque(maxlen=100)
        self.device_stats = defaultdict(lambda: {'packets': 0, 'last_seen': None, 'signal': -50})
        self.protocol_stats = defaultdict(int)
        self.signal_history = deque(maxlen=50)
        self.packet_timeline = deque(maxlen=30)
        self.is_running = False
        self.start_time = None
        
    def add_packet(self, packet_info):
        """Add a new packet to the visualization"""
        self.packet_data.append(packet_info)
        
        # Update device stats
        mac = packet_info.get('source_mac', 'Unknown')
        self.device_stats[mac]['packets'] += 1
        self.device_stats[mac]['last_seen'] = packet_info.get('timestamp')
        self.device_stats[mac]['signal'] = packet_info.get('signal_strength', -50)
        
        # Update protocol stats
        protocol = packet_info.get('protocol', 'Unknown')
        self.protocol_stats[protocol] += 1
        
        # Update signal history
        self.signal_history.append(packet_info.get('signal_strength', -50))
        
        # Update timeline
        self.packet_timeline.append({
            'time': datetime.now(),
            'count': len(self.packet_data)
        })
    
    def create_ascii_chart(self, data, width=50, height=10):
        """Create ASCII bar chart"""
        if not data:
            return "No data"
        
        max_val = max(data.values()) if data else 1
        chart_lines = []
        
        for key, value in data.items():
            bar_length = int((value / max_val) * width) if max_val > 0 else 0
            bar = "█" * bar_length + "░" * (width - bar_length)
            chart_lines.append(f"{key[:15]:<15} │{bar}│ {value}")
        
        return "\n".join(chart_lines)
    
    def create_signal_chart(self, data, width=40, height=8):
        """Create ASCII signal strength chart"""
        if len(data) < 2:
            return "Collecting data..."
        
        # Normalize signal strength to 0-1 range
        min_signal = min(data)
        max_signal = max(data)
        range_signal = max_signal - min_signal if max_signal != min_signal else 1
        
        chart_lines = []
        for i in range(height):
            threshold = min_signal + (range_signal * (height - i - 1) / height)
            line = ""
            for signal in data:
                if signal >= threshold:
                    line += "█"
                else:
                    line += "░"
            chart_lines.append(f"│{line}│")
        
        # Add signal strength labels
        chart_lines.append(f"└{'─' * width}┘")
        chart_lines.append(f"Signal: {min_signal:.0f}dBm to {max_signal:.0f}dBm")
        
        return "\n".join(chart_lines)
    
    def create_timeline_chart(self, data, width=60, height=6):
        """Create ASCII timeline chart"""
        if len(data) < 2:
            return "Collecting timeline data..."
        
        # Get recent data points
        recent_data = list(data)[-width:] if len(data) > width else data
        if len(recent_data) < 2:
            return "Collecting timeline data..."
        
        # Normalize values
        values = [d['count'] for d in recent_data]
        max_val = max(values)
        min_val = min(values)
        range_val = max_val - min_val if max_val != min_val else 1
        
        chart_lines = []
        for i in range(height):
            threshold = min_val + (range_val * (height - i - 1) / height)
            line = ""
            for value in values:
                if value >= threshold:
                    line += "█"
                else:
                    line += "░"
            chart_lines.append(f"│{line}│")
        
        chart_lines.append(f"└{'─' * width}┘")
        chart_lines.append(f"Packets: {min_val} to {max_val}")
        
        return "\n".join(chart_lines)
    
    def create_network_topology(self):
        """Create ASCII network topology"""
        if not self.device_stats:
            return "No devices discovered"
        
        topology_lines = []
        topology_lines.append("Network Topology:")
        topology_lines.append("┌" + "─" * 40 + "┐")
        
        for i, (mac, stats) in enumerate(list(self.device_stats.items())[:5]):
            device_name = f"Device_{mac[-5:]}"
            signal_bars = "█" * max(1, int((stats['signal'] + 80) / 10))  # Convert to 0-8 range
            topology_lines.append(f"│ {device_name:<15} {signal_bars:<8} {stats['packets']:>3}p │")
        
        topology_lines.append("└" + "─" * 40 + "┘")
        return "\n".join(topology_lines)
    
    def create_dashboard(self):
        """Create the main dashboard"""
        layout = Layout()
        
        # Header
        elapsed = (datetime.now() - self.start_time).seconds if self.start_time else 0
        status = "🟢 ACTIVE" if self.is_running else "🔴 STOPPED"
        
        header = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔍 Bluetooth Packet Sniffer - Live Analysis                ║
║ Status: {status} │ Packets: {len(self.packet_data)} │ Devices: {len(self.device_stats)} │ Runtime: {elapsed}s ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        # Create sections
        sections = []
        
        # 1. Protocol Distribution
        if self.protocol_stats:
            protocol_chart = self.create_ascii_chart(self.protocol_stats, width=30, height=8)
            protocol_panel = Panel(
                f"📊 Protocol Distribution\n\n{protocol_chart}",
                title="Protocols",
                border_style="cyan",
                box=box.ROUNDED
            )
            sections.append(protocol_panel)
        
        # 2. Signal Strength Chart
        if len(self.signal_history) > 5:
            signal_chart = self.create_signal_chart(list(self.signal_history), width=30, height=6)
            signal_panel = Panel(
                f"📶 Signal Strength\n\n{signal_chart}",
                title="Signal Analysis",
                border_style="green",
                box=box.ROUNDED
            )
            sections.append(signal_panel)
        
        # 3. Packet Timeline
        if len(self.packet_timeline) > 5:
            timeline_chart = self.create_timeline_chart(list(self.packet_timeline), width=30, height=6)
            timeline_panel = Panel(
                f"📈 Packet Timeline\n\n{timeline_chart}",
                title="Timeline",
                border_style="yellow",
                box=box.ROUNDED
            )
            sections.append(timeline_panel)
        
        # 4. Network Topology
        topology = self.create_network_topology()
        topology_panel = Panel(
            f"🕸️ {topology}",
            title="Network Topology",
            border_style="magenta",
            box=box.ROUNDED
        )
        sections.append(topology_panel)
        
        # 5. Device Table
        device_table = Table(title="📱 Discovered Devices", box=box.ROUNDED)
        device_table.add_column("MAC Address", style="cyan")
        device_table.add_column("Packets", style="green")
        device_table.add_column("Signal", style="yellow")
        device_table.add_column("Last Seen", style="blue")
        
        for mac, stats in list(self.device_stats.items())[:8]:
            last_seen = stats['last_seen'].strftime("%H:%M:%S") if stats['last_seen'] else "Unknown"
            signal_str = f"{stats['signal']:.0f}dBm"
            device_table.add_row(
                mac,
                str(stats['packets']),
                signal_str,
                last_seen
            )
        
        device_panel = Panel(device_table, title="Device Discovery", border_style="red", box=box.ROUNDED)
        sections.append(device_panel)
        
        # Combine all sections
        if len(sections) >= 2:
            # Create columns layout
            columns = Columns(sections[:2], equal=True, expand=True)
            dashboard_content = f"{header}\n{columns}"
            
            if len(sections) > 2:
                remaining_sections = sections[2:]
                for section in remaining_sections:
                    dashboard_content += f"\n{section}"
        else:
            dashboard_content = f"{header}\n" + "\n".join(str(section) for section in sections)
        
        return dashboard_content
    
    def simulate_packets(self, duration=60):
        """Simulate realistic Bluetooth packet data"""
        devices = [
            {'mac': 'AA:BB:CC:DD:EE:FF', 'name': 'iPhone 13', 'type': 'Phone'},
            {'mac': '11:22:33:44:55:66', 'name': 'AirPods Pro', 'type': 'Audio'},
            {'mac': 'FF:EE:DD:CC:BB:AA', 'name': 'Samsung Galaxy', 'type': 'Phone'},
            {'mac': '55:44:33:22:11:00', 'name': 'Bluetooth Speaker', 'type': 'Audio'},
            {'mac': '99:88:77:66:55:44', 'name': 'Smart Watch', 'type': 'Wearable'},
        ]
        
        protocols = ['HCI', 'L2CAP', 'RFCOMM', 'SDP', 'AVDTP', 'A2DP', 'HID', 'GATT']
        
        start_time = time.time()
        while self.is_running and (time.time() - start_time) < duration:
            device = random.choice(devices)
            protocol = random.choice(protocols)
            
            packet = {
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
            
            self.add_packet(packet)
            time.sleep(random.uniform(0.1, 1.0))
    
    def start_visualization(self, duration=60):
        """Start the terminal visualization"""
        self.is_running = True
        self.start_time = datetime.now()
        
        console.print("[bold blue]🔍 Starting Terminal Packet Visualizer...")
        console.print("[yellow]Press Ctrl+C to stop")
        
        # Start packet simulation in background
        sim_thread = threading.Thread(target=self.simulate_packets, args=(duration,))
        sim_thread.daemon = True
        sim_thread.start()
        
        try:
            # Live dashboard
            with Live(self.create_dashboard(), refresh_per_second=2, screen=True) as live:
                while self.is_running:
                    live.update(self.create_dashboard())
                    time.sleep(0.5)
        except KeyboardInterrupt:
            self.is_running = False
            console.print("\n[yellow]Visualization stopped by user")
        finally:
            self.is_running = False
            console.print("\n[bold green]📊 Visualization Complete!")
            console.print(f"[cyan]Total packets: {len(self.packet_data)}")
            console.print(f"[cyan]Unique devices: {len(self.device_stats)}")
            console.print(f"[cyan]Protocols detected: {len(self.protocol_stats)}")

def start_terminal_visualizer():
    """Start the terminal-based packet visualizer"""
    visualizer = TerminalPacketVisualizer()
    
    console.print("[bold blue]🔍 Bluetooth Terminal Packet Visualizer")
    console.print("[yellow]Real-time ASCII visualization of Bluetooth packets")
    
    try:
        duration = int(console.input("[cyan]Enter visualization duration (seconds): ") or "60")
    except (ValueError, EOFError, KeyboardInterrupt):
        duration = 60
        console.print("[yellow]Using default duration: 60 seconds")
    
    visualizer.start_visualization(duration)

if __name__ == "__main__":
    start_terminal_visualizer()
