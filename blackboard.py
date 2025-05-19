#!/usr/bin/env python3

import pygame
import json
import os

import numpy as np

from dmps.dynamic_movement_primitive import DynamicMovementPrimitive

# Constants
WIDTH, HEIGHT = 800, 600
BG_COLOR = (0, 0, 0)
DRAW_COLOR = (255, 255, 255)
FPS = 60
TRAJECTORY_FILE = "trajectory_blackboard.json"

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

playing_dmp = False
running = True
replaying = False
replay_index = 0
replay_drawn = []

dmp = None
dmp_x = None
dmp_y0 = None
dmp_y = None
dmp_dy = None
speed = 1.0

last_message = None

while running:
    screen.fill(BG_COLOR)

    if last_message is not None:
        draw_text(last_message, (10,10))

    draw_text(f"DMP speed: x{round(speed,1)}", (10, 34))

    # Draw in-progress points
    if len(points) > 1:
        pygame.draw.lines(screen, DRAW_COLOR, False, points, 2)
    
    if replaying:
        if trajectory:
            if replay_index < len(trajectory):
                replay_drawn.append(trajectory[replay_index])
            else:
                last_message = "Done"
                replaying = False
            replay_index += 1
        else:
            last_message = "No trajectory to replay"
            replaying = False

    if playing_dmp:
        if dmp is None:
            if trajectory is None:
                last_message = "No trajectory to imitate"
            else:
                dmp = DynamicMovementPrimitive(dt=1/FPS, n_bfs=100, n_dmps=2, ay=25)
                y = np.asarray(trajectory)
                dmp.fit(y, plot=True)
        tau = 1./speed
        dmp_x, dmp_y, dmp_dy, _ = dmp.step(
            dmp_y,
            dmp_dy,
            dmp_y0,
            np.asarray(pygame.mouse.get_pos()),
            dmp_x,
            tau=tau)
        t = dmp.cs.convert_to_t(dmp_x, tau=tau)
        T = len(trajectory)/FPS*tau
        if t > 1.2*T:
            last_message = "Finished DMP"
            playing_dmp = False
            dmp_y0 = None
        else:
            replay_drawn.append(dmp_y)

    if dmp_y0 is not None:
        pygame.draw.circle(screen, (0,255,0), dmp_y0, 5)

    if len(replay_drawn) > 1:
        pygame.draw.lines(screen, DRAW_COLOR, False, replay_drawn, 2)

    point_registered = False
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
                    last_message = "Trajectory saved"
                    dmp = None

        elif event.type == pygame.MOUSEMOTION:
            if drawing and not point_registered:
                points.append(event.pos)
                point_registered = True

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                speed += 0.1
            elif event.y < 0:
                speed -= 0.1

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                points = []
                replay_drawn = []
                screen.fill(BG_COLOR)
                last_message = "Cleared"
            elif event.key == pygame.K_r:
                recording = True
                points = []
                last_message = "Recording started. Draw a shape now."
            elif event.key == pygame.K_p:
                loaded = load_trajectory(TRAJECTORY_FILE)
                if loaded:
                    trajectory = loaded
                    replaying = True
                    replay_index = 0
                    replay_drawn = [trajectory[0]]  # start with the first point
                    last_message = "Replaying trajectory..."
                else:
                    last_message = "No recorded trajectory found."
            elif event.key == pygame.K_b:
                dmp_y0 = np.asarray(pygame.mouse.get_pos(), dtype=np.float64)
                last_message = "Established initial position. Press D to play DMP."
            elif event.key == pygame.K_d:
                loaded = load_trajectory(TRAJECTORY_FILE)
                if loaded:
                    trajectory = loaded
                    dmp_y = dmp_y0
                    dmp_dy = np.zeros(2)
                    dmp_x = 1.0
                    playing_dmp = True
                    last_message = "Playing DMP trajectories"
                else:
                    last_message = "No trajectory to replay"

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
