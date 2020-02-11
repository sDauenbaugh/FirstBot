import math
import time
from rlbot.agents.base_agent import SimpleControllerState

import util.util as util
from util.vec import Vec3
from util.orientation import relative_location
from util.util import predict_ball_path, GOAL_HOME


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
    
    def checkAvailable(self, agent):
        """Checks to see if the state is available. The default state is unavailable
        
        Attributes:
            agent (BaseAgent): the bot
        
        Returns:
            bool: False unless overridden. True means available, false means unavailable.
        
        """
        return False

class BallChase(State):
    """BallChase aims to drive the car straight toward the ball
    
    This State has no regard for other cars or the movement of the ball. This is a simple state not meant for use in-game.
    
    Note:
        This state is always available and expires after every tick.
    
    """
    def __init__(self):
        """Creates an unexpired instance of BallChase"""
        super().__init__()
        self.ticks = 0
        
    def checkAvailable(self, agent):
        """This state is always available"""
        return True
        
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
        
        return groundController(agent, target_location)
        
    
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
        """Attempts to hit the ball in a way that pushes it toward the goal"""
        self.checkExpire(agent)
        
        team = util.sign(agent.team)
        targetGoal = util.GOAL_HOME * -team
        
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
        
    def checkAvailable(self, agent):
        """Available when the ball is on the friendly side of the field"""
        if util.sign(agent.ball.location.y) == util.sign(agent.team):
            return True
        return False
    
    def checkExpired(self, agent):
        if util.sign(agent.ball.location.y) != util.sign(agent.team):
            self.expired = True
    
    def execute(self, agent):
        self.checkExpired(agent)
        team = util.sign(agent.team)
        ball_path = predict_ball_path(agent)
        danger = False
        for loc in ball_path:
            if(math.fabs(loc.y) > math.fabs(util.FIELD_LENGTH / 2)):
                danger = True
        target_location = agent.ball.local_location
        if danger:
            #aim to hit ball to the side
            #detect of ball is east or west of bot
            east_multiplier = util.sign(agent.ball.location.x - agent.me.location.x)
            #aim for side of the ball
            aim_location = agent.ball.location + Vec3(east_multiplier * util.BALL_RADIUS, 0, 0)
            target_location = relative_location(agent.me.location, agent.me.rotation, aim_location)
        elif agent.ball.local_location.length() > 500:
            #get in goal
            target_location = relative_location(agent.me.location, agent.me.rotation, util.GOAL_HOME * team)
        return groundController(agent, target_location)
    
class AimShot(State):
    """Aims the shot toward the net"""
    def __init__(self):
        """Creates an instance of AimShot"""
        super().__init__()
        
    def checkAvailable(self, agent):
        """If the ball is between the car and the goal, it is possible to shoot"""
        ballDirection = agent.ball.local_location
        goal_location = relative_location(agent.me.location, agent.me.rotation, util.GOAL_HOME*util.sign(agent.team)*-1)
        angle = ballDirection.ang_to(goal_location)
        if angle < (math.pi / 2):
            return True
        return False
    
    def checkExpired(self, agent, team):
        """If the ball is not reasonably close to being between the car and the goal, the state expires"""
        ballDirection = agent.ball.local_location
        goal_location = relative_location(agent.me.location, agent.me.rotation, util.GOAL_HOME*team*-1)
        angle = ballDirection.ang_to(goal_location)
        if angle < (math.pi / 2):
            return False
        return True
    
    def execute(self, agent):
        team = util.sign(agent.team)
        self.expired = self.checkExpired(agent, team)
        
        return shotController(agent, util.GOAL_HOME*team*-1)
    
def groundController(agent, target_location):
    """Gives a set of commands to move the car along the ground toward a target location
    
    Attributes:
        target_location (Vec3): The local location the car wants to aim for
        
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

def shotController(agent, shotTarget):
    """Gives a set of commands to make the car shoot the ball
    
    This function will flip the car into the ball in order to make a shot and
    it will adjust the car's speed and positioning to help make the shot.
    
    Attributes:
        shotTarget (Vec3): The position that we want to hit the ball toward
        
    Returns:
        SimpleControllerState: the set of commands to achieve the goal
    """
    controllerState = SimpleControllerState()
    #get ball distance and angle from car
    ball_direction = agent.ball.local_location
    ball_distance = agent.ball.local_location.flat().length()
    ball_angle = -math.atan2(ball_direction.y,ball_direction.x)
    if ball_angle > math.pi:
        ball_angle -= 2*math.pi
    elif ball_angle < -math.pi:
        ball_angle += 2*math.pi
    #get target distance and angle from ball
    ball_to_target = agent.ball.location - shotTarget
    target_distance = ball_to_target.length()
    ball_to_target_unit = ball_to_target.normalized()
    if(ball_distance < 270):
        flipReady = True
    else:
        flipReady = False
    
    #flipping
    if(flipReady):
        time_diff = time.time() - agent.timer1
        if time_diff > 2.2:
            agent.timer1 = time.time()
        elif time_diff <= 0.1:
            #jump and turn toward the ball
            controllerState.jump = True
            if ball_angle > 0:
                controllerState.yaw = -1
            elif ball_angle < 0:
                controllerState.yaw = 1
        elif time_diff >= 0.1 and time_diff <= 0.15:
            #keep turning
            controllerState.jump = False
            if ball_angle > 0:
                controllerState.yaw = -1
            elif ball_angle < 0:
                controllerState.yaw = 1
        elif time_diff > 0.15 and time_diff < 1:
            #flip
            controllerState.jump = True
            if ball_angle > 0:
                controllerState.yaw = -1
            elif ball_angle < 0:
                controllerState.yaw = 1
            if math.fabs(ball_angle) > math.pi:
                controllerState.pitch = 1
            else:
                controllerState.pitch = -1
        else:
            flipReady = False
            controllerState.jump = False
    else:
        controllerState = groundController(agent, ball_direction)
    
    return controllerState