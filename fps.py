import pygame
import time


counter = 0
start_time = time.time()
fps = ""

def blit_fps(screen, font):
    """Вывод FPS на экран"""
    global counter, start_time, fps
    counter += 1
    if (time.time() - start_time) > 1:
        fps = "FPS: " + str(int(counter / (time.time() - start_time)))
        counter = 0
        start_time = time.time()
    screen.blit(font.render(fps, True, (180, 0, 0)), (0, 0))