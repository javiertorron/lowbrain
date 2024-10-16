import psutil
from collections import defaultdict
from .scan_reverse_shell import ScanReverseShell
from .scan_trojan import ScanTrojan
from .scan_backdoor import ScanBackdoor

class ScanHandler:
    def __init__(self):
        self.processes = []
        self.grouped_processes = []
        self.reverse_shell_scanner = ScanReverseShell()
        self.trojan_scanner = ScanTrojan()
        self.backdoor_scanner = ScanBackdoor()

    def refresh_processes(self):
        self.processes = self.get_processes()
        self.grouped_processes = self.group_processes(self.processes)

    def get_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'connections', 'cmdline', 'exe']):
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent', 'connections', 'cmdline', 'exe'])
                pinfo['net_usage'] = sum(conn.laddr.port != 0 for conn in pinfo['connections'])
                pinfo['outbound_connections'] = [conn for conn in pinfo['connections'] if conn.type == psutil.SOCK_STREAM and conn.status == psutil.CONN_ESTABLISHED and conn.raddr]
                pinfo['type'] = self.classify_process(pinfo)
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes

    def classify_process(self, pinfo):
        if self.reverse_shell_scanner.is_potential_reverse_shell(pinfo):
            return "Potential Reverse Shell"
        elif self.trojan_scanner.is_potential_trojan(pinfo):
            return "Potential Trojan"
        elif self.backdoor_scanner.is_potential_backdoor(pinfo):
            return "Potential Backdoor"
        else:
            return "Normal"

    def group_processes(self, processes):
        groups = defaultdict(list)
        for proc in processes:
            groups[proc['name']].append(proc)
        
        grouped = []
        for name, procs in groups.items():
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
        
        return sorted(grouped, key=lambda x: x['cpu_percent'], reverse=True)

    def get_grouped_processes(self):
        if not self.grouped_processes:
            self.refresh_processes()
        return self.grouped_processes