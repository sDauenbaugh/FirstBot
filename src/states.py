import math
from rlbot.agents.base_agent import SimpleControllerState

import util.util as util
from util.vec import Vec3
from util.orientation import relative_location


class State():
    """State objects dictate the bot's current objective.
    
    These objects are used to control the behavior of the bot at a high level. States are reponsible for determining
    which controller to use as well as what actions the car needs to take. States do not directly determine controller inputs.
    State names should be descriptive and unique.
    
    Currently Implemented States:
        BallChase
        
    States in Development:
        Shoot
        Defend
        
    Attributes: expired (bool)
    
    """
    def __init__(self):
        """Creates a new unexpired state"""
        self.expired = False
    
    def execute(self, agent):
        """Executes the State's behavior.
        
        This function must be overridden by other States.
        
        Attributes:
            agent (BaseAgent): The bot
            
        Returns:
            Nothing.
            When overridden this function should return a SimpleControllerState() containing the commands for the car.
            
        """
        pass

class BallChase(State):
    """BallChase aims to drive the car straight toward the ball
    
    This State has no regard for other cars or the movement of the ball. This is a simple state not meant for use in-game.
    
    Note:
        Expires after 30 ticks
    
    """
    def __init__(self):
        """Creates an unexpired instance of BallChase"""
        super().__init__()
        self.ticks = 0
        
    def checkExpire(self):
        """Determines if the state is no longer useful"""
        self.ticks = self.ticks + 1
        if self.ticks > 30:
            self.expired = True
    
    def execute(self, agent):
        """Attempts to drive the car toward the ball.
        
        Overrides the State class's execute function. The ground controller is automatically used and the target 
        location is set to the ball's current location.
        
        Attributes:
            agent (BaseAgent): The bot
            
        Returns:
            SimpleControllerState: the set of commands to give the bot.
            
        """
        self.checkExpire()
        
        State.execute(self, agent)
        target_location = agent.ball.local_location
        
        return agent.controller(agent, target_location)
        
    
class Shoot(State):
    """Shoot attempts to hit the ball toward the opponent's goal"""
    def __init__(self):
        """Creates an instance of Shoot"""
        super().__init__()
        
    def checkExpire(self, agent):
        """Determines if the state is no longer useful"""
        if util.sign(agent.ball.location.y) == util.sign(agent.team):
            self.expired = True
            
    def checkAvailable(self, agent):
        """Determines if the state is an available option"""
        if util.sign(agent.ball.location.y) != util.sign(agent.team):
            return True
        else:
            return False
        
    def execute(self, agent):
        """Drafts a set of commands to shoot the ball toward the opponent's goal
        
        Attributes:
            agent (BaseAgent): the bot
            
        Returns:
            SimpleControllerState: The next set of commands to execute.
        
        """
        self.checkExpire(agent)
        
        team = util.sign(agent.team)
        targetGoal = util.GOAL_POSITION
        targetGoal.y = targetGoal.y * team
        
        ball_to_goal = targetGoal - agent.ball.location
        #distance_to_goal = ball_to_goal.length()
        direction_to_goal = ball_to_goal.normalized()
        
        aim_location = agent.ball.location - (direction_to_goal * util.BALL_RADIUS)
        local_target = relative_location(agent.me.location, agent.me.rotation, aim_location)
        
        return groundController(agent, local_target)
    
class Defend(State):
    """Defend attempts to divert the ball away from the bot's own goal"""
    def __init__(self):
        """Creates an instance of Defend"""
        super().__init__()
    
def groundController(agent, target_location):
    """Gives a set of commands to move the car along the ground toward a target location
    
    Attributes:
        target_location (Vec3): The location the car wants to aim for
        
    Returns:
        SimpleControllerState: the set of commands to achieve the goal
    """
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