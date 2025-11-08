from utils import *
from grid import Grid
from searching_algorithms import *


class Button:
    def __init__(self, x, y, w, h, text, font, color=(200,200,200), text_color=(0,0,0)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.color = color
        self.text_color = text_color

    def draw(self, surface, selected=False):
        bg = self.color if not selected else (max(self.color[0]-30,0), max(self.color[1]-30,0), max(self.color[2]-30,0))
        pygame.draw.rect(surface, bg, self.rect)
        pygame.draw.rect(surface, (0,0,0), self.rect, 2 if selected else 1)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

if __name__ == "__main__":
    pygame.init()
    # setting up how big will be the display window
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))

    # set a caption for the window
    pygame.display.set_caption("Path Visualizing Algorithm")

    ROWS = 50  # number of rows
    COLS = 50  # number of columns

    # --- UI: dropdown selector for algorithms ---
    FONT = pygame.font.SysFont(None, 20)
    btn_h = 28
    margin = 8
    start_x, start_y = margin, margin

    algos = [
        ("BFS", bfs),
        ("DFS", dfs),
        ("A*", astar),
        ("UCS", ucs),
        ("Greedy", greedy_search),
        ("DLS", lambda draw, g, s, e: dls(draw, g, s, e, limit=110)),
        ("IDS", lambda draw, g, s, e: ids(draw, g, s, e, max_depth=50)),
        ("IDA*", ida_star),
    ]

    dropdown_w = 160
    class Dropdown:
        def __init__(self, x, y, w, h, options, font):
            self.rect = pygame.Rect(x, y, w, h)
            self.options = options
            self.font = font
            self.selected = 0
            self.expanded = False

        def draw(self, surface):
            # box
            pygame.draw.rect(surface, (220,220,220), self.rect)
            pygame.draw.rect(surface, (0,0,0), self.rect, 2)
            # selected text
            text = self.options[self.selected][0]
            surf = self.font.render(text, True, (0,0,0))
            surface.blit(surf, (self.rect.x + 6, self.rect.y + (self.rect.h - surf.get_height())//2))
            # dropdown arrow
            pygame.draw.polygon(surface, (0,0,0), [(self.rect.right-18, self.rect.y + self.rect.h//2 - 4), (self.rect.right-6, self.rect.y + self.rect.h//2 - 4), (self.rect.right-12, self.rect.y + self.rect.h//2 + 4)])
            if self.expanded:
                for i, (label, _) in enumerate(self.options):
                    r = pygame.Rect(self.rect.x, self.rect.y + (i+1)*self.rect.h, self.rect.w, self.rect.h)
                    pygame.draw.rect(surface, (245,245,245), r)
                    pygame.draw.rect(surface, (0,0,0), r, 1)
                    surf = self.font.render(label, True, (0,0,0))
                    surface.blit(surf, (r.x + 6, r.y + (r.h - surf.get_height())//2))

        def is_clicked(self, pos):
            return self.rect.collidepoint(pos)

        def option_at(self, pos):
            if not self.expanded:
                return None
            x, y = pos
            if x < self.rect.x or x > self.rect.right:
                return None
            rel = y - self.rect.y
            idx = rel // self.rect.h - 1
            if 0 <= idx < len(self.options):
                return idx
            return None

        def toggle(self):
            self.expanded = not self.expanded

    dropdown = Dropdown(start_x, start_y, dropdown_w, btn_h, algos, FONT)
    # Run and Clear buttons (to right of dropdown)
    run_btn = Button(dropdown.rect.right + margin, start_y, 100, btn_h, "Run", FONT, color=(150,200,150))
    clear_btn = Button(run_btn.rect.x + run_btn.rect.w + margin, start_y, 100, btn_h, "Clear Path", FONT, color=(220,180,180))
    clear_all_btn = Button(clear_btn.rect.x + clear_btn.rect.w + margin, start_y, 100, btn_h, "Clear All", FONT, color=(200,120,120))

    # reserve UI bar height and create a subsurface for the grid below the UI
    ui_bar_h = btn_h + margin * 2
    grid_surface = WIN.subsurface((0, ui_bar_h, WIDTH, HEIGHT - ui_bar_h))
    grid = Grid(grid_surface, ROWS, COLS, WIDTH, HEIGHT - ui_bar_h)

    start = None
    end = None

    
    # flags for running the main loop
    run = True
    started = False
    painting = False
    # throttle drawing during algorithms: draw only every N calls
    DRAW_THROTTLE = 3
    draw_state = { 'count': 0 }

    while run:
        grid.draw()  # draw the grid and its spots
        # draw UI background bar so buttons are always visible
        ui_bar_h = btn_h + margin * 2
        pygame.draw.rect(WIN, (120, 120, 120), (0, 0, WIDTH, ui_bar_h))
        # draw dropdown and UI buttons on top
        dropdown.draw(WIN)
        run_btn.draw(WIN)
        clear_btn.draw(WIN)
        clear_all_btn.draw(WIN)
        # flip the display after drawing grid + UI so dropdown/overlays show correctly
        pygame.display.update()
        for event in pygame.event.get():
            # verify what events happened
            if event.type == pygame.QUIT:
                run = False

            if started:
                # do not allow any other interaction if the algorithm has started
                continue  # ignore other events if algorithm started

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # left click
                if event.button == 1:
                    clicked_ui = False
                    # dropdown click handling
                    if dropdown.is_clicked(pos):
                        # clicked on box -> toggle
                        dropdown.toggle()
                        clicked_ui = True
                    else:
                        opt = dropdown.option_at(pos)
                        if opt is not None:
                            dropdown.selected = opt
                            dropdown.expanded = False
                            clicked_ui = True

                    if run_btn.is_clicked(pos):
                        for row in grid.grid:
                            for spot in row:
                                spot.update_neighbors(grid.grid)
                        started = True
                        _, algo_func = dropdown.options[dropdown.selected]
                        def draw_fn():
                            # pump events to keep window responsive
                            pygame.event.pump()
                            draw_state['count'] += 1
                            if draw_state['count'] % DRAW_THROTTLE == 0:
                                # redraw grid and UI overlays during algorithm
                                grid.draw()
                                # draw UI bar + dropdown/buttons
                                ui_bar_h = btn_h + margin * 2
                                pygame.draw.rect(WIN, (240,240,240), (0, 0, WIDTH, ui_bar_h))
                                dropdown.draw(WIN)
                                run_btn.draw(WIN)
                                clear_btn.draw(WIN)
                                clear_all_btn.draw(WIN)
                                pygame.display.update()
                        algo_func(draw_fn, grid, start, end)
                        started = False
                        clicked_ui = True

                    if clear_btn.is_clicked(pos):
                        for r in grid.grid:
                            for s in r:
                                if not s.is_barrier() and not s.is_start() and not s.is_end():
                                    s.reset()
                        clicked_ui = True

                    if clear_all_btn.is_clicked(pos):
                        start = None
                        end = None
                        grid.reset()
                        clicked_ui = True

                    if clicked_ui:
                        continue

                    # if dropdown is expanded and click outside, collapse
                    if dropdown.expanded and not dropdown.is_clicked(pos) and dropdown.option_at(pos) is None:
                        dropdown.expanded = False
                        continue

                    x, y = pos
                    if y < ui_bar_h:
                        continue
                    grid_x, grid_y = x, y - ui_bar_h
                    row, col = grid.get_clicked_pos((grid_x, grid_y))
                    if row < 0 or col < 0 or row >= ROWS or col >= COLS:
                        continue
                    spot = grid.grid[row][col]
                    if not start and spot != end:
                        start = spot
                        start.make_start()
                    elif not end and spot != start:
                        end = spot
                        end.make_end()
                    elif spot != end and spot != start:
                        spot.make_barrier()

                # right click
                elif event.button == 3:
                    x, y = pos
                    if y < ui_bar_h:
                        continue
                    grid_x, grid_y = x, y - ui_bar_h
                    row, col = grid.get_clicked_pos((grid_x, grid_y))
                    if row < 0 or col < 0 or row >= ROWS or col >= COLS:
                        continue
                    spot = grid.grid[row][col]
                    spot.reset()

                    if spot == start:
                        start = None
                    elif spot == end:
                        end = None

            # handle mouse drag painting for barriers (smooth selection)
            if event.type == pygame.MOUSEMOTION:
                # if left button is held while moving, paint barriers
                if event.buttons[0]:
                    x, y = event.pos
                    if y < ui_bar_h:
                        continue
                    grid_x, grid_y = x, y - ui_bar_h
                    row, col = grid.get_clicked_pos((grid_x, grid_y))
                    if row < 0 or col < 0 or row >= ROWS or col >= COLS:
                        continue
                    spot = grid.grid[row][col]
                    # don't overwrite start/end
                    if not spot.is_start() and not spot.is_end():
                        spot.make_barrier()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    # run the algorithm
                    for row in grid.grid:
                        for spot in row:
                            spot.update_neighbors(grid.grid)
                    started = True
                    # call selected algorithm
                    _, algo_func = dropdown.options[dropdown.selected]
                    def draw_fn():
                        pygame.event.pump()
                        draw_state['count'] += 1
                        if draw_state['count'] % DRAW_THROTTLE == 0:
                            grid.draw()
                            ui_bar_h = btn_h + margin * 2
                            pygame.draw.rect(WIN, (240,240,240), (0, 0, WIDTH, ui_bar_h))
                            dropdown.draw(WIN)
                            run_btn.draw(WIN)
                            clear_btn.draw(WIN)
                            clear_all_btn.draw(WIN)
                            pygame.display.update()
                    algo_func(draw_fn, grid, start, end)
                    started = False

                if event.key == pygame.K_c:
                    print("Clearing the grid...")
                    start = None
                    end = None
                    grid.reset()
    pygame.quit()
