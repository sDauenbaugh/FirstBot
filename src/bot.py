import math
import time

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation, relative_location
from util.vec import Vec3
from util.util import predict_ball_path, sign

from states import *

class GameObject():
    """GameObjects are considered to be all objects that can move on the field.
        
    Attributes:
        location (Vec3): location vector defined by x,y,z coordinates
        velocity (Vec3): velocity vector with x,y,z components
        orientation (Orientation): orientation vector defined by pitch, yaw, and roll
        rvelocity (Vec3): Rotational velocity define by pitch, yaw, and roll components as x, y, z respectively
        local_location (Vec3): location of the GameObject relative to the bot
        
    """
    
    def __init__(self):
        """Creates a new GameObject with zeroed data."""
        self.location = Vec3(0,0,0)
        self.velocity = Vec3(0,0,0)
        self.orientation = Orientation(0,0,0)
        self.rvelocity = Vec3(0,0,0)
        
        self.local_location = Vec3(0,0,0)

class Car(GameObject):
    """Car is an Extension of the GameObject class that holds data and function specific to the bahavior of other cars.
    
    Attributes:
        boost (float): The amount of boost remaining in the car
    
    """
    def __init__(self):
        """Creates a new Car object with zero boost."""
        super().__init__()
        self.boost = 0.0
    

class Ball(GameObject):
    """Ball is an extension of the gameObject class that holds data and functions specific to the ball
    
    """
    def __init__(self):
        """Creates a new Ball object."""
        super().__init__()

class MyBot(BaseAgent):
    """MyBot is an extension of the BaseAgent class and handles all of the logic of the bot. 
    
    This is the class used by the rlBot framework to run the bot in-game.
    
    Attributes:
        controller_state (SimpleControllerState): The current set of commands the bot's controller should recieve
        me (Car): The Car GameObject representing the bot
        ball (Ball): The Ball object representing the ball
        state (State): The state governing the bot's current behavior
        controller (Controller): The controller governing the bot's movement
    
    """

    def initialize_agent(self):
        """The setup function that runs once when the bot is created."""
        self.controller_state = SimpleControllerState()
        self.me = Car()
        self.ball = Ball()
        
        self.state = Shoot()
        self.controller = groundController
        self.stateMessage = "Whoops"
        
        self.timer1 = time.time()

    def get_output(self, gamePacket: GameTickPacket) -> SimpleControllerState:
        """Calculates the next set of commands for the bot.
        
        This function should run 60 times a second, or once for every game tick. This function also calls a set
        of commands to draw debug information on screen.
        
        Args:
            gamePacket (GameTickPacket): set of current information about the game
            
        Returns:
            SimpleControllerState: the next set of commands for the bot
            
        """
        self.preprocess(gamePacket)
                
        if self.state.expired == True:
            if AimShot().checkAvailable(self) == True:
                self.state = AimShot()
                self.stateMessage = "Aiming"
            #if Shoot().checkAvailable(self) == True:
            #    self.state = Shoot()
            #    self.stateMessage = "Shooting"
            elif Defend().checkAvailable(self) == True:
                self.state = Defend()
                self.stateMessage = "Defending"
            else:
                self.state = BallChase()
                self.stateMessage = "Chasing"
        controller_state = self.state.execute(self)
        
        team = sign(self.team)
        ball_side = sign(self.ball.location.y)
        
        my_car = gamePacket.game_cars[self.index]
        message = f"{self.stateMessage} | Team {team} | Ball {ball_side} "
        action_display = message
        ball_path = predict_ball_path(self)
        draw_debug(self.renderer, my_car, gamePacket.game_ball, action_display, ball_path)

        return controller_state
    
    def preprocess(self, gamePacket: GameTickPacket):
        """Calculates a set of values that may be useful.
        
        This function runs every tick, so it should not contain any operations that are slow. Additionally, the operations
        should be limited to what is necessary to have on every tick.
        
        Args:
            gamePacket (GameTickPacket): set of current information about the game
            
        Returns:
            This function updates the attributes of the class and therefore has no return type. 
            
        """
        #load data about self
        self.me.location = Vec3(gamePacket.game_cars[self.index].physics.location)
        self.me.velocity = Vec3(gamePacket.game_cars[self.index].physics.velocity)
        self.me.rotation = Orientation(gamePacket.game_cars[self.index].physics.rotation)
        self.me.rvelocity = Vec3(gamePacket.game_cars[self.index].physics.angular_velocity)
        self.me.boost = gamePacket.game_cars[self.index].boost
        
        #load data about the ball
        self.ball.location = Vec3(gamePacket.game_ball.physics.location)
        self.ball.velocity = Vec3(gamePacket.game_ball.physics.velocity)
        self.ball.rotation = Orientation(gamePacket.game_ball.physics.rotation)
        self.ball.rvelocity = Vec3(gamePacket.game_ball.physics.angular_velocity)
        
        self.ball.local_location = relative_location(self.me.location, self.me.rotation, self.ball.location)


def draw_debug(renderer, car, ball, action_display, ball_path = None):
    """Draws debug information on screen.
    
    Args:
        renderer: renderer that will draw the information
        car: car object from GameTickPacket representing the bot
        ball: ball object from GameTickPacket
        action_discplay: message to display describing the car's current action
        ball_path: set of information containing the ball's predicted path
        
    Returns:
        This function has no returns, but instead draws information directly to the screen.
    
    """
    renderer.begin_rendering()
    # draw a line from the car to the ball
    renderer.draw_line_3d(car.physics.location, ball.physics.location, renderer.white())
    # print the action that the bot is taking
    renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())
    #draw the ball's predicted path
    renderer.draw_polyline_3d(ball_path, renderer.red())
    renderer.end_rendering()
