#!/usr/bin/env python3

import pygame
import json
import os

# Constants
WIDTH, HEIGHT = 800, 600
BG_COLOR = (0, 0, 0)
DRAW_COLOR = (255, 255, 255)
FPS = 60
TRAJECTORY_FILE = "trajectory.json"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackboard")
clock = pygame.time.Clock()

drawing = False
recording = False
trajectory = []
points = []

font = pygame.font.SysFont(None, 24)

def save_trajectory(traj, filename):
    with open(filename, 'w') as f:
        json.dump(traj, f)

def load_trajectory(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        return json.load(f)

def draw_text(text, pos):
    img = font.render(text, True, (255, 0, 0))
    screen.blit(img, pos)

running = True
replaying = False
replay_index = 0
replay_drawn = []

while running:
    screen.fill(BG_COLOR)

    # Draw in-progress points
    if len(points) > 1:
        pygame.draw.lines(screen, DRAW_COLOR, False, points, 2)
    
    if replaying:
        if trajectory:
            if replay_index < len(trajectory):
                replay_drawn.append(trajectory[replay_index])
            else:
                print("done")
                replaying = False
            replay_index += 1
        else:
            draw_text("No trajectory to replay", (10, 10))
            replaying = False
    
    if len(replay_drawn) > 1:
        pygame.draw.lines(screen, DRAW_COLOR, False, replay_drawn, 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                drawing = True
                if recording:
                    points = []

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                if recording:
                    recording = False
                    trajectory = points[:]
                    save_trajectory(trajectory, TRAJECTORY_FILE)

        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                points.append(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                points = []
                replay_drawn = []
                screen.fill(BG_COLOR)
            elif event.key == pygame.K_r:
                recording = True
                points = []
                print("Recording started. Draw a shape now.")
            elif event.key == pygame.K_p:
                loaded = load_trajectory(TRAJECTORY_FILE)
                if loaded:
                    trajectory = loaded
                    replaying = True
                    replay_index = 0
                    replay_drawn = [trajectory[0]]  # start with the first point
                    print("Replaying trajectory...")
                else:
                    print("No recorded trajectory found.")

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
