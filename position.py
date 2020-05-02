class Position:
    row = None
    col = None

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def get_row(self):
        return self.row

    def get_col(self):
        return self.col

    def set_position(self, new_row, new_col):
        self.row = new_row
        self.col = new_col

