import tkinter as tk
from collections import deque
import copy
import colorsys

BG = "#121212"
PANEL = "#1e1e1e"
ACCENT = "#2a2a2a"
TEXT = "#ffffff"


class FlowApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Flower 3000")
        self.root.configure(bg=BG)
        self.root.geometry("1000x900")
        self.root.minsize(700, 700)

        self.size = 6
        self.current_color = 1
        self.endpoints = {}
        self.frames = []
        self.colors = {}
        self.cell = 40

        self.build_ui()
        self.new_grid()

    # ui

    def build_ui(self):

        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(fill="both", expand=True, padx=20, pady=20)

        self.topbar = tk.Frame(self.main, bg=BG)
        self.topbar.pack(fill="x", pady=(0,15))

        self.size_var = tk.IntVar(value=6)

        self.size_box = tk.Spinbox(
            self.topbar,
            from_=5, to=14,
            textvariable=self.size_var,
            width=5,
            bg=PANEL,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat"
        )
        self.size_box.pack(side="left", padx=(0,10))

        self.make_button(self.topbar, "New Grid", self.new_grid).pack(side="left", padx=5)
        self.make_button(self.topbar, "Solve", self.solve).pack(side="left", padx=5)
        self.make_button(self.topbar, "Clear", self.clear).pack(side="left", padx=5)

        self.palette_frame = tk.Frame(self.main, bg=BG)
        self.palette_frame.pack(pady=10)

        self.canvas_frame = tk.Frame(self.main, bg=PANEL)
        self.canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg=PANEL,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self.on_resize)

    def make_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=PANEL,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground=TEXT,
            relief="flat",
            padx=15,
            pady=6,
            cursor="hand2"
        )

    # resize

    def on_resize(self, event):
        size = min(event.width, event.height)
        self.cell = size // self.size
        self.draw()

    # colors

    def generate_colors(self, count):
        colors = {}
        for i in range(count):
            hue = i / count
            r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
            colors[i+1] = "#%02x%02x%02x" % (
                int(r*255), int(g*255), int(b*255)
            )
        return colors

    def build_palette(self):

        for widget in self.palette_frame.winfo_children():
            widget.destroy()

        max_pairs = (self.size * self.size) // 2
        self.colors = self.generate_colors(max_pairs)

        columns = 12
        row = 0
        col = 0

        for i in range(1, max_pairs+1):

            swatch = tk.Canvas(
                self.palette_frame,
                width=34,
                height=34,
                bg=BG,
                highlightthickness=0,
                cursor="hand2"
            )

            swatch.create_oval(
                5, 5, 29, 29,
                fill=self.colors[i],
                outline=""
            )

            swatch.bind("<Button-1>", lambda e, c=i: self.select_color(c))
            swatch.grid(row=row, column=col, padx=6, pady=6)

            col += 1
            if col >= columns:
                col = 0
                row += 1

    # grid

    def new_grid(self):
        self.size = self.size_var.get()
        self.grid = [[0]*self.size for _ in range(self.size)]
        self.endpoints = {}
        self.frames = []
        self.current_color = 1

        self.build_palette()
        self.draw()

        self.canvas.bind("<Button-1>", self.place_point)

    def clear(self):
        self.new_grid()

    def select_color(self, color):
        self.current_color = color

    def place_point(self, event):

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        size = min(canvas_w, canvas_h)
        offset_x = (canvas_w - size) // 2
        offset_y = (canvas_h - size) // 2

        x = event.x - offset_x
        y = event.y - offset_y

        if x < 0 or y < 0:
            return

        c = x // self.cell
        r = y // self.cell

        if r >= self.size or c >= self.size:
            return

        if self.grid[r][c] != 0:
            return

        color = self.current_color

        if color not in self.endpoints:
            self.endpoints[color] = []

        if len(self.endpoints[color]) >= 2:
            return

        self.endpoints[color].append((r, c))
        self.grid[r][c] = color
        self.draw()

    def draw(self, state=None):

        if state is None:
            state = self.grid

        self.canvas.delete("all")

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        size = min(canvas_w, canvas_h)
        offset_x = (canvas_w - size) // 2
        offset_y = (canvas_h - size) // 2

        for r in range(self.size):
            for c in range(self.size):

                x1 = offset_x + c*self.cell
                y1 = offset_y + r*self.cell
                x2 = x1+self.cell
                y2 = y1+self.cell

                color = state[r][c]
                fill = PANEL

                if color != 0:
                    fill = self.colors.get(color, "#ffffff")

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill,
                    outline="#2f2f2f",
                    width=1
                )

    # solver

    def neighbors(self, r, c):
        for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                yield nr, nc

    def reachable(self, start, end):
        queue = deque([start])
        seen = {start}

        while queue:
            r, c = queue.popleft()
            if (r, c) == end:
                return True

            for nr, nc in self.neighbors(r, c):
                if (nr, nc) not in seen:
                    if self.grid[nr][nc] == 0 or (nr, nc) == end:
                        seen.add((nr, nc))
                        queue.append((nr, nc))
        return False

    def full(self):
        return all(self.grid[r][c] != 0
                   for r in range(self.size)
                   for c in range(self.size))

    def solve(self):

        for c in self.endpoints:
            if len(self.endpoints[c]) != 2:
                return

        self.frames = []

        frontiers = {c:self.endpoints[c][0] for c in self.endpoints}
        targets = {c:self.endpoints[c][1] for c in self.endpoints}

        def dfs():

            if self.full():
                return True

            best_color = None
            best_moves = None

            for color, pos in frontiers.items():

                if pos == targets[color]:
                    continue

                moves = []
                for nr, nc in self.neighbors(*pos):
                    if self.grid[nr][nc] == 0 or (nr, nc) == targets[color]:
                        moves.append((nr, nc))

                if not moves:
                    return False

                if best_moves is None or len(moves) < len(best_moves):
                    best_moves = moves
                    best_color = color

            if best_color is None:
                return False

            color = best_color
            pos = frontiers[color]

            for nr, nc in best_moves:

                old_front = frontiers[color]
                old_cell = self.grid[nr][nc]

                frontiers[color] = (nr, nc)

                if (nr, nc) != targets[color]:
                    self.grid[nr][nc] = color

                valid = True
                for c2 in frontiers:
                    if frontiers[c2] != targets[c2]:
                        if not self.reachable(frontiers[c2], targets[c2]):
                            valid = False
                            break

                if valid:
                    self.frames.append(copy.deepcopy(self.grid))
                    if dfs():
                        return True

                frontiers[color] = old_front
                self.grid[nr][nc] = old_cell

            return False

        if dfs():
            self.animate()

    # animations

    def animate(self):
        self.anim_index = 0

        def step():
            if self.anim_index < len(self.frames):
                self.draw(self.frames[self.anim_index])
                self.anim_index += 1
                self.root.after(15, step)

        step()


root = tk.Tk()
app = FlowApp(root)
root.mainloop()