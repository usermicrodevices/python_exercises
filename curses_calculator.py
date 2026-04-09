#!/usr/bin/env python3
"""
AI powered Console Calculator with Powers using Curses (standard library)
- Supports arithmetic (+, -, *, /) and exponentiation (^ or **)
- Handles 'ans' variable for previous result
- Provides math functions: sqrt, sin, cos, tan, log, log10, exp, abs, round
- Uses curses for a polished, colorful interface
- Works on Unix-like systems (Linux, macOS); for Windows install windows-curses
"""

import math
import curses
from typing import Union, Optional, List, Tuple

# ----------------------------------------------------------------------
# Safe evaluation (same as before, no changes needed)
# ----------------------------------------------------------------------
ALLOWED_NAMES = {
    "ans": 0.0,
    "pi": math.pi,
    "e": math.e,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "round": round,
}

def safe_eval(expr: str, last_result: Union[int, float]) -> Union[int, float]:
    """Evaluate expression with ^ replaced by ** and 'ans' variable."""
    # Replace caret with Python exponent operator
    expr = expr.replace('^', '**')
    # Replace 'ans' with last result (case‑insensitive)
    expr = expr.replace('ans', str(last_result))
    local_ns = ALLOWED_NAMES.copy()
    local_ns["ans"] = last_result
    return eval(expr, {"__builtins__": {}}, local_ns)

# ----------------------------------------------------------------------
# Curses GUI
# ----------------------------------------------------------------------
class CursesCalculator:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.history: List[Tuple[str, Union[str, float]]] = []  # (expr, result_or_error)
        self.last_result = 0.0
        self.max_history_lines = 20   # lines shown in output area
        self.init_colors()

    def init_colors(self):
        """Set up color pairs."""
        curses.start_color()
        curses.use_default_colors()
        # Define color pairs (foreground, background)
        #  -1 means default background
        curses.init_pair(1, curses.COLOR_CYAN, -1)    # borders / titles
        curses.init_pair(2, curses.COLOR_YELLOW, -1)  # expression
        curses.init_pair(3, curses.COLOR_GREEN, -1)   # result
        curses.init_pair(4, curses.COLOR_RED, -1)     # error
        curses.init_pair(5, curses.COLOR_MAGENTA, -1) # prompt / special symbols
        curses.init_pair(6, curses.COLOR_WHITE, -1)   # normal text
        self.color_border = curses.color_pair(1) | curses.A_BOLD
        self.color_expr = curses.color_pair(2)
        self.color_result = curses.color_pair(3)
        self.color_error = curses.color_pair(4) | curses.A_BOLD
        self.color_prompt = curses.color_pair(5) | curses.A_BOLD
        self.color_normal = curses.color_pair(6)

    def draw_border(self, win, title: str = ""):
        """Draw a border around a window with an optional title."""
        height, width = win.getmaxyx()
        win.border(0)
        if title:
            # place title in the top border
            try:
                win.addstr(0, 2, f" {title} ", self.color_border)
            except curses.error:
                pass

    def format_number(self, num: Union[int, float]) -> str:
        """Return a nicely formatted number (no trailing .0 for integers)."""
        if isinstance(num, float) and num.is_integer():
            return str(int(num))
        # limit decimal places for readability
        return f"{num:.10g}".rstrip('0').rstrip('.')

    def display_history(self, output_win):
        """Show the calculation history inside the output window."""
        output_win.clear()
        self.draw_border(output_win, " History ")
        max_y, max_x = output_win.getmaxyx()
        # Leave 2 lines for borders + 1 for bottom margin
        usable_lines = max_y - 3
        # Show the last 'usable_lines' entries
        start = max(0, len(self.history) - usable_lines)
        for idx, (expr, result_or_err) in enumerate(self.history[start:]):
            if idx >= usable_lines:
                break
            line_y = idx + 1
            # Truncate if too long
            expr_display = expr[:max_x - 20]
            if isinstance(result_or_err, str):  # error
                text = f"{expr_display}  →  [ERROR] {result_or_err}"
                color = self.color_error
            else:
                res_str = self.format_number(result_or_err)
                text = f"{expr_display}  →  {res_str}"
                color = self.color_expr
            try:
                output_win.addstr(line_y, 2, text[:max_x-4], color)
            except curses.error:
                pass
        output_win.refresh()

    def display_input_prompt(self, input_win, user_input: str = ""):
        """Show the input line with a prompt."""
        input_win.clear()
        self.draw_border(input_win, " Input ")
        height, width = input_win.getmaxyx()
        prompt = "> "
        # Leave space for border and prompt
        max_input_len = width - len(prompt) - 3
        # Display the current input text
        try:
            input_win.addstr(1, 2, prompt, self.color_prompt)
            input_win.addstr(1, 2 + len(prompt), user_input[-max_input_len:], self.color_normal)
        except curses.error:
            pass
        input_win.refresh()

    def show_message(self, output_win, msg: str, is_error=False):
        """Temporarily show a message in the output window (e.g., help)."""
        output_win.clear()
        self.draw_border(output_win, " Message ")
        height, width = output_win.getmaxyx()
        lines = msg.split('\n')
        color = self.color_error if is_error else self.color_normal
        for i, line in enumerate(lines):
            if i >= height - 2:
                break
            try:
                output_win.addstr(i+1, 2, line[:width-4], color)
            except curses.error:
                pass
        output_win.refresh()
        # Wait for a key press
        self.stdscr.getch()

    def get_user_input(self, input_win) -> str:
        """Read a line of input with simple line editing (backspace, enter)."""
        user_input = ""
        self.display_input_prompt(input_win, user_input)
        while True:
            key = self.stdscr.getch()
            if key == ord('\n') or key == ord('\r'):  # Enter
                break
            elif key == 127 or key == curses.KEY_BACKSPACE or key == 8:  # Backspace
                if user_input:
                    user_input = user_input[:-1]
                    self.display_input_prompt(input_win, user_input)
            elif key == 27:  # Escape – treat as cancel (return empty)
                user_input = ""
                break
            elif 32 <= key <= 126:  # printable ASCII
                user_input += chr(key)
                self.display_input_prompt(input_win, user_input)
        return user_input.strip()

    def show_help(self, output_win):
        """Display help text in the output area."""
        help_text = """
Available operators: +, -, *, /, ** or ^ for power
Parentheses: (2+3)*4
Special variable: ans (previous result)

Math functions & constants:
sqrt, sin, cos, tan, log, log10, exp, abs, round
pi, e

Commands:
  help   – show this help
  clear  – clear history
  quit   – exit calculator
        """
        self.show_message(output_win, help_text)

    def clear_history(self, output_win):
        """Clear the calculation history."""
        self.history.clear()
        self.display_history(output_win)

    def add_to_history(self, expr: str, result: Optional[Union[int, float]] = None, error: Optional[str] = None):
        """Store an expression and its result or error."""
        if error:
            self.history.append((expr, error))
        else:
            self.history.append((expr, result))
        # Keep history size manageable (optional)
        if len(self.history) > 100:
            self.history = self.history[-100:]

    def run(self):
        """Main calculator loop."""
        # Setup curses
        curses.curs_set(1)      # show cursor
        self.stdscr.clear()
        self.stdscr.refresh()

        # Get screen dimensions
        max_y, max_x = self.stdscr.getmaxyx()
        # Create two windows: output (top) and input (bottom)
        output_height = max_y - 5
        input_height = 3
        output_win = curses.newwin(output_height, max_x, 0, 0)
        input_win = curses.newwin(input_height, max_x, output_height, 0)

        # Initial display
        self.display_history(output_win)
        self.display_input_prompt(input_win)

        while True:
            user_input = self.get_user_input(input_win)
            if not user_input:
                continue

            cmd = user_input.lower()
            if cmd in ('quit', 'exit', 'q'):
                break
            elif cmd == 'help':
                self.show_help(output_win)
                self.display_history(output_win)   # restore history
                continue
            elif cmd == 'clear':
                self.clear_history(output_win)
                continue

            # Evaluate expression
            try:
                result = safe_eval(user_input, self.last_result)
                self.last_result = result
                self.add_to_history(user_input, result=result)
                self.display_history(output_win)
            except ZeroDivisionError:
                self.add_to_history(user_input, error="Division by zero")
                self.display_history(output_win)
            except (SyntaxError, NameError, TypeError, ValueError) as e:
                self.add_to_history(user_input, error=f"Invalid: {e}")
                self.display_history(output_win)
            except Exception as e:
                self.add_to_history(user_input, error=f"Error: {e}")
                self.display_history(output_win)

# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
def main(stdscr):
    calc = CursesCalculator(stdscr)
    calc.run()

if __name__ == "__main__":
    curses.wrapper(main)
