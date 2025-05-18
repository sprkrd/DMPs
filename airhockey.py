#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Box2D.examples.framework import (Framework, Keys, main)
from Box2D import (b2CircleShape, b2FixtureDef, b2ChainShape, b2PolygonShape,
                   b2RevoluteJointDef, b2_pi, b2Vec2)

from math import sqrt

from dmps.dynamic_movement_primitive import DynamicMovementPrimitive

import matplotlib.pyplot as plt
import numpy as np
import json

class Airhockey(Framework):
    name = "Airhockey"
    description = ('Control the mallet using the mouse')
    bodies = []
    joints = []

    scale_factor = 20
    table_width = 1.038
    table_length = 1.948
    goal_length = 0.25
    puck_radius = 0.03165
    mallet_radius = 0.04815

    P = 2000
    D = 2.5*sqrt(P)

    def __init__(self):
        super().__init__()

        w = Airhockey.scale_factor * Airhockey.table_width
        l = Airhockey.scale_factor * Airhockey.table_length
        g = Airhockey.scale_factor * Airhockey.goal_length
        m = Airhockey.scale_factor * Airhockey.mallet_radius
        p = Airhockey.scale_factor * Airhockey.puck_radius


        self.settings.hz = 100

        self.world.gravity = (0, 0)

        self.recorded_trajectory = None
        self.dmp = None
        self.trigger_reset = False
        self.recording = False
        self.reproducing = False
        self.reproducing_dmp = False
        self.dmp_x = None
        self.tracking = False
        self.reproduction_timestep = 0
        self.reproduction_length = 0

        walls = self.world.CreateStaticBody(
            shapes=[
                # bottom half
                b2ChainShape(vertices_chain=[
                    (-l/2, -g/2),
                    (-l/2, -w/2),
                    (l/2, -w/2),
                    (l/2, -g/2)
                ]),

                # top half
                b2ChainShape(vertices_chain=[
                    (-l/2, g/2),
                    (-l/2, w/2),
                    (l/2, w/2),
                    (l/2, g/2)
                ]),
            ]
        )

        # Mallet
        self.mallet = self.world.CreateDynamicBody(
            fixtures=b2FixtureDef(
                shape=b2CircleShape(radius=m),
                density=1.0,
                restitution=0),
            bullet=True,
            linearDamping=0,
            angularDamping=5,
            position=(-l/4, 0))

        # Puck
        self.puck = self.world.CreateDynamicBody(
            fixtures=b2FixtureDef(
                shape=b2CircleShape(radius=p),
                density=0.25,
                restitution=0.8),
            bullet=True,
            linearDamping=0,
            angularDamping=5,
            position=(-l/4, w/4))

    def Keyboard(self, key):
        if key == Keys.K_a:
            self.pressed = True

    def LoadTrajectory(self):
        if self.recorded_trajectory is None:
            try:
                with open("recorded_trajectory.json", "r") as f:
                    self.recorded_trajectory = json.load(f)
            except FileNotFoundError:
                print("trajectory file not found, create a trajectory first")
                return False
        return True

    def FitDMP(self):
        if not self.LoadTrajectory():
            return False
        dmp = DynamicMovementPrimitive(dt=1/self.settings.hz, n_bfs=100, n_dmps=2, ay=25)
        y = np.array([self.recorded_trajectory["position_x"], self.recorded_trajectory["position_y"]]).T
        dmp.fit(y, plot=True)
        self.dmp = dmp
        return True

    def KeyboardUp(self, key):
        if key == Keys.K_a:
            self.pressed = False
        elif key == Keys.K_r:
            self.trigger_reset = True
        elif key == Keys.K_s:
            if self.recording:
                print("Stop recording")
                with open("recorded_trajectory.json", "w") as f:
                    json.dump(self.recorded_trajectory, f, indent=4)
                self.recording = False
            else:
                print("Begin recording")
                self.dmp = None
                self.recorded_trajectory = {
                        "position_x": [],
                        "position_y": [],
                        "velocity_x": [],
                        "velocity_y": [],
                        "acceleration_x": [],
                        "acceleration_y": [],
                        "dt": 1./self.settings.hz
                }
                self.recording = True
        elif key == Keys.K_p:
            if self.LoadTrajectory():
                self.reproducing = True
                self.reproduction_timestep = 0
                self.reproduction_length = len(self.recorded_trajectory["position_x"])
        elif key == Keys.K_d:
            if self.dmp is None:
                if not self.FitDMP():
                    print("Could not fit DMP")
                    return
            self.reproducing_dmp = True
            self.dmp_x = 1.0
            self.dmp_y0 = np.asarray(self.mallet.worldCenter)
        elif key == Keys.K_t:
            self.tracking = not self.tracking

    def ResetStatus(self):
        w = Airhockey.scale_factor * Airhockey.table_width
        l = Airhockey.scale_factor * Airhockey.table_length
        self.puck.linearVelocity = (0,0)
        self.puck.position = (-l/4, w/4)
        self.mallet.linearVelocity = (0,0)
        if self.mouseWorld:
            self.mallet.position = self.mouseWorld
        else:
            self.mallet.position = (-l/4, 0)

    def DurationRecordedTrajectory(self):
        dt = self.recorded_trajectory["dt"]
        return dt * len(self.recorded_trajectory["position_x"])

    def Step(self, settings):
        if self.trigger_reset:
            self.ResetStatus()
            self.trigger_reset = False
            
        if self.reproducing and self.reproduction_timestep >= len(self.recorded_trajectory["position_x"]):
            self.reproducing = False
        
        target = None
        if self.reproducing:
            target = b2Vec2(
                self.recorded_trajectory["position_x"][self.reproduction_timestep],
                self.recorded_trajectory["position_y"][self.reproduction_timestep]
            )
            self.reproduction_timestep += 1
        elif self.reproducing_dmp:
            malletPos = self.mallet.worldCenter
            malletVel = self.mallet.linearVelocity
            x, y, dy, ddy = self.dmp.step(
                    np.asarray(self.mallet.worldCenter),
                    np.asarray(self.mallet.linearVelocity),
                    self.dmp_y0,
                    np.asarray(self.puck.worldCenter),
                    self.dmp_x
            )
            self.dmp_x = x
            # target = y
            # self.mallet.position = y
            # self.mallet.linearVelocity = dy
            self.mallet.ApplyForceToCenter(ddy*self.mallet.mass, True)
            t = self.dmp.cs.convert_to_t(x)
            T = self.DurationRecordedTrajectory()
            if t > T:
                print("finished")
                self.mallet.linearVelocity = (0,0)
                self.reproducing_dmp = False
        elif self.mouseWorld and self.tracking:
            target = self.mouseWorld
            
        if target is not None:
            e = target - self.mallet.worldCenter
            de = - self.mallet.linearVelocity
            self.mallet.ApplyForce(self.P*e + self.D*de, self.mallet.worldCenter, True)
        if self.recording:
            malletPos = self.mallet.worldCenter
            malletVel = self.mallet.linearVelocity
            if self.recorded_trajectory["velocity_x"]:
                prevVelX = self.recorded_trajectory["velocity_x"][-1]
                prevVelY = self.recorded_trajectory["velocity_y"][-1]
            else:
                prevVelX = 0
                prevVelY = 0
            inv_dt = self.settings.hz
            self.recorded_trajectory["position_x"].append(malletPos[0])
            self.recorded_trajectory["position_y"].append(malletPos[1])
            self.recorded_trajectory["velocity_x"].append(malletVel[0])
            self.recorded_trajectory["velocity_y"].append(malletVel[1])
            self.recorded_trajectory["acceleration_x"].append(inv_dt*(malletVel[0]-prevVelX))
            self.recorded_trajectory["acceleration_y"].append(inv_dt*(malletVel[1]-prevVelY))
            

        super().Step(settings)

if __name__ == "__main__":
    main(Airhockey)
