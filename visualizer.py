# Optional imports for advanced features
import warnings
import os

# Suppress scapy/libpcap warnings
warnings.filterwarnings("ignore", message="No libpcap provider available")
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['SCAPY_DISABLE_WARNING'] = '1'

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import tkinter as tk
    from tkinter import ttk
    import numpy as np
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib/tkinter not available. Advanced visualizer disabled.")

from collections import deque
import threading
import time
from datetime import datetime, timedelta

# Set style for beautiful plots
if MATPLOTLIB_AVAILABLE:
    plt.style.use('dark_background')
    sns.set_palette("husl")

class BluetoothVisualizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bluetooth Packet Sniffer - Real-time Visualization")
        self.root.configure(bg='#1e1e1e')
        self.root.geometry("1400x900")
        
        # Data storage
        self.packet_data = deque(maxlen=1000)
        self.device_data = {}
        self.protocol_data = deque(maxlen=100)
        self.signal_data = deque(maxlen=200)
        self.timeline_data = deque(maxlen=500)
        
        # Create the main figure
        self.fig = plt.figure(figsize=(14, 9), facecolor='#1e1e1e')
        self.fig.suptitle('Bluetooth Packet Sniffer - Live Analysis', 
                         fontsize=16, color='white', fontweight='bold')
        
        # Create subplots
        self.setup_plots()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Animation
        self.ani = animation.FuncAnimation(self.fig, self.update_plots, 
                                          interval=1000, blit=False, 
                                          save_count=1000, cache_frame_data=False)
        
        # Control panel
        self.create_control_panel()
        
    def setup_plots(self):
        """Setup all the subplots"""
        # Create a 3x2 grid
        gs = self.fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. Packet Timeline (top left)
        self.ax1 = self.fig.add_subplot(gs[0, 0])
        self.ax1.set_title('Packet Timeline', color='white', fontweight='bold')
        self.ax1.set_xlabel('Time', color='white')
        self.ax1.set_ylabel('Packets/sec', color='white')
        self.ax1.grid(True, alpha=0.3)
        
        # 2. Protocol Distribution (top right)
        self.ax2 = self.fig.add_subplot(gs[0, 1])
        self.ax2.set_title('Protocol Distribution', color='white', fontweight='bold')
        
        # 3. Device Activity (middle left)
        self.ax3 = self.fig.add_subplot(gs[1, 0])
        self.ax3.set_title('Device Activity', color='white', fontweight='bold')
        self.ax3.set_xlabel('Time', color='white')
        self.ax3.set_ylabel('Signal Strength (dBm)', color='white')
        self.ax3.grid(True, alpha=0.3)
        
        # 4. Signal Strength Heatmap (middle right)
        self.ax4 = self.fig.add_subplot(gs[1, 1])
        self.ax4.set_title('Signal Strength Heatmap', color='white', fontweight='bold')
        
        # 5. Packet Size Distribution (bottom left)
        self.ax5 = self.fig.add_subplot(gs[2, 0])
        self.ax5.set_title('Packet Size Distribution', color='white', fontweight='bold')
        self.ax5.set_xlabel('Packet Size (bytes)', color='white')
        self.ax5.set_ylabel('Frequency', color='white')
        
        # 6. Network Topology (bottom right)
        self.ax6 = self.fig.add_subplot(gs[2, 1])
        self.ax6.set_title('Network Topology', color='white', fontweight='bold')
        self.ax6.set_aspect('equal')
        
        # Initialize empty plots
        self.init_plots()
        
    def init_plots(self):
        """Initialize empty plots"""
        # Timeline
        self.timeline_line, = self.ax1.plot([], [], 'cyan', linewidth=2, alpha=0.8)
        
        # Protocol pie chart
        self.protocol_pie = None
        
        # Device activity scatter
        self.device_scatter = self.ax3.scatter([], [], c=[], s=50, alpha=0.7, cmap='viridis')
        
        # Signal heatmap
        self.signal_heatmap = None
        
        # Packet size histogram
        self.packet_hist = None
        
        # Network topology
        self.topology_scatter = self.ax6.scatter([], [], c=[], s=100, alpha=0.8, cmap='plasma')
        
    def create_control_panel(self):
        """Create control panel"""
        control_frame = tk.Frame(self.root, bg='#2d2d2d', height=100)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Start/Stop button
        self.start_btn = tk.Button(control_frame, text="Start Sniffing", 
                                 command=self.toggle_sniffing, bg='#4CAF50', fg='white',
                                 font=('Arial', 12, 'bold'))
        self.start_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(control_frame, text="Status: Stopped", 
                                   bg='#2d2d2d', fg='white', font=('Arial', 12))
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Packet count
        self.packet_label = tk.Label(control_frame, text="Packets: 0", 
                                   bg='#2d2d2d', fg='cyan', font=('Arial', 12, 'bold'))
        self.packet_label.pack(side=tk.LEFT, padx=20)
        
        # Device count
        self.device_label = tk.Label(control_frame, text="Devices: 0", 
                                   bg='#2d2d2d', fg='magenta', font=('Arial', 12, 'bold'))
        self.device_label.pack(side=tk.LEFT, padx=20)
        
        # Export button
        export_btn = tk.Button(control_frame, text="Export Data", 
                             command=self.export_data, bg='#2196F3', fg='white',
                             font=('Arial', 12, 'bold'))
        export_btn.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.is_sniffing = False
        
    def toggle_sniffing(self):
        """Toggle sniffing on/off"""
        if not self.is_sniffing:
            self.start_sniffing()
        else:
            self.stop_sniffing()
            
    def start_sniffing(self):
        """Start packet sniffing simulation"""
        self.is_sniffing = True
        self.start_btn.config(text="Stop Sniffing", bg='#f44336')
        self.status_label.config(text="Status: Sniffing...", fg='#4CAF50')
        
        # Start simulation thread
        self.sim_thread = threading.Thread(target=self.simulate_packets)
        self.sim_thread.daemon = True
        self.sim_thread.start()
        
    def stop_sniffing(self):
        """Stop packet sniffing"""
        self.is_sniffing = False
        self.start_btn.config(text="Start Sniffing", bg='#4CAF50')
        self.status_label.config(text="Status: Stopped", fg='white')
        
    def simulate_packets(self):
        """Simulate realistic Bluetooth packet data"""
        import random
        
        devices = [
            {'mac': 'AA:BB:CC:DD:EE:FF', 'name': 'iPhone 13', 'type': 'Phone', 'x': 0.2, 'y': 0.3},
            {'mac': '11:22:33:44:55:66', 'name': 'AirPods Pro', 'type': 'Audio', 'x': 0.7, 'y': 0.2},
            {'mac': 'FF:EE:DD:CC:BB:AA', 'name': 'Samsung Galaxy', 'type': 'Phone', 'x': 0.3, 'y': 0.8},
            {'mac': '55:44:33:22:11:00', 'name': 'Bluetooth Speaker', 'type': 'Audio', 'x': 0.8, 'y': 0.7},
            {'mac': '99:88:77:66:55:44', 'name': 'Smart Watch', 'type': 'Wearable', 'x': 0.5, 'y': 0.5},
        ]
        
        protocols = ['HCI', 'L2CAP', 'RFCOMM', 'SDP', 'AVDTP', 'A2DP', 'HID', 'GATT']
        
        start_time = time.time()
        while self.is_sniffing:
            device = random.choice(devices)
            protocol = random.choice(protocols)
            
            packet = {
                'timestamp': datetime.now(),
                'device': device,
                'protocol': protocol,
                'size': random.randint(20, 1500),
                'signal_strength': random.randint(-80, -20),
                'direction': random.choice(['TX', 'RX'])
            }
            
            self.add_packet(packet)
            time.sleep(random.uniform(0.1, 1.0))
            
    def add_packet(self, packet):
        """Add packet to visualization data"""
        self.packet_data.append(packet)
        
        # Update device data
        mac = packet['device']['mac']
        if mac not in self.device_data:
            self.device_data[mac] = {
                'name': packet['device']['name'],
                'packets': 0,
                'last_seen': packet['timestamp'],
                'signal_history': deque(maxlen=50)
            }
        
        self.device_data[mac]['packets'] += 1
        self.device_data[mac]['last_seen'] = packet['timestamp']
        self.device_data[mac]['signal_history'].append(packet['signal_strength'])
        
        # Update protocol data
        self.protocol_data.append(packet['protocol'])
        
        # Update signal data
        self.signal_data.append(packet['signal_strength'])
        
        # Update timeline
        self.timeline_data.append({
            'timestamp': packet['timestamp'],
            'count': len(self.packet_data)
        })
        
    def update_plots(self, frame):
        """Update all plots with new data"""
        if not self.packet_data:
            return
            
        # Update packet count
        self.packet_label.config(text=f"Packets: {len(self.packet_data)}")
        self.device_label.config(text=f"Devices: {len(self.device_data)}")
        
        # 1. Timeline plot
        if len(self.timeline_data) > 1:
            times = [d['timestamp'] for d in self.timeline_data]
            counts = [d['count'] for d in self.timeline_data]
            
            self.ax1.clear()
            self.ax1.plot(times, counts, 'cyan', linewidth=2, alpha=0.8)
            self.ax1.set_title('Packet Timeline', color='white', fontweight='bold')
            self.ax1.set_xlabel('Time', color='white')
            self.ax1.set_ylabel('Total Packets', color='white')
            self.ax1.grid(True, alpha=0.3)
            self.ax1.tick_params(colors='white')
        
        # 2. Protocol distribution
        if self.protocol_data:
            protocol_counts = {}
            for protocol in self.protocol_data:
                protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
            
            if protocol_counts:
                self.ax2.clear()
                protocols = list(protocol_counts.keys())
                counts = list(protocol_counts.values())
                colors = plt.cm.Set3(np.linspace(0, 1, len(protocols)))
                
                wedges, texts, autotexts = self.ax2.pie(counts, labels=protocols, autopct='%1.1f%%', 
                                                      colors=colors, startangle=90)
                self.ax2.set_title('Protocol Distribution', color='white', fontweight='bold')
                
                # Style the text
                for text in texts:
                    text.set_color('white')
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
        
        # 3. Device activity
        if self.device_data:
            self.ax3.clear()
            for mac, data in self.device_data.items():
                if data['signal_history']:
                    times = list(range(len(data['signal_history'])))
                    signals = list(data['signal_history'])
                    self.ax3.plot(times, signals, 'o-', label=data['name'], alpha=0.7, linewidth=2)
            
            self.ax3.set_title('Device Signal Activity', color='white', fontweight='bold')
            self.ax3.set_xlabel('Time Steps', color='white')
            self.ax3.set_ylabel('Signal Strength (dBm)', color='white')
            self.ax3.grid(True, alpha=0.3)
            self.ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            self.ax3.tick_params(colors='white')
        
        # 4. Signal strength heatmap
        if len(self.signal_data) > 10:
            self.ax4.clear()
            # Create a 2D histogram of signal strength over time
            signal_array = np.array(list(self.signal_data))
            time_bins = np.linspace(0, len(signal_array), 20)
            signal_bins = np.linspace(signal_array.min(), signal_array.max(), 20)
            
            hist, xedges, yedges = np.histogram2d(range(len(signal_array)), signal_array, 
                                                bins=[time_bins, signal_bins])
            
            im = self.ax4.imshow(hist.T, extent=[0, len(signal_array), signal_array.min(), signal_array.max()], 
                               aspect='auto', cmap='viridis', origin='lower')
            self.ax4.set_title('Signal Strength Heatmap', color='white', fontweight='bold')
            self.ax4.set_xlabel('Time', color='white')
            self.ax4.set_ylabel('Signal Strength (dBm)', color='white')
            self.ax4.tick_params(colors='white')
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=self.ax4)
            cbar.set_label('Packet Density', color='white')
            cbar.ax.tick_params(colors='white')
        
        # 5. Packet size distribution
        if self.packet_data:
            sizes = [p['size'] for p in self.packet_data]
            self.ax5.clear()
            self.ax5.hist(sizes, bins=20, alpha=0.7, color='orange', edgecolor='white')
            self.ax5.set_title('Packet Size Distribution', color='white', fontweight='bold')
            self.ax5.set_xlabel('Packet Size (bytes)', color='white')
            self.ax5.set_ylabel('Frequency', color='white')
            self.ax5.grid(True, alpha=0.3)
            self.ax5.tick_params(colors='white')
        
        # 6. Network topology
        if self.device_data:
            self.ax6.clear()
            x_coords = []
            y_coords = []
            colors = []
            sizes = []
            labels = []
            
            for mac, data in self.device_data.items():
                # Use device position from simulation
                device = {'mac': mac, 'x': 0.5, 'y': 0.5}
                x_coords.append(device['x'])
                y_coords.append(device['y'])
                colors.append(data['packets'])
                sizes.append(min(200, max(50, data['packets'] * 10)))
                labels.append(data['name'])
            
            if x_coords:
                scatter = self.ax6.scatter(x_coords, y_coords, c=colors, s=sizes, 
                                        alpha=0.8, cmap='plasma', edgecolors='white', linewidth=2)
                
                # Add labels
                for i, label in enumerate(labels):
                    self.ax6.annotate(label, (x_coords[i], y_coords[i]), 
                                    xytext=(5, 5), textcoords='offset points',
                                    fontsize=8, color='white', fontweight='bold')
                
                self.ax6.set_title('Network Topology', color='white', fontweight='bold')
                self.ax6.set_xlim(-0.1, 1.1)
                self.ax6.set_ylim(-0.1, 1.1)
                self.ax6.set_aspect('equal')
                self.ax6.grid(True, alpha=0.3)
                self.ax6.tick_params(colors='white')
        
        # Update canvas
        self.canvas.draw()
        
    def export_data(self):
        """Export captured data"""
        import json
        
        export_data = {
            'packets': list(self.packet_data),
            'devices': dict(self.device_data),
            'protocols': list(self.protocol_data),
            'timeline': list(self.timeline_data)
        }
        
        filename = f"bluetooth_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, default=str, indent=2)
            
            # Show success message
            success_window = tk.Toplevel(self.root)
            success_window.title("Export Successful")
            success_window.geometry("300x100")
            success_window.configure(bg='#2d2d2d')
            
            tk.Label(success_window, text=f"Data exported to {filename}", 
                    bg='#2d2d2d', fg='white', font=('Arial', 12)).pack(expand=True)
            
        except Exception as e:
            print(f"Export error: {e}")
    
    def run(self):
        """Run the visualizer"""
        self.root.mainloop()

def start_visualizer():
    """Start the advanced visualizer"""
    if not MATPLOTLIB_AVAILABLE:
        print("Error: matplotlib/tkinter not available. Please install required dependencies:")
        print("pip install matplotlib seaborn tkinter")
        return
    
    visualizer = BluetoothVisualizer()
    visualizer.run()

if __name__ == "__main__":
    start_visualizer()
