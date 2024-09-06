"""
This is our main driver file.
It will be responsible for handling user input and displaying the current GameState object.
"""

import pygame as p
import chessModule
import AI
from AI import SearchMove
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512  # 400 is another option
MOVE_LOG_PANEL_WIDTH = 260
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # dimensions of a chess board are 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15  # for animations later on
IMAGES = {}

"""
Initialize a global dictionary of image. This will be called exactly once in the main
"""


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('Main/images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))
    # Note: we can access an image by saying 'IMAGES['wp']'

def displayPlayModeSelection(screen):
    screen.fill(p.Color('black'))
    font = p.font.SysFont('Arial', 24)
    text = font.render("Select Play Mode", True, p.Color('White'))
    text_rect = text.get_rect(center=((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH) // 2, BOARD_HEIGHT // 2 - 100))
    screen.blit(text, text_rect)
    
    pvp_button = p.Rect(286, 200, 200, 50)
    pvc_button = p.Rect(276, 300, 220, 50)
    quit_button = p.Rect(296, 400, 180, 50)
    
    p.draw.rect(screen, p.Color('gray'), pvp_button)
    p.draw.rect(screen, p.Color('gray'), pvc_button)
    p.draw.rect(screen, p.Color('gray'), quit_button)
    
    pvp_text = font.render("Player vs Player", True, p.Color('black'))
    pvc_text = font.render("Player vs Computer", True, p.Color('black'))
    quit_text = font.render("Quit", True, p.Color('black'))
    
    screen.blit(pvp_text, (pvp_button.x + 25, pvp_button.y + 10))
    screen.blit(pvc_text, (pvc_button.x + 25, pvc_button.y + 10))
    screen.blit(quit_text, (quit_button.x + 70, quit_button.y + 10))
    
    return pvp_button, pvc_button, quit_button

def displaySideSelection(screen):
    screen.fill(p.Color('black'))
    font = p.font.SysFont('Arial', 24)
    text = font.render("Select Your Side", True, p.Color('White'))
    text_rect = text.get_rect(center=((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH) // 2, BOARD_HEIGHT // 2 - 100))
    screen.blit(text, text_rect)

    WHITE_BUTTON = p.Rect(296, 200, 180, 50)
    BLACK_BUTTON = p.Rect(296, 300, 180, 50)

    p.draw.rect(screen, p.Color('gray'), WHITE_BUTTON)
    p.draw.rect(screen, p.Color('gray'), BLACK_BUTTON)
    
    white_text = font.render("White", True, p.Color('black'))
    black_text = font.render("Black", True, p.Color('black'))
    
    screen.blit(white_text, (WHITE_BUTTON.x + 60, WHITE_BUTTON.y + 10))
    screen.blit(black_text, (BLACK_BUTTON.x + 60, BLACK_BUTTON.y + 10))
    
    return WHITE_BUTTON, BLACK_BUTTON


"""
The main driver for our code. This will handle user input and updating the graphics
"""


def main():
    p.init()
    p.display.set_caption("Chess")
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    moveLogFont = p.font.SysFont('Arial', 14, True, False)
    gs = chessModule.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    animate = False  # flag variable for when we should animate a move
    loadImages()  # only do this once, before the while loop
    running = True
    sqSelected = ()  # no square is selected, keep track of the last click of the user (tuple: (row, col))
    playerClicks = []  # keep track of player clicks (two tuples: [(6, 4), (4, 4)]
    gameOver = False
    playerOne = True#bool(random.randint(0, 1))  #if a human is playing white, then this will be True. If an AI is playing then it will be False
    playerTwo = False#not(playerOne)   #same as above but for black
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    play_mode_selected = True
    side_selected = False
    is_white = True
    p.mouse.set_cursor(*p.cursors.tri_right)
    
    while play_mode_selected:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
                play_mode_selected = False
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if pvp_button.collidepoint(mouse_pos):
                    playerOne = True
                    playerTwo = True
                    play_mode_selected = False
                elif pvc_button.collidepoint(mouse_pos):
    
                    side_selected = True
                    while side_selected:
                        for event in p.event.get():
                            if event.type == p.QUIT:
                                running = False
                                side_selected = False
                                play_mode_selected = False
                            elif event.type == p.MOUSEBUTTONDOWN:
                                mouse_pos = event.pos
                                if WHITE_BUTTON.collidepoint(mouse_pos):
                                    is_white = True
                                    side_selected = False
                                    play_mode_selected = False
                                elif BLACK_BUTTON.collidepoint(mouse_pos):
                                    is_white = False
                                    side_selected = False
                                    play_mode_selected = False

                        WHITE_BUTTON, BLACK_BUTTON = displaySideSelection(screen)
                        p.display.flip()
                    playerOne = is_white
                    playerTwo = not is_white
                elif quit_button.collidepoint(mouse_pos):
                    p.mouse.set_cursor()
                    play_mode_selected = False
                    p.quit()
        pvp_button, pvc_button, quit_button = displayPlayModeSelection(screen)
        p.display.flip()
    
    while running:


        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x, y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col) or col >= 8:  # the user clicked the same square twice or outside the board
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append for both 1st and 2nd clicks
                    if len(playerClicks) == 2:  # after 2nd clicks
                        move = chessModule.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' is dressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:  # reset the board when 'r' is pressed
                    gs = chessModule.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    
        # AI move finder logic
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("thinking...")
                returnQueue = Queue()
                moveFinderProcess = Process(target = SearchMove.startSearch, args = (gs, validMoves, returnQueue))
                moveFinderProcess.start()
            if not moveFinderProcess.is_alive():  
                print("done thinking")
                AIMove =  returnQueue.get()
                # AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
                if AIMove is None:
                    AIMove = SearchMove.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False # end the thinking process
            

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)


        if gs.checkMate or gs.staleMate:
            gameOver = True
            text = 'Stalemate' if gs.staleMate else 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate'
            drawEndGameText(screen, text)

        

        clock.tick(MAX_FPS)
        p.display.flip()



"""
Highlight square selected and moves for piece selected
"""


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # sqSelected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value -> 0 transparency; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


"""
Responsible for all the graphics within a current game state.
"""


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw piece on top of those squares
    drawMoveLog(screen, gs, moveLogFont)


"""
Draw the squares on the board. The top left square is always light.
"""


def drawBoard(screen):
    global colors
    colors = [p.Color('white'), p.Color(98, 161, 98)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    # Draw rank notation (numbers)
    rank_notation = ['8', '7', '6', '5', '4', '3', '2', '1']
    for i in range(DIMENSION):
        font = p.font.SysFont('Arial', int(SQ_SIZE /4))  # Adjust the font size as needed
        text_surface = font.render(rank_notation[i], True, p.Color('black'))
        screen.blit(text_surface, (5, i * SQ_SIZE + 5))  # Adjust the position as needed
    
    # Draw file notation (letters)
    file_notation = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for i in range(DIMENSION):
        font = p.font.SysFont('Arial', int(SQ_SIZE / 4))  # Adjust the font size as needed
        text_surface = font.render(file_notation[i], True, p.Color('black'))
        screen.blit(text_surface, ((i+1) * SQ_SIZE - 8, BOARD_HEIGHT - SQ_SIZE/3))  # Adjust the position as needed


"""
Draw the pieces on the board using the current GameState.board
"""


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':  # not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the move log
'''

def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    message1 = "Welcome!!!"
    # message2 = "The sides has been randomly chosen."
    message3 = "Press 'z' to undo the lastest move."
    message4 = "Press 'r' to restart the game."
    message5 = "On your turn, select the chess piece you want "
    message6 = "to move and move it to the highlighted squares."
    message7 = "Wish you have a pleasant experience!"
    message8 = "                         ----------------------"
    message9 = "Instructions:"
    moveTexts = [message1, message9, message3, message4, message5, message6, message7, message8]
    for i in range(0, len(moveLog), 2):
        if i !=0 and i % 38 == 0:
            moveTexts = ["Keep going!", message8, moveTexts[-1]]
        moveString = str(i//2 + 1) + '. White: ' + str(moveLog[i]) + '  '
        if i+1 < len(moveLog): #append the black move
            moveString += 'Black: ' + str(moveLog[i+1])
        moveTexts.append(moveString)

    padding = 2
    textY = padding
    for i in range(len(moveTexts)):
        text = moveTexts[i]
        textObject = font.render(text, 1, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + padding

"""
Animating a move
"""


def animateMove(move, screen, board, clock):
    global colors
    coords = []  # list of coords that the animation will move through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10  # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving pieces
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawEndGameText(screen, text):
    font = p.font.SysFont('Helvitca', 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == '__main__':
    main()
    