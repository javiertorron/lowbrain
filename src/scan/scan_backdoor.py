class ScanBackdoor:
    def __init__(self):
        self.suspicious_ports = [4444, 5555, 6666, 7777, 8888, 9999]

    def is_potential_backdoor(self, pinfo):
        # Check for listening on suspicious ports
        for conn in pinfo['connections']:
            if conn.status == 'LISTEN' and conn.laddr.port in self.suspicious_ports:
                return True
        
        # Check for suspicious process names
        if any(name in pinfo['name'].lower() for name in ['backdoor', 'rat', 'remote']):
            return True
        
        return False