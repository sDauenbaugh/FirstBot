import math
from rlbot.agents.base_agent import SimpleControllerState

class State():
    def __init__(self):
        pass
    
    def execute(self, agent):
        pass

class BallChase(State):
    def __init__(self):
        self.expired = False
    
    def execute(self, agent):
        State.execute(self, agent)
        target_location = agent.ball.local_location
        
        return agent.controller(agent, target_location)
        
    
class Shoot(State):
    def __init__(self):
        pass
    
class Defend(State):
    def __init__(self):
        pass
    
def groundController(agent, target_location):
    controllerState = SimpleControllerState()
    ball_direction = target_location;
    distance = target_location.flat().length()
    
    angle = -math.atan2(ball_direction.y,ball_direction.x)

    if angle > math.pi:
        angle -= 2*math.pi
    elif angle < -math.pi:
        angle += 2*math.pi
    
    speed = 0.0
    turn_rate = 0.0
    r1 = 250
    r2 = 1000
    if distance <= r1:
        #calculate turn direction
        if(angle > math.pi/16):
            turn_rate = -1.0
        elif(angle < -math.pi/16):
            turn_rate = 1.0
        #if toward ball move forward
        if(abs(angle) < math.pi / 4):
            speed = 1.0
        else: #if not toward ball reverse, flips turn rate to adjust
            turn_rate = turn_rate * -1.0
            speed = -1.0
    #if far away, move at full speed forward
    elif distance >= r2:
        speed = 1.0
        if(angle > math.pi/12):
            turn_rate = -1.0
        elif(angle < -math.pi/12):
            turn_rate = 1.0
    #if mid range, adjust forward
    else:
        #adjust angle
        if(angle > math.pi/12):
            turn_rate = -1.0
        elif(angle < -math.pi/12):
            turn_rate = 1.0
        #adjust speed
        if abs(angle) < math.pi / 2:
            speed = 1.0
        else:
            speed = 0.5
            
    controllerState.throttle = speed
    controllerState.steer = turn_rate
    return controllerState