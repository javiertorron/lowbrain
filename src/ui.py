import curses
from scan.scan_ui import ScanUI

class UI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)  # Hide the cursor
        self.height, self.width = self.stdscr.getmaxyx()
        self.menu_items = ["Escanear", "Control en tiempo real", "Registros", "Opciones", "Salir"]
        self.current_selection = 0

    def draw_title(self):
        title = "Low Brain IDS"
        x = (self.width - len(title)) // 2
        self.stdscr.addstr(0, x, title, curses.A_BOLD)

    def draw_menu(self):
        menu_height = len(self.menu_items)
        menu_width = max(len(item) for item in self.menu_items) + 4
        start_y = (self.height - menu_height) // 2
        start_x = (self.width - menu_width) // 2

        for idx, item in enumerate(self.menu_items):
            y = start_y + idx
            x = start_x + 2
            if idx == self.current_selection:
                self.stdscr.attron(curses.color_pair(1))
                self.stdscr.addstr(y, start_x, " " * menu_width)
                self.stdscr.addstr(y, x, item)
                self.stdscr.attroff(curses.color_pair(1))
            else:
                self.stdscr.attron(curses.color_pair(2))
                self.stdscr.addstr(y, x, item)
                self.stdscr.attroff(curses.color_pair(2))

    def draw_status_bar(self):
        status_text = "w/s - navegar | enter - seleccionar | q - salir"
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.addstr(self.height-1, 0, status_text.ljust(self.width))
        self.stdscr.attroff(curses.color_pair(3))

    def run(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        while True:
            self.stdscr.clear()
            self.draw_title()
            self.draw_menu()
            self.draw_status_bar()
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key == ord('w') and self.current_selection > 0:
                self.current_selection -= 1
            elif key == ord('s') and self.current_selection < len(self.menu_items) - 1:
                self.current_selection += 1
            elif key == 10:  # Enter key
                if self.current_selection == 0:
                    scan_ui = ScanUI(self.stdscr)
                    scan_ui.run()
                elif self.current_selection == 4:
                    break  # Exit
            elif key == ord('q'):  # q key to quit
                break

        curses.endwin()