# Press P to pause
# During pause you can draw what you want
# In order to import patter , just paste it into pattern.txt where 'X' - is alive cell and '.' is dead cell
# Wrapped borders cause patterns to look slightly different than expected
import os

import arcade
import numpy as np

ROW_COUNT = 40
COLUMN_COUNT = 40
WIDTH = 15
HEIGHT = 15
MARGIN = 3
SCREEN_WIDTH = (WIDTH + MARGIN) * COLUMN_COUNT + MARGIN
SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN
SCREEN_TITLE = "Game of Life 250372"


class Logic:
    def __init__(self, file_name):
        try:  # Loading Pattern
            # This part clear columns and rows containing only dots
            with open(file_name, 'r') as pattern_file:
                pattern = pattern_file.read()
            lines = pattern.strip().split('\n')
            matrix = np.array([list(line) for line in lines])
            rows_to_delete = np.where(np.all(matrix == '.', axis=1))
            matrix = np.delete(matrix, rows_to_delete, axis=0)
            matrix = matrix.T
            rows_to_delete = np.where(np.all(matrix == '.', axis=1))
            matrix = np.delete(matrix, rows_to_delete, axis=0)
            matrix = matrix.T
            pattern_fixed = '\n'.join([''.join(row) for row in matrix])
            with open(file_name, 'w') as pattern_file:
                pattern_file.write(pattern_fixed)

            self.pattern = open(file_name)
            self.alive = np.array([[cell == "X" for cell in row.rstrip()] for row in self.pattern])
            self.grid = np.zeros((ROW_COUNT, COLUMN_COUNT))
            self.index = np.where(self.alive)
            self.grid[self.index[0], self.index[1]] = 1
        except FileNotFoundError:
            self.grid = np.random.choice([0, 1], size=(ROW_COUNT, COLUMN_COUNT), p=[0.5, 0.5])

    def update_grid(self):  # Main logic
        neighbors_count = np.zeros_like(self.grid)

        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbors_count += np.roll(self.grid, (i, j), axis=(0, 1))

        neighbors_count -= self.grid

        new_grid = np.where((self.grid == 1) & ((neighbors_count < 2) | (neighbors_count > 3)), 0, self.grid)
        new_grid = np.where((self.grid == 0) & (neighbors_count == 3), 1, new_grid)

        self.grid = new_grid


class Gui(arcade.Window):
    def __init__(self, width, height, title, logic):
        super().__init__(width, height, title)
        self.logic = logic
        self.background_color = arcade.color.BLUE
        self.grid_sprite_list = arcade.SpriteList()
        self.pause = True

        for row in range(ROW_COUNT):  # Here I generate the sprite list (white/green squares in-game)
            for column in range(COLUMN_COUNT):
                x = column * (WIDTH + MARGIN) + (WIDTH / 2 + MARGIN)
                y = row * (HEIGHT + MARGIN) + (HEIGHT / 2 + MARGIN)
                sprite = arcade.SpriteSolidColor(WIDTH, HEIGHT, arcade.color.WHITE)
                sprite.center_x = x
                sprite.center_y = y
                self.grid_sprite_list.append(sprite)

    def resync_grid_with_sprites(self):
        for row in range(ROW_COUNT):
            for column in range(COLUMN_COUNT):
                pos = row * COLUMN_COUNT + column
                if self.logic.grid[row][column] == 0:
                    self.grid_sprite_list[pos].color = arcade.color.WHITE
                else:
                    self.grid_sprite_list[pos].color = arcade.color.GREEN

    def on_draw(self):
        self.clear()
        self.grid_sprite_list.draw()

    def on_update(self, delta_time):
        if self.pause is True:
            self.logic.update_grid()
            self.resync_grid_with_sprites()

    def on_mouse_press(self, x, y, button, modifiers):
        column = int(x // (WIDTH + MARGIN))  # It allows us to get coordinates of place where user clicked
        row = int(y // (HEIGHT + MARGIN))

        if row < ROW_COUNT and column < COLUMN_COUNT:
            self.logic.grid[row][column] = 1 - self.logic.grid[row][
                column]  # This line allows us to omit unnecessary if statement
            self.resync_grid_with_sprites()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == ord('p'):
            self.pause = not self.pause


def main():
    directory = '.'
    files_names = [file for file in os.listdir(directory) if file.endswith('.txt')]
    print(files_names)
    file_name = input("Type name of pattern you want to use (if empty it will be random): ")

    logic = Logic(file_name)
    gui = Gui(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, logic)
    arcade.run()


if __name__ == "__main__":
    main()