'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *
from moba import *

class MyMinion(Minion):
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.states = [Idle]
		### Add your states to self.states (but don't remove Idle)
		### YOUR CODE GOES BELOW HERE ###
		self.states.append(Attack)
		self.states.append(Move)
		### YOUR CODE GOES ABOVE HERE ###
	def start(self):
		Minion.start(self)
		self.changeState(Idle)
############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.
class Idle(State):
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###
		target = None
		agentLocation = self.agent.getLocation()
		towers =  findFirstTower(self.agent)
		bases = findFirstBase(self.agent)
		enemies = findFirstEnemy(self.agent)
		if len(bases) > 0:
			self.agent.changeState(Move, towers, bases, enemies, None)
		### YOUR CODE GOES ABOVE HERE ###
		return None

##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)
class Taunt(State):

	def parseArgs(self, args):
		self.victim = args[0]

	def execute(self, delta = 0):
		if self.victim is not None:
			print("Hey " + str(self.victim) + ", I don't like you!")
		self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:
def findFirstTower(agent):
	towers = agent.world.getEnemyTowers(agent.getTeam())
	towers = sorted(towers, key = lambda x: distance(x.getLocation(), agent.getLocation()))
	return towers

def findFirstBase(agent):	
	bases = agent.world.getEnemyBases(agent.getTeam())
	bases = sorted(bases, key = lambda x: distance(x.getLocation(), agent.getLocation()))
	return bases

def findFirstEnemy(agent):
	enemies = agent.world.getEnemyNPCs(agent.getTeam())
	enemies = sorted(enemies, key = lambda x: distance(x.getLocation(), agent.getLocation()))
	return enemies

def shoot(agent, location):
	agent.turnToFace(location)
	agent.shoot()
def shootable(agent, target):
	return target in agent.getVisible() and distance(agent.getLocation(), target.getLocation()) <= BULLETRANGE
def priorTarget(agent, towers, bases, enemies):
	targets = []
	if towers != None and len(towers) > 0:
		for visible in agent.getVisible():
			if visible in towers:
				targets.append(visible)
	elif bases != None and len(bases) > 0:
		for visible in agent.getVisible():
			if visible in bases:
				targets.append(visible)
	else:
		for visible in agent.getVisible():
			if visible in enemies:
				targets.append(visible)
	targets = sorted(targets, key = lambda x: distance(x.getLocation(), agent.getLocation()))
	return targets
class Move(State):
	def parseArgs(self, args):
		self.towers = args[0]
		self.bases = args[1]
		self.enemies = args[2]
		self.target = args[3]

	def enter(self, oldstate):
		#State.enter(self, oldstate)
		if self.towers != None and len(self.towers) > 0:
			self.target = self.towers[0]
		elif self.bases != None and len(self.bases) > 0:
			self.target = self.bases[0]
		self.agent.navigateTo(self.target.getLocation())
	def execute(self, delta = 0):
		if not self.agent.isMoving():
			self.agent.changeState(Idle)
		targets = priorTarget(self.agent, self.towers, self.bases, self.enemies)
		if targets != None and len(targets) > 0 and shootable(self.agent, targets[0]):
			self.agent.changeState(Attack, self.towers, self.bases, self.enemies, targets[0])
	def exit(self):
		self.agent.stopMoving()
class Attack(State):
	def parseArgs(self, args):
		self.towers = args[0]
		self.bases = args[1]
		self.enemies = args[2]
		self.target = args[3]

	def enter(self, oldstate):
		#State.enter(self, oldstate)
		shoot(self.agent, self.target.getLocation())
	def execute(self, delta = 0):
		shoot(self.agent, self.target.getLocation())
		targets = priorTarget(self.agent, self.towers, self.bases, self.enemies)
		if targets != None and len(targets) > 0 and shootable(self.agent, targets[0]):
			self.target = targets[0]
		else:
			self.agent.changeState(Idle)