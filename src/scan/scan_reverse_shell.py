import psutil

class ScanReverseShell:
    def __init__(self):
        self.suspicious_paths = ['/tmp', '/dev/shm', '/run']
        self.suspicious_names = ['nc', 'netcat', 'ncat', 'socat', 'bash', 'python', 'perl', 'ruby']

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