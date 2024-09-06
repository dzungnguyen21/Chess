from AI import Evaluation



def orderMoves(gs, validMoves):
    #move ordering
    moveScores = {}
    for move in validMoves:
        # move repitition
        if move.moveID in moveScores:
            moveScore += 1000000
            continue
        moveScore = 0
        movePiece = move.pieceMoved
        capturePiece = move.pieceCaptured

        movePieceType = movePiece[1]
        capturePieceType = capturePiece[1]

        endSquareRow = move.endRow
        endSquareCol = move.endCol
        startSquareRow = move.startRow
        startSquareCol = move.startCol

        isCapture = capturePieceType != '-'
        opponentCanRecapture = gs.squareUnderAttack(endSquareRow, endSquareCol)


        if isCapture:
            # Determine simple winning or losing based on pieces score
            captureMaterialDelta = Evaluation.pieceScore[capturePieceType] - Evaluation.pieceScore[movePieceType]

            if opponentCanRecapture:
                if captureMaterialDelta >= 0:
                    moveScore += 80000 + captureMaterialDelta
                else:
                    moveScore += 20000 + captureMaterialDelta

            else:
                
                moveScore += 80000 + captureMaterialDelta


        if movePieceType == 'p': 
            # Pawn Promotion
            if move.isPawnPromotion and  not isCapture:
                moveScore += 60000
        elif movePieceType != 'K':
            # Position score on recapture
            toScore = Evaluation.piecePositionScores[movePiece][endSquareRow][endSquareCol]
            fromScore = Evaluation.piecePositionScores[movePiece][startSquareRow][startSquareCol]
            moveScore += toScore - fromScore
            if gs.squareUnderPawnsAttack(endSquareRow, endSquareCol):
                moveScore -= 50
            elif opponentCanRecapture:
                moveScore -= 25
            

        # Hashing
        moveScores[move.moveID] = moveScore
    
    # Order the moves based on their scores (higher scores first)
    validMoves.sort(key=lambda move: moveScores[move.moveID], reverse=True)

