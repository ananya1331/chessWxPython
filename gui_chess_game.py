import pygame
import chess
import chess.engine
import pickle
import time

# Constants
WIDTH, HEIGHT = 800, 800  # Full screen size
SQ_SIZE = WIDTH // 8
FPS = 60

# Colors
WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
GREEN = (106, 135, 89)

# Init
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess vs AI")
FONT = pygame.font.SysFont("arial", 24)

# Load Images
PIECES = {}
def load_images():
    piece_map = {
        'r': 'black_rook.png',
        'n': 'black_knight.png',
        'b': 'black_bishop.png',
        'q': 'black_queen.png',
        'k': 'black_king.png',
        'p': 'black_pawn.png',
        'R': 'white_rook.png',
        'N': 'white_knight.png',
        'B': 'white_bishop.png',
        'Q': 'white_queen.png',
        'K': 'white_king.png',
        'P': 'white_pawn.png',
    }

    for symbol, filename in piece_map.items():
        PIECES[symbol] = pygame.transform.scale(
            pygame.image.load(f"img/{filename}"),
            (SQ_SIZE, SQ_SIZE)
        )

def draw_board(board, player_color):
    for row in range(8):
        for col in range(8):
            display_row = row if player_color == chess.WHITE else 7 - row
            display_col = col if player_color == chess.WHITE else 7 - col
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(WIN, color, pygame.Rect(display_col * SQ_SIZE, display_row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = chess.square_rank(square)
            col = chess.square_file(square)
            display_row = 7 - row if player_color == chess.WHITE else row
            display_col = col if player_color == chess.WHITE else 7 - col
            WIN.blit(PIECES[piece.symbol()], pygame.Rect(display_col * SQ_SIZE, display_row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    pygame.display.update()

def show_message(text):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    WIN.blit(overlay, (0, 0))

    font_big = pygame.font.SysFont("arial", 48, True)
    message = font_big.render(text, True, (255, 255, 255))
    WIN.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - message.get_height() // 2))
    pygame.display.update()
    pygame.time.wait(3000)

def get_square_under_mouse():
    x, y = pygame.mouse.get_pos()
    row = y // SQ_SIZE
    col = x // SQ_SIZE
    return chess.square(col, 7 - row)

def evaluate_board(board):
    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3.3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    eval = 0
    for piece_type in values:
        eval += len(board.pieces(piece_type, chess.WHITE)) * values[piece_type]
        eval -= len(board.pieces(piece_type, chess.BLACK)) * values[piece_type]

    eval += 0.1 * len(list(board.legal_moves)) if board.turn == chess.WHITE else -0.1 * len(list(board.legal_moves))
    return eval

def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    if maximizing:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

def save_game(board):
    with open("saved_chess_game.pkl", "wb") as f:
        pickle.dump(board.fen(), f)
    print("Game saved!")

def load_game():
    try:
        with open("saved_chess_game.pkl", "rb") as f:
            fen = pickle.load(f)
            board = chess.Board(fen)
            print("Game loaded!")
            return board
    except:
        print("No saved game found.")
        return chess.Board()

def choose_side():
    choosing = True
    while choosing:
        WIN.fill((0, 0, 0))
        text1 = FONT.render("Press W to play as White", True, (255, 255, 255))
        text2 = FONT.render("Press B to play as Black", True, (255, 255, 255))
        WIN.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - 40))
        WIN.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2 + 10))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    return chess.WHITE
                elif event.key == pygame.K_b:
                    return chess.BLACK

def main():
    clock = pygame.time.Clock()
    board = chess.Board()
    selected_square = None
    player_color = choose_side()
    ai_color = not player_color

    load_images()

    if board.turn == ai_color:
        _, ai_move = minimax(board, 3, float('-inf'), float('inf'), ai_color == chess.WHITE)
        if ai_move:
            board.push(ai_move)

    while True:
        draw_board(board, player_color)
        clock.tick(FPS)

        if board.is_checkmate():
            if board.turn == player_color:
                show_message("Checkmate! Computer wins.")
            else:
                show_message("Checkmate! You win.")
            break

        elif board.is_stalemate():
            show_message("Stalemate... Draw.")
            break

        elif board.is_check():
            show_message("Check!")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_game(board)
                elif event.key == pygame.K_l:
                    board = load_game()
                    selected_square = None

            if event.type == pygame.MOUSEBUTTONDOWN and board.turn == player_color:
                square = get_square_under_mouse()
                if selected_square is None:
                    if board.piece_at(square) and board.piece_at(square).color == player_color:
                        selected_square = square
                else:
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        board.push(move)
                        selected_square = None
                    else:
                        selected_square = None

        if not board.is_game_over() and board.turn == ai_color:
            time.sleep(0.7)
            _, ai_move = minimax(board, 3, float('-inf'), float('inf'), ai_color == chess.WHITE)
            if ai_move:
                board.push(ai_move)

if __name__ == "__main__":
    main()
