import pygame
import sys
import numpy as np
import os
import socket
from mysocket import create_server
import RPi.GPIO as GPIO
import time

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def led_setup():
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(3,GPIO.OUT)
def led_blink():
        t_end = time.time() + 15
        while time.time() < t_end:
                GPIO.output(3,True)
                time.sleep(0.3)
                GPIO.output(3,False)
                time.sleep(0.3)

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
WHITE = (255,255,255)

clock = pygame.time.Clock()
pygame.init()
size = (900, 650)
screen = pygame.display.set_mode(size)
pygame.mixer.music.load(resource_path('assets/music.mp3'))
pygame.mixer.music.play(-1)
GRAVITY, t= pygame.USEREVENT + 1, 800
TICK, t2= pygame.USEREVENT + 2, 400
pygame.time.set_timer(GRAVITY, t)
pygame.time.set_timer(TICK, t2)
boardImage = pygame.image.load(resource_path('assets/boardTemplate.png'))
background = pygame.image.load(resource_path('assets/background.png'))
arcadeFont = pygame.font.Font(resource_path('assets/ARCADECLASSIC.TTF'),30)
arcadeFont2 = pygame.font.Font(resource_path('assets/ARCADECLASSIC.TTF'),80)
scoreTitle = arcadeFont.render("Score",True, (255,255,255))
NextTitle = arcadeFont.render("Next",True, (255,255,255))
GameOver = arcadeFont2.render("Game Over",True, (255,0,0))
figures = [ [1,3,5,7],
            [2,4,5,7],
            [3,5,4,6],
            [3,5,4,7],
            [2,3,5,7],
            [3,5,7,6],
            [2,3,4,5] ]
blockColors = [YELLOW,
    pygame.image.load(resource_path('assets/mavi.png')),
    pygame.image.load(resource_path('assets/sari.png')),
    pygame.image.load(resource_path('assets/turuncu.png')),
    pygame.image.load(resource_path('assets/yesil.png')),
    pygame.image.load(resource_path('assets/pembe.png')),
    pygame.image.load(resource_path('assets/mor.png')),
    pygame.image.load(resource_path('assets/kirmizi.png'))
]
def newBlock(block):
    blockposx = np.array([],dtype=int)
    blockposy = np.array([],dtype=int)
    for i in figures[block]:
            blockposx = np.append(blockposx,int(i%2) + 4)
            blockposy = np.append(blockposy,int(i/2))
    return (blockposx,blockposy)

def rotate(piece,center):
    centerx,centery = center
    piecex,piecey = piece
    for i in range(len(piecex)):
        x = piecey[i] - centery
        y = piecex[i] - centerx
        piecex[i] = centerx - x
        piecey[i] = centery + y

    return piecex,piecey

def gravity(piecey):
    return piecey + 1
def check(board,piece):
    piecex,piecey = piece
    for i in range(len(piecex)):
        if(piecex[i]<0 or piecex[i]>=10 or piecey[i]>=20):
            return 0
        elif(board[piecey[i]][piecex[i]]):
            return 0
    return 1
def checkForTouchDown(board,piece):
    piecex,piecey = piece
    for i in range(len(piecex)):
        try:
            if(board[piecey[i]][piecex[i]] != 0):
                return 0
        except:
            return 0
    return 1

def isFilled(board):
    count = 0
    temp = []
    for i in (range(20)):
        if(np.all(board[i])):
            count += 1
            temp.append(i)
    for i in temp:
        board[i] = 0
        for j in reversed(range(0,i+1)):
            try:
                board[j] = board[j-1]
            except:
                board[1] = board[0]
        board[0] = 0
    return board,count
def checkForGameOver(blockposy):
    return np.any(blockposy<0)

def printTheBoard(board):
    x=0
    y=0
    for rows in board:
        for columns in rows:
            if(columns != 0):
                screen.blit(blockColors[columns],(300 + x*30,25 + y*30, 30, 30))
            x += 1
        x = 0
        y += 1

def main():
    led_setup()
    GPIO.output(3,False)
    s = create_server()
    c, addr = s.accept()
    gameOver = False
    gameBoard = np.zeros((20,10),dtype=int)
    score=0
    tempScore = 0
    posx,posy = (0,0)
    colorNum = 1
    nextColorNum = np.random.randint(1,8,dtype=int)
    block = 3
    blockposx = np.array([],dtype=int)
    blockposy = np.array([],dtype=int)
    tempx = np.array([],dtype=int)
    tempy = np.array([],dtype=int)
    blockposx,blockposy = newBlock(block)
    block = np.random.randint(0,32767,dtype=int)%7
    nextblockposx,nextblockposy = newBlock(block)
    while not gameOver:
        direction = c.recv(4096).decode()
        scoreText = arcadeFont.render(str(score),True, (255,255,255))
        screen.fill(BLACK)
        screen.blit(background,(0,0))
        screen.blit(boardImage,(294,19))
        screen.blit(scoreTitle, (660,28))
        screen.blit(scoreText, (660,52))
        screen.blit(NextTitle, (660,115))
        for i in range(len(nextblockposx)):
            screen.blit(blockColors[nextColorNum],(710+(nextblockposx[i] - 4)*30,160+nextblockposy[i]*30))

        printTheBoard(gameBoard)
        gameBoard,tempScore = isFilled(gameBoard)
        if(tempScore != 0):
            score += (2*tempScore-1)*100
        for i in range(len(blockposx)):
            screen.blit(blockColors[colorNum],(300+blockposx[i]*30,25+blockposy[i]*30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if direction == "left" and event.type == TICK:
                tempx = np.empty_like(blockposx)
                tempx[:] = blockposx
                blockposx -= 1
                if(check(gameBoard,(blockposx,blockposy))==0):
                    blockposx[:] = tempx
            if direction == "change" and event.type == TICK:
                tempx = np.empty_like(blockposx)
                tempx[:] = blockposx
                tempy = np.empty_like(blockposy)
                tempy[:] = blockposy
                blockposx,blockposy = rotate((blockposx,blockposy),(blockposx[1],blockposy[1]))
                if(check(gameBoard,(blockposx,blockposy))==0):
                    blockposx[:] = tempx
                    blockposy[:] = tempy
            if direction == "right" and event.type == TICK:
                tempx = np.empty_like(blockposx)
                tempx[:] = blockposx
                blockposx += 1
                if(check(gameBoard,(blockposx,blockposy))==0):
                    blockposx[:] = tempx

            if event.type == GRAVITY: # is called every 't' milliseconds
                tempy = np.empty_like(blockposy)
                tempy[:] = blockposy
                blockposy = gravity(blockposy)
                if(checkForTouchDown(gameBoard,(blockposx,blockposy))==0):
                    blockposy[:] = tempy
                    for i in range(len(blockposx)):
                        gameBoard[blockposy[i]][blockposx[i]] = colorNum
                    blockposx[:] = nextblockposx
                    blockposy[:] = nextblockposy
                    colorNum = nextColorNum
                    nextColorNum = np.random.randint(1,8,dtype=int)
                    block = np.random.randint(0,32767,dtype=int)%7
                    nextblockposx,nextblockposy = newBlock(block)
                    while(check(gameBoard, (blockposx,blockposy))==0 and not gameOver):
                        blockposy -= 1
                        gameOver = checkForGameOver(blockposy)
        if direction == "down":
            tempy = np.empty_like(blockposy)
            tempy[:] = blockposy
            blockposy += 1
            if(check(gameBoard,(blockposx,blockposy))==0):
                blockposy[:] = tempy
                pygame.display.update()

        gameOver = checkForGameOver(blockposy)
        pygame.display.update()
        clock.tick(60)
    
    s.close()
    pygame.mixer.music.stop()
    screen.blit(GameOver, (265,280))
    pygame.display.update()
    led_blink()
    GPIO.cleanup()
    pygame.time.wait(3000)

if __name__ == "__main__":
    main()


