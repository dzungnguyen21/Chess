
from AI import Evaluation
from AI import MoveOrdering
import random

CHECKMATE = 9999999

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def startSearch(gs, validMoves, returnQueue):
    global nextMove, counter
    counter = 0
    nextMove = None

    # Iterative deppening
    for depth in range(1, gs.depth() + 1):

        NegaMaxAlphaBeta(gs, validMoves, depth, 0, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)

        if counter >= 80000:
            break

    print(counter)

    returnQueue.put(nextMove)

def NegaMaxAlphaBeta(gs, validMoves, depth, ply, alpha, beta, turnMultiple):
    global nextMove, counter

    counter += 1

    if counter >= 80000:
        return 0

    # Consider quiet position while depth reached
    if depth == 0 or gs.checkMate or gs.staleMate:
        return quiescenceSearch(gs, alpha, beta, turnMultiple)
    
    #move ordering
    MoveOrdering.orderMoves(gs, validMoves)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
   
        nextMoves = gs.getValidMoves()

        score = -NegaMaxAlphaBeta(gs, nextMoves, depth-1, ply + 1, -beta, -alpha, -turnMultiple)
        if score > maxScore:
            maxScore = score
            if ply == 0:
                nextMove = move
     
        gs.undoMove()



        if maxScore > alpha:
            alpha = maxScore
        
        if alpha >= beta:

            break

    return maxScore


# Evaluate quiet position
def quiescenceSearch(gs, alpha, beta, turnMultiple):
    global counter
    counter += 1

    if counter >= 80000:
        return 0

    eval = turnMultiple * Evaluation.scoreBoard(gs)

    alpha = max(alpha, eval)
    if eval >= beta:
        return beta

    # Get capture move only
    captureMoves = gs.getCaptureMoves()
    MoveOrdering.orderMoves(gs,captureMoves)

    for move in captureMoves:
        gs.makeMove(move)
        eval = -quiescenceSearch(gs,-beta,-alpha, -turnMultiple)
        gs.undoMove()

        alpha = max(alpha, eval)
        if eval >= beta:
            return beta

    return alpha