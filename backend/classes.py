from enum import Enum, auto
from dataclasses import dataclass


@dataclass(frozen=True)
class Square:
    row: int
    col: int

    def __post_init__(self):
        if not (0 <= self.row <= 9 and 0 <= self.col <= 9):
            raise ValueError(f"The board is a 10x10 board. {self.row}, {self.col} is not valid.")

    def __add__(self, delta: tuple[int, int]) -> "Square":
        dr, dc = delta
        return Square(self.row + dr, self.col + dc)


class JetanPiece(Enum):
    Panthan = "p"
    Chief = "C"
    Princess = "Q"
    Padwar = "P"
    Warrior = "W"
    Thoat = "T"
    Dwar = "D"
    Flier = "F"


class Color(Enum):
    ORANGE = auto()
    BLACK = auto()


@dataclass
class Piece:
    type: JetanPiece
    color: Color
    square: Square


class Princess(Piece):
    has_escape: bool = True


class Board:
    def piece_at(self, square: Square) -> Piece | None:
        return None
