import curses
import psutil
import time
from collections import defaultdict
import os

class Scan:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = self.stdscr.getmaxyx()
        self.processes = []
        self.grouped_processes = []
        self.sort_key = 'cpu_percent'
        self.sort_reverse = True
        self.current_selection = 0
        self.scroll_offset = 0
        self.suspicious_paths = ['/tmp', '/dev/shm', '/run']
        self.suspicious_names = ['nc', 'netcat', 'ncat', 'socat', 'bash', 'python', 'perl', 'ruby']

    def get_processes(self):
        processes = defaultdict(list)
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'connections', 'cmdline', 'exe']):
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent', 'connections', 'cmdline', 'exe'])
                pinfo['net_usage'] = sum(conn.laddr.port != 0 for conn in pinfo['connections'])
                pinfo['outbound_connections'] = [conn for conn in pinfo['connections'] if conn.type == socket.SOCK_STREAM and conn.status == psutil.CONN_ESTABLISHED and conn.raddr]
                pinfo['port'] = self.get_listening_port(pinfo['connections'])
                pinfo['type'] = self.classify_process(pinfo)
                processes[pinfo['name']].append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        grouped = []
        for name, procs in processes.items():
            group = {
                'name': name,
                'count': len(procs),
                'cpu_percent': sum(p['cpu_percent'] for p in procs),
                'memory_percent': sum(p['memory_percent'] for p in procs),
                'net_usage': sum(p['net_usage'] for p in procs),
                'type': max(set(p['type'] for p in procs), key=lambda t: procs.count({'type': t}.items())),
                'processes': procs
            }
            grouped.append(group)
        
        return sorted(grouped, key=lambda x: x[self.sort_key], reverse=self.sort_reverse)

    def get_listening_port(self, connections):
        listening_conns = [conn for conn in connections if conn.status == 'LISTEN']
        return listening_conns[0].laddr.port if listening_conns else "-"

    def classify_process(self, pinfo):
        if self.is_potential_reverse_shell(pinfo):
            return "Potential Reverse Shell"
        elif pinfo['cpu_percent'] > 50 and pinfo['memory_percent'] > 50:
            return "High Resource Usage"
        else:
            return "Normal"

    def is_potential_reverse_shell(self, pinfo):
        # Check for suspicious executable paths
        if pinfo['exe'] and any(path in pinfo['exe'] for path in self.suspicious_paths):
            return True
        
        # Check for suspicious process names
        if any(name in pinfo['name'].lower() for name in self.suspicious_names):
            return True
        
        # Check for unusual network activity
        if pinfo['outbound_connections'] and pinfo['name'].lower() not in ['chrome', 'firefox', 'iexplore', 'edge']:
            return True
        
        # Check for shell processes with network activity
        if pinfo['name'].lower() in ['cmd.exe', 'powershell.exe', 'bash.exe'] and pinfo['net_usage'] > 0:
            return True
        
        # Check for suspicious command line arguments
        if pinfo['cmdline']:
            cmdline = ' '.join(pinfo['cmdline']).lower()
            if any(term in cmdline for term in ['-e', 'sh', 'bash', 'cmd.exe', '/c', 'powershell']):
                return True
        
        return False

    # ... [rest of the methods remain the same] ...

    def draw_floating_window(self):
        selected_group = self.grouped_processes[self.current_selection]
        processes = selected_group['processes']
        
        win_height = min(len(processes) + 4, self.height - 4)
        win_width = self.width - 4
        win_y = (self.height - win_height) // 2
        win_x = 2
        
        win = curses.newwin(win_height, win_width, win_y, win_x)
        win.box()
        win.addstr(1, 2, f"Procesos de {selected_group['name']} (Total: {len(processes)}):")
        win.addstr(2, 2, f"{'PID':>7} {'CPU%':>8} {'MEM%':>8} {'RED':>5} {'TIPO':<25}")
        
        for idx, proc in enumerate(processes[:win_height-4]):
            pid = f"{proc['pid']:7}"
            cpu = f"{proc['cpu_percent']:8.1f}"
            mem = f"{proc['memory_percent']:8.1f}"
            net = f"{proc['net_usage']:5}"
            ptype = f"{proc['type']:<25}"
            
            line = f"{pid} {cpu} {mem} {net} {ptype}"
            win.addstr(idx+3, 2, line[:win_width-4])
        
        win.refresh()
        win.getch()

    # ... [rest of the methods remain the same] ...