# -*- coding: UTF-8 -*-
"""
    @Time    ：2025-02-17 9:11
    @Project ：dia
    @Author  ：Brandon Dong
    @E-mail  : Brandon_Dong@outlook.com
"""
import tkinter as tk
import random
import math
import numpy as np


class Brain():

    def __init__(self, botp):
        self.bot = botp

        # t4: battery attribute of mobile robot ————————————————————————————————————————————————————————————————————————
        self.batteryLevel = 100  # initialise battery capacity
        self.seekCharger = False  # is seek charger mode ?
        # ——————————————————————————————————————————————————————————————————————————————————————————————————————————————

    # modify this to change the robot's behaviour
    def thinkAndAct(self, lightL, lightR, x, y, sl, sr, heatL, heatR):  # t5
        # wheels not moving - no movement - no response to light

        # t4: battery attribute of mobile robot ————————————————————————————————————————————————————————————————————————
        print(f"current battery: {self.batteryLevel} %")
        if self.bot.step_count % 5 == 0:  # battery capacity decreasing for every 5 calls
            self.batteryLevel -= 1
        if self.batteryLevel <= 0:
            self.batteryLevel = 0
            return 0, 0, None, None  # stop move when out of battery
        if self.batteryLevel < 30:  # seek charger when low battery
            self.seekCharger = True
        if self.seekCharger:  # move to the charger when at the seekCharger mode
            chargerX, chargerY = 500, 500  # assume the position of charger is fixed
            angle_to_charger = math.atan2(chargerY - y, chargerX - x)
            speedLeft = 2.0 + math.sin(angle_to_charger - self.bot.theta)
            speedRight = 2.0 - math.sin(angle_to_charger - self.bot.theta)
            # charge when arrive the charger
            if abs(x - chargerX) < 10 and abs(y - chargerY) < 10:
                self.batteryLevel += 10
                if self.batteryLevel >= 100:
                    self.seekCharger = False  # enough battery then quit the seek charger mode
            return speedLeft, speedRight, None, None
        # ——————————————————————————————————————————————————————————————————————————————————————————————————————————————

        # t1: move the mobile robot to the light, t5: second form heater ———————————————————————————————————————————————
        # speedLeft = 5
        # speedRight = 5
        base_speed = 2.0  # basic speed
        light_turn_factor = 0.1  # light turn factor, close to light, -0.1 represents away from light
        heat_turn_factor = 0.1  # heater turn factor, away from heat, 0.1 represents close to heat
        speedLeft = base_speed + (lightR - lightL) * light_turn_factor + (heatR - heatL) * heat_turn_factor
        speedRight = base_speed + (lightL - lightR) * light_turn_factor + (heatL - heatR) * heat_turn_factor
        # ——————————————————————————————————————————————————————————————————————————————————————————————————————————————

        # t2: restrict the speed of mobile robot ———————————————————————————————————————————————————————————————————————
        max_speed = 10.0  # max speed
        min_speed = -10.0  # min speed
        speedLeft = max(min(speedLeft, max_speed), min_speed)  # min <= speed <= max
        speedRight = max(min(speedRight, max_speed), min_speed)  # min <= speed <= max
        # ——————————————————————————————————————————————————————————————————————————————————————————————————————————————

        newX = None
        newY = None
        return speedLeft, speedRight, newX, newY


class Bot():

    def __init__(self, namep):
        self.name = namep
        self.x = random.randint(100, 900)
        self.y = random.randint(100, 900)
        self.theta = random.uniform(0.0, 2.0 * math.pi)
        # self.theta = 0
        self.ll = 60  # axle width
        self.sl = 0.0
        self.sr = 0.0
        self.step_count = 0  # t4: add step count

    def thinkAndAct(self, agents, passiveObjects):
        lightL, lightR = self.senseLight(passiveObjects)
        heatL, heatR = self.senseHeat(passiveObjects)  # t5
        self.sl, self.sr, xx, yy = self.brain.thinkAndAct(lightL, lightR, self.x, self.y, self.sl, self.sr, heatL,
                                                          heatR)  # t5
        if xx != None:
            self.x = xx
        if yy != None:
            self.y = yy
        self.step_count += 1  # t4: add step count

    def setBrain(self, brainp):
        self.brain = brainp

    # returns the output from polling the light sensors
    def senseLight(self, passiveObjects):
        lightL = 0.0
        lightR = 0.0
        for pp in passiveObjects:
            if isinstance(pp, Lamp):
                lx, ly = pp.getLocation()
                distanceL = math.sqrt((lx - self.sensorPositions[0]) * (lx - self.sensorPositions[0]) + \
                                      (ly - self.sensorPositions[1]) * (ly - self.sensorPositions[1]))
                distanceR = math.sqrt((lx - self.sensorPositions[2]) * (lx - self.sensorPositions[2]) + \
                                      (ly - self.sensorPositions[3]) * (ly - self.sensorPositions[3]))
                lightL += 200000 / (distanceL * distanceL)
                lightR += 200000 / (distanceR * distanceR)
        return lightL, lightR

    # t5: second form heater ———————————————————————————————————————————————————————————————————————————————————————————
    def senseHeat(self, passiveObjects):
        heatL = 0.0
        heatR = 0.0
        for pp in passiveObjects:
            if isinstance(pp, Heater):
                hx, hy = pp.getLocation()
                distanceL = math.sqrt((hx - self.sensorPositions[0]) * (hx - self.sensorPositions[0]) + \
                                      (hy - self.sensorPositions[1]) * (hy - self.sensorPositions[1]))
                distanceR = math.sqrt((hx - self.sensorPositions[2]) * (hx - self.sensorPositions[2]) + \
                                      (hy - self.sensorPositions[3]) * (hy - self.sensorPositions[3]))
                heatL += 200000 / (distanceL * distanceL)
                heatR += 200000 / (distanceR * distanceR)
        return heatL, heatR

    # ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————

    # what happens at each timestep
    def update(self, canvas, dt):
        # for now, the only thing that changes is that the robot moves
        #   (using the current settings of self.sl and self.sr)
        self.move(canvas, dt)

    # draws the robot at its current position
    def draw(self, canvas):
        points = [(self.x + 30 * math.sin(self.theta)) - 30 * math.sin((math.pi / 2.0) - self.theta), \
                  (self.y - 30 * math.cos(self.theta)) - 30 * math.cos((math.pi / 2.0) - self.theta), \
                  (self.x - 30 * math.sin(self.theta)) - 30 * math.sin((math.pi / 2.0) - self.theta), \
                  (self.y + 30 * math.cos(self.theta)) - 30 * math.cos((math.pi / 2.0) - self.theta), \
                  (self.x - 30 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta), \
                  (self.y + 30 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta), \
                  (self.x + 30 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta), \
                  (self.y - 30 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta) \
                  ]
        canvas.create_polygon(points, fill="blue", tags=self.name)

        self.sensorPositions = [(self.x + 20 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta), \
                                (self.y - 20 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta), \
                                (self.x - 20 * math.sin(self.theta)) + 30 * math.sin((math.pi / 2.0) - self.theta), \
                                (self.y + 20 * math.cos(self.theta)) + 30 * math.cos((math.pi / 2.0) - self.theta) \
                                ]

        centre1PosX = self.x
        centre1PosY = self.y
        canvas.create_oval(centre1PosX - 8, centre1PosY - 8, \
                           centre1PosX + 8, centre1PosY + 8, \
                           fill="gold", tags=self.name)

        wheel1PosX = self.x - 30 * math.sin(self.theta)
        wheel1PosY = self.y + 30 * math.cos(self.theta)
        canvas.create_oval(wheel1PosX - 3, wheel1PosY - 3, \
                           wheel1PosX + 3, wheel1PosY + 3, \
                           fill="red", tags=self.name)

        wheel2PosX = self.x + 30 * math.sin(self.theta)
        wheel2PosY = self.y - 30 * math.cos(self.theta)
        canvas.create_oval(wheel2PosX - 3, wheel2PosY - 3, \
                           wheel2PosX + 3, wheel2PosY + 3, \
                           fill="green", tags=self.name)

        sensor1PosX = self.sensorPositions[0]
        sensor1PosY = self.sensorPositions[1]
        sensor2PosX = self.sensorPositions[2]
        sensor2PosY = self.sensorPositions[3]
        canvas.create_oval(sensor1PosX - 3, sensor1PosY - 3, \
                           sensor1PosX + 3, sensor1PosY + 3, \
                           fill="yellow", tags=self.name)
        canvas.create_oval(sensor2PosX - 3, sensor2PosY - 3, \
                           sensor2PosX + 3, sensor2PosY + 3, \
                           fill="yellow", tags=self.name)

    # handles the physics of the movement
    # cf. Dudek and Jenkin, Computational Principles of Mobile Robotics
    def move(self, canvas, dt):
        if self.sl == self.sr:
            R = 0
        else:
            R = (self.ll / 2.0) * ((self.sr + self.sl) / (self.sl - self.sr))
        omega = (self.sl - self.sr) / self.ll
        ICCx = self.x - R * math.sin(self.theta)  # instantaneous centre of curvature
        ICCy = self.y + R * math.cos(self.theta)
        m = np.matrix([[math.cos(omega * dt), -math.sin(omega * dt), 0], \
                       [math.sin(omega * dt), math.cos(omega * dt), 0], \
                       [0, 0, 1]])
        v1 = np.matrix([[self.x - ICCx], [self.y - ICCy], [self.theta]])
        v2 = np.matrix([[ICCx], [ICCy], [omega * dt]])
        newv = np.add(np.dot(m, v1), v2)
        newX = newv.item(0)
        newY = newv.item(1)
        newTheta = newv.item(2)
        newTheta = newTheta % (2.0 * math.pi)  # make sure angle doesn't go outside [0.0,2*pi)

        # t3: implement the toroidal geometry ——————————————————————————————————————————————————————————————————————————
        if newX < 0:
            newX = 1000
        elif newX > 1000:
            newX = 0
        if newY < 0:
            newY = 1000
        elif newY > 1000:
            newY = 0
        # ——————————————————————————————————————————————————————————————————————————————————————————————————————————————

        self.x = newX
        self.y = newY
        self.theta = newTheta
        if self.sl == self.sr:  # straight line movement
            self.x += self.sr * math.cos(self.theta)  # sr wlog
            self.y += self.sr * math.sin(self.theta)
        canvas.delete(self.name)
        self.draw(canvas)


class Lamp():
    def __init__(self, namep):
        self.centreX = random.randint(100, 900)
        self.centreY = random.randint(100, 900)
        self.name = namep

    def draw(self, canvas):
        body = canvas.create_oval(self.centreX - 10, self.centreY - 10, \
                                  self.centreX + 10, self.centreY + 10, \
                                  fill="yellow", tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY


# t4: battery attribute of mobile robot ————————————————————————————————————————————————————————————————————————————————
class Charger():
    def __init__(self, namep):
        self.centreX = 500
        self.centreY = 500
        self.name = namep

    def draw(self, canvas):
        body = canvas.create_oval(self.centreX - 10, self.centreY - 10, \
                                  self.centreX + 10, self.centreY + 10, \
                                  fill="green", tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY


# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————


# t5: second form heater ————————————————————————————————————————————————————————————————————————————————
class Heater():
    def __init__(self, namep):
        self.centreX = random.randint(100, 900)
        self.centreY = random.randint(100, 900)
        self.name = namep

    def draw(self, canvas):
        body = canvas.create_oval(self.centreX - 10, self.centreY - 10, \
                                  self.centreX + 10, self.centreY + 10, \
                                  fill="red", tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY


# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————


def initialise(window):
    window.resizable(False, False)
    canvas = tk.Canvas(window, width=1000, height=1000)
    canvas.pack()
    return canvas


def buttonClicked(x, y, agents):
    for rr in agents:
        if isinstance(rr, Bot):
            rr.x = x
            rr.y = y


def createObjects(canvas, noOfBots, noOfLights, noOfChargers, noOfHeaters):  # t4, t5
    agents = []
    passiveObjects = []
    for i in range(0, noOfBots):
        bot = Bot("Bot" + str(i))
        brain = Brain(bot)
        bot.setBrain(brain)
        agents.append(bot)
        bot.draw(canvas)
    for i in range(0, noOfLights):
        lamp = Lamp("Lamp" + str(i))
        passiveObjects.append(lamp)
        lamp.draw(canvas)

    # t4: battery attribute of mobile robot ————————————————————————————————————————————————————————————————————————————
    for i in range(0, noOfChargers):
        charger = Charger("Charger" + str(i))
        passiveObjects.append(Charger)
        charger.draw(canvas)
    # ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————

    # t5: second form heater ———————————————————————————————————————————————————————————————————————————————————————————
    for i in range(0, noOfHeaters):
        heater = Heater("Heater" + str(i))
        passiveObjects.append(Heater)
        heater.draw(canvas)
    # ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————

    canvas.bind("<Button-1>", lambda event: buttonClicked(event.x, event.y, agents))
    return agents, passiveObjects


def moveIt(canvas, agents, passiveObjects):
    for rr in agents:
        rr.thinkAndAct(agents, passiveObjects)
        rr.update(canvas, 1.0)
    canvas.after(50, moveIt, canvas, agents, passiveObjects)


def main():
    window = tk.Tk()
    canvas = initialise(window)  # •	Creates a window to display the scene
    # This consists of two lists. agents is a list of things that move (e.g. robots),
    # and passiveObjects is a list of things that don’t move (e.g. lights, charging stations, barriers)
    agents, passiveObjects = createObjects(canvas, noOfBots=1, noOfLights=1, noOfChargers=1, noOfHeaters=1)  # t4, t5
    moveIt(canvas, agents, passiveObjects)
    window.mainloop()  # update the windows


main()
