import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation, relative_location
from util.vec import Vec3

from states import *

class GameObject():
    def __init__(self):
        self.location = Vec3(0,0,0)
        self.velocity = Vec3(0,0,0)
        self.orientation = Orientation(0,0,0)
        self.rvelocity = Vec3(0,0,0)
        
        self.local_location = Vec3(0,0,0)

class Car(GameObject):
    def __init__(self):
        super().__init__()
        self.boost = 0.0
    

class Ball(GameObject):
    def __init__(self):
        super().__init__()

class MyBot(BaseAgent):

    def initialize_agent(self):
        # This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        self.me = Car()
        self.ball = Ball()
        
        self.state = BallChase()
        self.controller = groundController

    def get_output(self, gamePacket: GameTickPacket) -> SimpleControllerState:
        self.preprocess(gamePacket)
        controller_state = self.state.execute(self)
        
        my_car = gamePacket.game_cars[self.index]
        message = f"speed: {controller_state.throttle} | turn: {controller_state.steer}"
        action_display = message
        draw_debug(self.renderer, my_car, gamePacket.game_ball, action_display)

        return controller_state
    
    def preprocess(self, gamePacket: GameTickPacket):
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


def draw_debug(renderer, car, ball, action_display):
    renderer.begin_rendering()
    # draw a line from the car to the ball
    renderer.draw_line_3d(car.physics.location, ball.physics.location, renderer.white())
    # print the action that the bot is taking
    renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())
    renderer.end_rendering()
