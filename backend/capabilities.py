from abc import ABC, abstractmethod
from typing import Iterable

from backend.classes import Piece, Princess, Board, Square, Color, JetanPiece
from backend.constants import ORTHO_MOVES, DIAGONAL_MOVES


class Capability(ABC):
    @abstractmethod
    def moves(self, piece: Piece, board: Board) -> Iterable[list[Square]]: ...
    def destinations(self, piece: Piece, board: Board) -> Iterable[Square]:
        yield from {move[-1] for move in self.moves(piece, board)}


class Stepper(Capability):
    def __init__(self, directions: list[tuple[int, int]], max_steps: int) -> None:
        self.directions = directions
        self.max_steps = max_steps

    def moves(self, piece: Piece, board: Board) -> Iterable[list[Square]]:
        path = [piece.square]
        yield from self._dfs_paths(piece, board, path, self.max_steps)

    def _dfs_paths(self, piece: Piece, board: Board, path: list[Square], steps_left: int):
        if steps_left == 0:
            if len(path) == self.max_steps + 1:
                yield list(path)
            return
        current_square = path[-1]
        for direction in self.directions:
            try:
                next_square = current_square + direction
                if next_square in path:
                    continue
            except ValueError:
                continue
            blocker = board.piece_at(next_square)
            if blocker is None:
                path.append(next_square)
                yield from self._dfs_paths(piece, board, path, steps_left - 1)
                path.pop()
            else:
                if blocker.color != piece.color and steps_left == 1:
                    yield path + [next_square]


class Jumper(Capability):
    def __init__(self, directions: list[tuple[int, int]], max_steps: int) -> None:
        self.directions = directions
        self.max_steps = max_steps

    def moves(self, piece: Piece, board: Board) -> Iterable[list[Square]]:
        path = [piece.square]
        yield from self._dfs_paths(piece, board, path, self.max_steps)

    def _dfs_paths(self, piece: Piece, board: Board, path: list[Square], steps_left: int):
        if steps_left == 0:
            if len(path) == self.max_steps + 1:
                yield list(path)
            return
        current_square = path[-1]
        for direction in self.directions:
            try:
                next_square = current_square + direction
                if next_square in path:
                    continue
            except ValueError:
                continue
            if steps_left == 1:
                blocker = board.piece_at(next_square)
                if blocker:
                    if blocker.color != piece.color:
                        yield path + [next_square]
                else:
                    yield path + [next_square]
            else:
                path.append(next_square)
                yield from self._dfs_paths(piece, board, path, steps_left - 1)
                path.pop()


class ThoatMovement(Capability):
    def moves(self, piece: Piece, board: Board) -> Iterable[list[Square]]:
        paths = []
        for step1 in ORTHO_MOVES:
            path: list[Square] = [piece.square]
            try:
                intermediate_step = path[-1] + step1
                path.append(intermediate_step)
            except ValueError:
                continue
            for step2 in DIAGONAL_MOVES:
                second_path = path.copy()
                try:
                    final_step = second_path[-1] + step2
                    blocker = board.piece_at(final_step)
                    if blocker:
                        if blocker.color == piece.color:
                            continue
                    second_path.append(final_step)
                    paths.append(second_path)
                except ValueError:
                    continue
        yield from paths


class JumperNoCapture(Capability):
    def __init__(self, directions: list[tuple[int, int]], max_steps: int) -> None:
        self.directions = directions
        self.max_steps = max_steps

    def moves(self, piece: Piece, board: Board) -> Iterable[list[Square]]:
        path = [piece.square]
        yield from self._dfs_paths(piece, board, path, self.max_steps)

    def _dfs_paths(self, piece: Piece, board: Board, path: list[Square], steps_left: int):
        if steps_left == 0:
            if len(path) == self.max_steps + 1:
                yield list(path)
            return
        current_square = path[-1]
        for direction in self.directions:
            try:
                next_square = current_square + direction
                if next_square in path:
                    continue
            except ValueError:
                continue
            if steps_left == 1:
                blocker = board.piece_at(next_square)
                if blocker is None:
                    yield path + [next_square]
            else:
                path.append(next_square)
                yield from self._dfs_paths(piece, board, path, steps_left - 1)
                path.pop()


class PrincessEscape(Capability):

    def moves(self, piece: Princess, board: Board) -> Iterable[list[Square]]:
        if not piece.has_escape:
            return
        else:
            moves = []
            for row in range(10):
                for col in range(10):
                    square = Square(row, col)
                    if board.piece_at(square) is None and square != piece.square:
                        yield [piece.square, square]


CAPABILITIES_BY_TYPE = {
    (JetanPiece.Panthan, Color.BLACK): [Stepper([(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0)], 1)],
    (JetanPiece.Panthan, Color.ORANGE): [Stepper([(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)], 1)],
    (JetanPiece.Chief, Color.BLACK): [Stepper(ORTHO_MOVES + DIAGONAL_MOVES, 3)],
    (JetanPiece.Chief, Color.ORANGE): [Stepper(ORTHO_MOVES + DIAGONAL_MOVES, 3)],
    (JetanPiece.Warrior, Color.BLACK): [Stepper(ORTHO_MOVES, 2)],
    (JetanPiece.Warrior, Color.ORANGE): [Stepper(ORTHO_MOVES, 2)],
    (JetanPiece.Padwar, Color.BLACK): [Stepper(DIAGONAL_MOVES, 2)],
    (JetanPiece.Padwar, Color.ORANGE): [Stepper(DIAGONAL_MOVES, 2)],
    (JetanPiece.Dwar, Color.BLACK): [Stepper(ORTHO_MOVES, 3)],
    (JetanPiece.Dwar, Color.ORANGE): [Stepper(ORTHO_MOVES, 3)],
    (JetanPiece.Flier, Color.BLACK): [Jumper(DIAGONAL_MOVES, 3)],
    (JetanPiece.Flier, Color.ORANGE): [Jumper(DIAGONAL_MOVES, 3)],
    (JetanPiece.Thoat, Color.ORANGE): [ThoatMovement()],
    (JetanPiece.Thoat, Color.BLACK): [ThoatMovement()],
    (JetanPiece.Princess, Color.ORANGE): [JumperNoCapture(ORTHO_MOVES + DIAGONAL_MOVES, 3), PrincessEscape()],
    (JetanPiece.Princess, Color.BLACK): [JumperNoCapture(ORTHO_MOVES + DIAGONAL_MOVES, 3), PrincessEscape()],
}
