from utils import *
from collections import deque
from queue import PriorityQueue
import math
from grid import Grid
from spot import Spot


def bfs(draw: callable, grid: Grid, start: Spot, end: Spot) -> bool:
    if not start or not end:
        return False
    queue = deque([start])
    previous = {start: None}
    while queue:
        draw()
        current = queue.popleft()
        if current == end:
            while current in previous and previous[current]:
                current = previous[current]
                current.make_path(); draw()
            end.make_end(); start.make_start()
            return True
        for neighbor in current.neighbors:
            if neighbor not in previous:
                previous[neighbor] = current
                queue.append(neighbor)
                neighbor.make_open()
        if current != start:
            current.make_closed()
    return False


def dfs(draw: callable, grid: Grid, start: Spot, end: Spot) -> bool:
    if not start or not end:
        return False
    stack = [start]
    previous = {start: None}
    while stack:
        draw()
        current = stack.pop()
        if current == end:
            while current in previous and previous[current]:
                current = previous[current]
                current.make_path(); draw()
            end.make_end(); start.make_start()
            return True
        for neighbor in current.neighbors:
            if neighbor not in previous:
                previous[neighbor] = current
                stack.append(neighbor)
                neighbor.make_open()
        if current != start:
            current.make_closed()
    return False


def dls(draw: callable, grid: Grid, start: Spot, end: Spot, limit: int | None = None) -> bool:
    """
    Depth-Limited Search (iterative, depth-aware revisits).
    If `limit` is None, we use a safe upper bound = rows * cols (covers any simple path).
    """
    if not start or not end:
        return False

    if limit is None:
        rows = len(grid.grid)
        cols = len(grid.grid[0]) if rows else 0
        limit = rows * cols  # big enough to not stop before reaching goal

    stack = [(start, 0)]
    previous = {start: None}
    seen_depth: dict[Spot, int] = {start: 0}

    while stack:
        draw()
        current, depth = stack.pop()

        if current == end:
            while current in previous and previous[current]:
                current = previous[current]
                current.make_path(); draw()
            end.make_end(); start.make_start()
            return True

        if depth == limit:
            continue

        for nb in current.neighbors:
            nd = depth + 1
            # allow (re)visit if we found a shallower depth within the limit
            if nd <= limit and (nb not in seen_depth or nd < seen_depth[nb]):
                seen_depth[nb] = nd
                previous[nb] = current
                stack.append((nb, nd))
                nb.make_open()

        if current != start:
            current.make_closed()

    return False


def h_manhattan_distance(p1, p2) -> float:
    if isinstance(p1, Spot):
        p1 = p1.get_position()
    if isinstance(p2, Spot):
        p2 = p2.get_position()
    x1, y1 = p1
    x2, y2 = p2
    return float(abs(x1 - x2) + abs(y1 - y2))


def h_euclidian_distance(p1, p2) -> float:
    if isinstance(p1, Spot):
        p1 = p1.get_position()
    if isinstance(p2, Spot):
        p2 = p2.get_position()
    x1, y1 = p1
    x2, y2 = p2
    return float(math.hypot(x1 - x2, y1 - y2))


def astar(draw: callable, grid: Grid, start: Spot, end: Spot) -> bool:
    if not start or not end:
        return False

    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    previous = {start: None}
    g_score: dict[Spot, float] = {start: 0.0}
    closed: set[Spot] = set()

    while not open_set.empty():
        draw()
        _, _, current = open_set.get()
        if current in closed:
            continue

        if current == end:
            while current in previous and previous[current]:
                current = previous[current]
                current.make_path(); draw()
            end.make_end(); start.make_start()
            return True

        closed.add(current)

        for neighbor in current.neighbors:
            tentative = g_score[current] + 1  # unit edge cost
            if tentative < g_score.get(neighbor, float('inf')):
                previous[neighbor] = current
                g_score[neighbor] = tentative
                f = tentative + h_manhattan_distance(neighbor, end)
                count += 1
                open_set.put((f, count, neighbor))  # always push on improvement
                neighbor.make_open()

        if current != start:
            current.make_closed()

    return False


def ucs(draw: callable, grid: Grid, start: Spot, end: Spot) -> bool:
    """
    Dijkstra/UCS with decrease-key via reinsert and stale-pop skipping.
    """
    if not start or not end:
        return False

    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    previous = {start: None}
    g_score: dict[Spot, float] = {start: 0.0}
    closed: set[Spot] = set()

    while not open_set.empty():
        draw()
        _, _, current = open_set.get()
        if current in closed:
            continue

        if current == end:
            while current in previous and previous[current]:
                current = previous[current]
                current.make_path(); draw()
            end.make_end(); start.make_start()
            return True

        closed.add(current)

        for neighbor in current.neighbors:
            tentative = g_score[current] + 1
            if tentative < g_score.get(neighbor, float('inf')):
                previous[neighbor] = current
                g_score[neighbor] = tentative
                count += 1
                open_set.put((g_score[neighbor], count, neighbor))  # priority = g
                neighbor.make_open()

        if current != start:
            current.make_closed()

    return False


def greedy_search(draw: callable, grid: Grid, start: Spot, end: Spot) -> bool:
    if not start or not end:
        return False

    count = 0
    open_set = PriorityQueue()
    open_set.put((h_manhattan_distance(start, end), count, start))
    previous = {start: None}
    visited = set()

    while not open_set.empty():
        draw()
        _, _, current = open_set.get()
        if current in visited:
            continue
        visited.add(current)

        if current == end:
            while current in previous and previous[current]:
                current = previous[current]
                current.make_path(); draw()
            end.make_end(); start.make_start()
            return True

        for neighbor in current.neighbors:
            if neighbor not in previous:
                previous[neighbor] = current
                count += 1
                open_set.put((h_manhattan_distance(neighbor, end), count, neighbor))
                neighbor.make_open()

        if current != start:
            current.make_closed()

    return False


def ids(draw: callable, grid: Grid, start: Spot, end: Spot, max_depth: int | None = None) -> bool:
    """
    Iterative Deepening DFS using the fixed DLS.
    If max_depth is None, use rows*cols as a safe bound.
    """
    if max_depth is None:
        rows = len(grid.grid)
        cols = len(grid.grid[0]) if rows else 0
        max_depth = 2*(rows + cols)

    for depth in range(max_depth + 1):
        # clear visualization (keep barriers/start/end)
        for row in grid.grid:
            for spot in row:
                if spot != start and spot != end and not spot.is_barrier():
                    spot.reset()
        if dls(draw, grid, start, end, limit=depth):
            return True
    return False


def ida_star(draw: callable, grid: Grid, start: Spot, end: Spot) -> bool:
    def search(path: list[Spot], g: float, threshold: float) -> tuple[bool, float]:
        current = path[-1]
        draw()
        f = g + h_manhattan_distance(current, end)
        if f > threshold:
            return False, f
        if current == end:
            for s in path[1:-1]:
                s.make_path(); draw()
            return True, f

        min_threshold = float('inf')
        current.make_closed()

        for neighbor in current.neighbors:
            if neighbor in path:
                continue
            path.append(neighbor)
            neighbor.make_open()
            found, new_thr = search(path, g + 1, threshold)
            if found:
                return True, new_thr
            if new_thr < min_threshold:
                min_threshold = new_thr
            path.pop()
            if neighbor != end:
                neighbor.reset()
        return False, min_threshold

    if not start or not end:
        return False

    threshold = h_manhattan_distance(start, end)
    path = [start]

    while True:
        # reset visuals (keep barriers/start/end)
        for row in grid.grid:
            for s in row:
                if s != start and s != end and not s.is_barrier():
                    s.reset()

        found, threshold = search(path, 0, threshold)
        if found:
            end.make_end(); start.make_start()
            return True
        if threshold == float('inf'):
            return False
        # continue with raised threshold
