"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "south"
NORTH = "north"

NCARS = 20

class Monitor():

	def __init__(self):
		self.inside_north = Value('i', 0)
		self.inside_south = Value('i', 0)
		self.mutex = Lock()
		self.ok_to_go = Condition(self.mutex)

	def can_enter(self,direction):
		if direction==SOUTH:
			if self.inside_north.value!=0:
				return False
			return True
		if direction==NORTH:
			if self.inside_south.value!=0:
				return False
			return True

	def wants_enter(self,direction):
		self.mutex.acquire()
		self.ok_to_go.wait_for(lambda: self.can_enter(direction)==True)
		if direction==SOUTH:
			self.inside_south.value+=1
		if direction==NORTH:
			self.inside_north.value+=1
		self.mutex.release()

	def leaves_tunnel(self,direction):
		self.mutex.acquire()
		if direction==SOUTH:
			self.inside_south.value-=1
			if self.inside_south.value==0:
				self.ok_to_go.notify_all()
		if direction==NORTH:
			self.inside_north.value-=1
			if self.inside_north==0:
				self.ok_to_go.notify_all()
		self.mutex.release()



def delay(n=3):
	time.sleep(random.random()*n)

def car(cid, direction, monitor):
	print (f"car {cid} direction {direction} created")
	delay(6)
	print(f"car {cid} heading {direction} wants to enter")
	monitor.wants_enter(direction)
	print(f"car {cid} heading {direction} enters the tunnel")
	delay(3)
	print(f"car {cid} heading {direction} leaving the tunnel")
	monitor.leaves_tunnel(direction)
	print(f"car {cid} heading {direction} out of the tunnel")



def main():
	monitor = Monitor()
	cid = 0
	for _ in range(NCARS):
		direction = NORTH if random.randint(0,1)==1  else SOUTH
		cid += 1
		p = Process(target=car, args=(cid, direction, monitor))
		p.start()
		time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s

if __name__ == '__main__':
	main()
