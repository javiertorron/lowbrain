import curses
from .scan_handler import ScanHandler

class ScanUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = self.stdscr.getmaxyx()
        self.current_selection = 0
        self.scroll_offset = 0
        self.scan_handler = ScanHandler()

    def draw_header(self):
        header = f"{'NOMBRE':<20} {'#':>5} {'CPU%':>8} {'MEM%':>8} {'RED':>5} {'TIPO':<15}"
        self.stdscr.attron(curses.color_pair(4))
        self.stdscr.addstr(0, 0, header.ljust(self.width))
        self.stdscr.attroff(curses.color_pair(4))

    def draw_processes(self):
        processes = self.scan_handler.get_grouped_processes()
        for idx, proc in enumerate(processes[self.scroll_offset:self.scroll_offset+self.height-3]):
            if idx + self.scroll_offset == self.current_selection:
                self.stdscr.attron(curses.color_pair(1))
            
            name = f"{proc['name'][:20]:<20}"
            count = f"{proc['count']:5}"
            cpu = f"{proc['cpu_percent']:8.1f}"
            mem = f"{proc['memory_percent']:8.1f}"
            net = f"{proc['net_usage']:5}"
            ptype = f"{proc['type'][:15]:<15}"
            
            line = f"{name} {count} {cpu} {mem} {net} {ptype}"
            
            if "Shell" in proc['type']:
                self.stdscr.attron(curses.color_pair(2))
            elif "Trojan" in proc['type']:
                self.stdscr.attron(curses.color_pair(3))
            
            self.stdscr.addstr(idx+1, 0, line[:self.width-1])
            
            if "Shell" in proc['type'] or "Trojan" in proc['type']:
                self.stdscr.attroff(curses.color_pair(2) | curses.color_pair(3))
            
            if idx + self.scroll_offset == self.current_selection:
                self.stdscr.attroff(curses.color_pair(1))

    def draw_status_bar(self):
        status_text = "q - volver | w/s - arriba/abajo | enter - detalles | r - actualizar"
        self.stdscr.attron(curses.color_pair(4))
        self.stdscr.addstr(self.height-1, 0, status_text.ljust(self.width))
        self.stdscr.attroff(curses.color_pair(4))

    def draw_floating_window(self):
        processes = self.scan_handler.get_grouped_processes()
        selected_group = processes[self.current_selection]
        group_processes = selected_group['processes']
        
        win_height = min(len(group_processes) + 4, self.height - 4)
        win_width = self.width - 4
        win_y = (self.height - win_height) // 2
        win_x = 2
        
        win = curses.newwin(win_height, win_width, win_y, win_x)
        win.box()
        win.addstr(1, 2, f"Procesos de {selected_group['name']} (Total: {len(group_processes)}):")
        win.addstr(2, 2, f"{'PID':>7} {'CPU%':>8} {'MEM%':>8} {'RED':>5} {'TIPO':<25}")
        
        for idx, proc in enumerate(group_processes[:win_height-4]):
            pid = f"{proc['pid']:7}"
            cpu = f"{proc['cpu_percent']:8.1f}"
            mem = f"{proc['memory_percent']:8.1f}"
            net = f"{proc['net_usage']:5}"
            ptype = f"{proc['type'][:25]:<25}"
            
            line = f"{pid} {cpu} {mem} {net} {ptype}"
            win.addstr(idx+3, 2, line[:win_width-4])
        
        win.refresh()
        win.getch()

    def draw(self):
        self.stdscr.clear()
        self.draw_header()
        self.draw_processes()
        self.draw_status_bar()
        self.stdscr.refresh()

    def run(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected process
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Reverse Shell
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Trojan
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Header and status bar

        while True:
            self.draw()
            
            key = self.stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('w'):
                self.current_selection = max(0, self.current_selection - 1)
                if self.current_selection < self.scroll_offset:
                    self.scroll_offset = self.current_selection
            elif key == ord('s'):
                max_selection = len(self.scan_handler.get_grouped_processes()) - 1
                self.current_selection = min(max_selection, self.current_selection + 1)
                if self.current_selection >= self.scroll_offset + self.height - 3:
                    self.scroll_offset = self.current_selection - (self.height - 4)
            elif key == 10:  # Enter key
                self.draw_floating_window()
            elif key == ord('r'):
                self.scan_handler.refresh_processes()