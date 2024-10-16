class ScanTrojan:
    def __init__(self):
        self.cpu_threshold = 50
        self.memory_threshold = 50

    def is_potential_trojan(self, pinfo):
        # This is a very basic check. In a real-world scenario, you'd want more sophisticated detection methods.
        if pinfo['cpu_percent'] > self.cpu_threshold and pinfo['memory_percent'] > self.memory_threshold:
            return True
        return False