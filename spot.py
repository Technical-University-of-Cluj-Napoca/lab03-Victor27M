from utils import *

class Spot:
    # --- Constructor ---
    def __init__(self, row: int, col: int, width: int, height: int, total_rows: int):
        """
        Initialize a spot in the grid.
        Args: 
            row (int): The row index of the spot.
            col (int): The column index of the spot.
            width (int): The width of the spot.
            height (int): The height of the spot.
            total_rows (int): Keeps track of the total number of rows in the grid (while avoiding global variables).
        """
        # a square has a position in the grid (row, col) and a position in the window (x, y)
        self.row: int = row
        self.col: int = col
        # a square has also a width and a height
        # the coordinates (x, y) are calculated based on the place inside the grid and its size.
        self.width: int = width
        self.height: int = height
        self.x: int = row * width
        self.y: int = col * height
        self.color: tuple = (120, 120, 120)  # default background grey
        self.neighbors: list = []
        self.total_rows: int = total_rows

    # ---- Methods to change the state of the spot (i.e., its setters) ----
    def get_position(self) -> tuple[int, int]:
        """
        Gets the (row, col) position of the spot in the grid.
        Returns:
            tuple[int, int]: A tuple containing the row and column indices of the spot in the grid.
        """
        return self.row, self.col

    def is_closed(self) -> bool:
        """
        Checks if the spot is marked as closed (blue).
        Returns:
            bool: True if the spot is closed (blue), False otherwise.
        """
        return self.color == (0, 102, 204)

    def is_open(self) -> bool:
        """
        Checks if the spot is marked as open (cyan).
        Returns:
            bool: True if the spot is marked as open (cyan), False otherwise.
        """
        return self.color == (0, 255, 255)

    def is_barrier(self) -> bool:
        """
        Checks if the spot is marked as a barrier (dark grey).
        Returns:
            bool: True if the spot is a barrier (dark grey), False otherwise.
        """
        return self.color == (50, 50, 50)

    def is_start(self) -> bool:
        """
        Checks if the spot is marked as the start node (orange).
        Returns:
            bool: True if the spot is the start node (orange), False otherwise.
        """
        return self.color == (255, 165, 0)

    def is_end(self) -> bool:
        """
        Checks if the spot is marked as the end node (red).
        Returns:
            bool: True if the spot is the end node (red), False otherwise.
        """
        return self.color == (255, 0, 0)

    # ---- Methods to change the state of the spot (i.e., its setters) ----
    def reset(self) -> None:
        """
        Change the color of the spot back to grey (unvisited).
        Returns:
            None
        """
        self.color = (120, 120, 120)

    def make_closed(self) -> None:
        """
        Mark the spot as closed (blue).
        Returns:
            None
        """
        self.color = (0, 102, 204)

    def make_open(self) -> None:
        """
        Mark the spot as open (cyan).
        Returns:
            None
        """
        self.color = (0, 255, 255)

    def make_barrier(self) -> None:
        """
        Mark the spot as a barrier (dark grey).
        Returns:
            None
        """
        self.color = (50, 50, 50)

    def make_start(self) -> None:
        """
        Mark the spot as the start node (orange).
        Returns:
            None
        """
        self.color = (255, 165, 0)

    def make_end(self) -> None:
        """
        Mark the spot as the end node (red).
        Returns:
            None
        """
        self.color = (255, 0, 0)

    def make_path(self) -> None:
        """
        Mark the spot as part of the path (yellow).
        Returns:
            None
        """
        self.color = (255, 255, 0)

    # --- Operators ---
    def __lt__(self, other: "Spot") -> bool:
        """
        Less-than operator for comparing two spots. The other spot is always "greater" than this one.
        This is used to avoid errors in data structures that require comparison, like PriorityQueue.
        """
        return False
    
    # --- Other Methods ---
    def draw(self, win: pygame.Surface) -> None:
        """
        Draw the spot on the given Pygame surface (window).
        Args:
            win (pygame.Surface): The Pygame surface (window) where the spot will be drawn.
        """
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid: list[list["Spot"]]) -> None:
        """
        Update the list of neighbor spots that are not barriers.
        Args:
            grid (list[list[Spot]]): The 2D list (matrix) representing the grid of Spot objects.
        Returns:
            None
        """
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])
