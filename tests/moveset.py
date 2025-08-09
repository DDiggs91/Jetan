from typing import Iterable

from backend.classes import Board, Piece, Princess, Square, JetanPiece, Color
from backend.capabilities import CAPABILITIES_BY_TYPE


def generate_legal_moves(board: Board, piece: Piece) -> Iterable[list[Square]]:
    for capability in CAPABILITIES_BY_TYPE[(piece.type, piece.color)]:
        yield from capability.moves(piece, board)


empty_board = Board()
test_piece = Piece(JetanPiece.Panthan, Color.BLACK, Square(5, 5))
result = list(generate_legal_moves(empty_board, test_piece))
assert len(result) == 5
test_piece = Piece(JetanPiece.Panthan, Color.BLACK, Square(5, 9))
result = list(generate_legal_moves(empty_board, test_piece))
assert len(result) == 2
test_piece = Piece(JetanPiece.Panthan, Color.BLACK, Square(9, 9))
result = list(generate_legal_moves(empty_board, test_piece))
assert len(result) == 1
test_piece = Piece(JetanPiece.Chief, Color.BLACK, Square(5, 5))
result = list(generate_legal_moves(empty_board, test_piece))
assert len(result) == 368
test_piece = Piece(JetanPiece.Warrior, Color.BLACK, Square(5, 5))
result = list(generate_legal_moves(empty_board, test_piece))
assert len(result) == 12
test_piece = Piece(JetanPiece.Padwar, Color.BLACK, Square(5, 5))
result = list(generate_legal_moves(empty_board, test_piece))
assert len(result) == 12
test_piece = Piece(JetanPiece.Dwar, Color.BLACK, Square(5, 5))
result = list(generate_legal_moves(empty_board, test_piece))
assert len(result) == 36
test_piece = Piece(JetanPiece.Flier, Color.BLACK, Square(5, 5))
result = list(generate_legal_moves(empty_board, test_piece))
assert len(result) == 36
test_piece = Piece(JetanPiece.Flier, Color.BLACK, Square(0, 0))
result = list(generate_legal_moves(empty_board, test_piece))
assert len(result) == 5
test_piece = Piece(JetanPiece.Thoat, Color.BLACK, Square(5, 5))
result = list(generate_legal_moves(empty_board, test_piece))
assert len(result) == 16
test_piece = Piece(JetanPiece.Thoat, Color.BLACK, Square(0, 0))
result = list(generate_legal_moves(empty_board, test_piece))
assert len(result) == 4
test_piece = Princess(JetanPiece.Princess, Color.BLACK, Square(5, 5))
result = list(generate_legal_moves(empty_board, test_piece))
assert len(result) == 467
