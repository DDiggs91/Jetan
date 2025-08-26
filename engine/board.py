from engine.pieces import Piece, Square, Move, JetanPiece, Color, validate_move, destinations

INITIAL_BOARD_SETUP = [
    Piece(JetanPiece.Warrior, Color.ORANGE, Square(9, 0)),
    Piece(JetanPiece.Padwar, Color.ORANGE, Square(9, 1)),
    Piece(JetanPiece.Dwar, Color.ORANGE, Square(9, 2)),
    Piece(JetanPiece.Flier, Color.ORANGE, Square(9, 3)),
    Piece(JetanPiece.Princess, Color.ORANGE, Square(9, 4)),
    Piece(JetanPiece.Chief, Color.ORANGE, Square(9, 5)),
    Piece(JetanPiece.Flier, Color.ORANGE, Square(9, 6)),
    Piece(JetanPiece.Dwar, Color.ORANGE, Square(9, 7)),
    Piece(JetanPiece.Padwar, Color.ORANGE, Square(9, 8)),
    Piece(JetanPiece.Warrior, Color.ORANGE, Square(9, 9)),
    Piece(JetanPiece.Thoat, Color.ORANGE, Square(8, 0)),
    Piece(JetanPiece.Panthan, Color.ORANGE, Square(8, 1)),
    Piece(JetanPiece.Panthan, Color.ORANGE, Square(8, 2)),
    Piece(JetanPiece.Panthan, Color.ORANGE, Square(8, 3)),
    Piece(JetanPiece.Panthan, Color.ORANGE, Square(8, 4)),
    Piece(JetanPiece.Panthan, Color.ORANGE, Square(8, 5)),
    Piece(JetanPiece.Panthan, Color.ORANGE, Square(8, 6)),
    Piece(JetanPiece.Panthan, Color.ORANGE, Square(8, 7)),
    Piece(JetanPiece.Panthan, Color.ORANGE, Square(8, 8)),
    Piece(JetanPiece.Thoat, Color.BLACK, Square(8, 9)),
    Piece(JetanPiece.Warrior, Color.BLACK, Square(0, 0)),
    Piece(JetanPiece.Padwar, Color.BLACK, Square(0, 1)),
    Piece(JetanPiece.Dwar, Color.BLACK, Square(0, 2)),
    Piece(JetanPiece.Flier, Color.BLACK, Square(0, 3)),
    Piece(JetanPiece.Princess, Color.BLACK, Square(0, 4)),
    Piece(JetanPiece.Chief, Color.BLACK, Square(0, 5)),
    Piece(JetanPiece.Flier, Color.BLACK, Square(0, 6)),
    Piece(JetanPiece.Dwar, Color.BLACK, Square(0, 7)),
    Piece(JetanPiece.Padwar, Color.BLACK, Square(0, 8)),
    Piece(JetanPiece.Warrior, Color.BLACK, Square(0, 9)),
    Piece(JetanPiece.Thoat, Color.BLACK, Square(1, 0)),
    Piece(JetanPiece.Panthan, Color.BLACK, Square(1, 1)),
    Piece(JetanPiece.Panthan, Color.BLACK, Square(1, 2)),
    Piece(JetanPiece.Panthan, Color.BLACK, Square(1, 3)),
    Piece(JetanPiece.Panthan, Color.BLACK, Square(1, 4)),
    Piece(JetanPiece.Panthan, Color.BLACK, Square(1, 5)),
    Piece(JetanPiece.Panthan, Color.BLACK, Square(1, 6)),
    Piece(JetanPiece.Panthan, Color.BLACK, Square(1, 7)),
    Piece(JetanPiece.Panthan, Color.BLACK, Square(1, 8)),
    Piece(JetanPiece.Thoat, Color.BLACK, Square(1, 9)),
]


class Board:
    def __init__(self, board_state: list[Piece] | None = None) -> None:
        self.current_board: list[Piece] = []
        if not board_state:
            board_state = INITIAL_BOARD_SETUP
        for piece in board_state:
            self.current_board.append(piece)

    def from_actions(self, moves: list[Move]) -> "Board":
        board = Board()
        for move in moves:
            self.apply_move(move)
        return board

    def piece_at(self, square: Square) -> Piece | None:
        return next((piece for piece in self.current_board if piece.square == square), None)

    def apply_move(self, move: Move) -> list[Piece]:
        if not validate_move(move, self):
            raise ValueError(f"This move is illegal. {move.piece.square} to {move.final_square}")
        if move.piece == JetanPiece.Princess:
            if move.final_square in self.threatened_squares(move.piece.color):
                raise ValueError("The princess may not enter a threatened square.")
        if captured_piece := self.piece_at(move.final_square):
            del self.current_board[self.current_board.index(captured_piece)]
        piece_index = self.current_board.index(move.piece)
        self.current_board[piece_index].square = move.final_square
        return self.current_board

    def threatened_squares(self, color: Color) -> list[Square]:
        result = set()
        for piece in self.current_board:
            if piece.color != color and piece.type != JetanPiece.Princess:
                for square in destinations(piece, self):
                    result.add(square)
        return list(result)
