import curses

class RealTime:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = self.stdscr.getmaxyx()

    def draw(self):
        self.stdscr.clear()
        title = "Control en tiempo real"
        x = (self.width - len(title)) // 2
        self.stdscr.addstr(0, x, title, curses.A_BOLD)
        self.stdscr.addstr(2, 2, "Presione 'q' para volver al menú principal")
        self.stdscr.addstr(4, 2, "Aquí irá la funcionalidad de control en tiempo real...")

    def run(self):
        while True:
            self.draw()
            self.stdscr.refresh()
            key = self.stdscr.getch()
            if key == ord('q'):
                break