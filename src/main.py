import curses
from scan.scan_ui import ScanUI

def main(stdscr):
    ui = ScanUI(stdscr)
    ui.run()

if __name__ == "__main__":
    curses.wrapper(main)