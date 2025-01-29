import numpy as np
import hashlib


class RandomArt:
    field = None  # initialised to (xdim, ydim) numpy array of zeros
    input_string = None
    input_bytes = None
    start = None
    end = None

    symbols = [
        " ",
        ".",
        "o",
        "+",
        "=",
        "*",
        "B",
        "0",
        "X",
        "@",
        "%",
        "&",
        "#",
        "/",
        "^",
    ]
    start_symbol = "S"
    end_symbol = "E"

    xdim = 17
    ydim = 9

    def __init__(self, title: str = None, xdim: int = 17, ydim: int = 9):
        self.xdim = xdim
        self.ydim = ydim
        self.start = (self.xdim // 2, self.ydim // 2)
        self.title = title

        self.clear_board()

    def clear_board(self):
        self.field = np.zeros((self.xdim, self.ydim), dtype=int)

    def resize(self, xdim: int, ydim: int):
        self.xdim = xdim
        self.ydim = ydim
        self.clear_board()

    def __str__(self):
        if self.title is None:
            output = "+" + "-" * self.xdim + "+\n"
        else:
            if len(self.title) > self.xdim - 2:
                title_str = "[" + self.title[: self.xdim - 5] + "...]"
            else:
                title_str = "[" + self.title + "]"
            output = "+" + title_str.center(self.xdim, "-") + "+\n"

        for y in range(self.ydim):
            output += "|"
            for x in range(self.xdim):
                if x == self.start[0] and y == self.start[1]:
                    output += self.start_symbol
                elif x == self.end[0] and y == self.end[1]:
                    output += self.end_symbol
                else:
                    # Note modulo to wrap symbols around for very long walks
                    output += self.symbols[self.field[x, y] % len(self.symbols)]
            output += "|\n"

        output += "+" + "-" * (self.xdim) + "+"
        return output

    def make_art(
        self, input_string: str, do_md5: bool = True, is_hex: bool = False
    ) -> str:
        self.input_string = input_string
        if is_hex:
            self.input_bytes = bytes.fromhex(self.input_string)
        elif do_md5:
            md5 = hashlib.md5()
            md5.update(self.input_string.encode("utf-8"))
            self.input_bytes = md5.digest()
        else:
            self.input_bytes = self.input_string.encode("utf-8")

        bishop = list(self.start)  # copy the start position
        # Don't need to increment start as it will always be "S"

        for byte in self.input_bytes:
            # Extract the pairs of bits from the byte into an array.
            # Least significant first
            w = byte
            bit_pairs = []
            for _ in range(4):
                b1 = int(w & 1 != 0)
                w = w >> 1
                b2 = int(w & 1 != 0)
                w = w >> 1
                bit_pairs.append((b2, b1))

            for bit_pair in bit_pairs:
                dy = bit_pair[0] * 2 - 1
                dx = bit_pair[1] * 2 - 1

                # Move the bishop, sliding along walls as necessary
                bishop[0] = max(min(bishop[0] + dx, self.xdim - 1), 0)
                bishop[1] = max(min(bishop[1] + dy, self.ydim - 1), 0)

                # Drop a coin on the current square
                self.field[bishop[0], bishop[1]] += 1

        # We are done. Mark the end point
        self.end = bishop

        return str(self)


# Standalone function to generate random art
def generate_random_art(
    title: str, input_string: str, do_md5: bool = True, is_hex: bool = False
) -> str:
    random_art = RandomArt(title=title)
    return random_art.make_art(input_string, do_md5=do_md5, is_hex=is_hex)
