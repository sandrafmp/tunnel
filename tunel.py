"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "south"
NORTH = "north"

NCARS = 100
NLINE = 5

#### IDEA ####
#The idea for the full program is to check if we have a waiting car on the other side, and if that is the case we
#let 5 cars pass before letting the waiting car on the opposite pass.


class Monitor():
    def __init__(self):
        self.inside_north = Value('i', 0) #cars inside directed north
        self.inside_south = Value('i', 0) #cars inside directed south
        self.turno_north = Value('i',False) #north cars can pass
        self.turno_south = Value('i', False) #south cars can pass
        self.counter = Value('i',0) #counting how many cars have entered
        self.waiting = Value('i',False) #if anyone is waiting to enter
        self.mutex = Lock() #semaphore to regulate the process
        self.ok_to_go = Condition (self.mutex) #condition

    def can_enter(self,direction):
        if direction==SOUTH:
            #south cars can pass if there isn't any inside going north and it is their turn
            if self.inside_north.value==0 and self.turno_south.value:
                return True
            return False
        if direction==NORTH:
            #north cars can pass if there isn't any inside going south and it is their turn
            if self.inside_south.value==0 and self.turno_north.value:
                return True
            return False

    #notifies the tunnel a car has arrived
    def wants_enter(self,direction):
        self.mutex.acquire()
        #setting the direction if the tunnel is free
        if self.inside_north.value==0 and self.inside_south.value==0:
            if direction==SOUTH:
                self.turno_south.value=True
            if direction==NORTH:
                self.turno_north.value=True
        if self.can_enter(direction) == False:  # if can_enter is false, a car is waiting
            self.waiting.value = True
        #waits for the tunnnel being accessible
        self.ok_to_go.wait_for(lambda: self.can_enter(direction))

        self.counter.value +=1
        #change direction when there are more than NLINE cars have entered and at least a car waiting
        if direction==SOUTH:
            self.inside_south.value+=1
            if self.counter.value>NLINE and self.waiting.value:
                self.turno_south.value=False
        if direction==NORTH:
            self.inside_north.value+=1
            if self.counter.value>NLINE and self.waiting.value:
                self.turno_north.value=False
        self.mutex.release()

    def leaves_tunnel(self,direction):
        self.mutex.acquire()
        if direction==SOUTH:
            self.inside_south.value-=1
            # when south empties, it's time to open up the entry
            if self.inside_south.value==0:
                if self.waiting.value == True:
                    self.turno_north.value=True
                    self.waiting.value=False
                #no need to force a change in direction anymore
                self.counter.value=0
                #every car can go now
                self.ok_to_go.notify_all()
            elif self.turno_south.value==False:
                if self.counter.value>0:
                    self.counter.value-=1
                else:
                    self.turno_north.value=True
                    self.waiting.value=False
                    self.ok_to_go.notify_all()
        if direction==NORTH:
            self.inside_north.value-=1
            if self.inside_north.value==0:
                if self.waiting.value == True:
                    self.turno_south.value=True
                    self.waiting.value=False
                self.counter.value=0
                self.ok_to_go.notify_all()
            elif self.turno_north.value==False:
                if self.counter.value>0:
                    self.counter.value-=1
                else:
                    self.turno_south.value=True
                    self.waiting.value=False
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
        direction = NORTH if random.randint(0,1)==1  else NORTH
        if cid == 14:   #change distribution of the cars
            direction = SOUTH


        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s

if __name__ == '__main__':
    main()
