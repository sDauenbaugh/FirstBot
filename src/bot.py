import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation
from util.vec import Vec3

class GameObject():
    def __init__(self):
        self.location = Vec3([0,0,0])
        self.velocity = Vec3([0,0,0])
        self.rotation = Vec3([0,0,0])
        self.rvelocity = Vec3([0,0,0])
        
        self.local_location = Vec3([0,0,0])

class Car(GameObject):
    def __init__(self):
        super().__init__(self)
        self.me.matrix = [Vec3[0,0,0],Vec3[0,0,0],Vec3[0,0,0]]
        self.me.boost = 0.0
    

class Ball(GameObject):
    def __init__(self):
        super().__init__(self)

class MyBot(BaseAgent):

    def initialize_agent(self):
        # This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        self.me = Car()
        self.ball = Ball()

    def get_output(self, gamePacket: GameTickPacket) -> SimpleControllerState:
        ball_location = Vec3(gamePacket.game_ball.physics.location)

        my_car = gamePacket.game_cars[self.index]
        car_location = Vec3(my_car.physics.location)

        car_to_ball = ball_location - car_location

        # Find the direction of our car using the Orientation class
        car_orientation = Orientation(my_car.physics.rotation)
        car_direction = car_orientation.forward

        steer_correction_radians = find_correction(car_direction, car_to_ball)
        
        #calculate the car's next movement
        distance = math.sqrt(math.pow(car_to_ball.x, 2) + math.pow(car_to_ball.y, 2))      
        speed, turn = find_movement(steer_correction_radians, distance)
            
        self.controller_state.throttle = speed
        self.controller_state.steer = turn
        
        message = f"speed: {speed} | turn: {turn}"
        action_display = message

        draw_debug(self.renderer, my_car, gamePacket.game_ball, action_display)

        return self.controller_state
    
    def preprocess(self, gamePacket: GameTickPacket):
        #load data about self
        self.me.location = Vec3(gamePacket.game_cars[self.index].physics.location)
        self.me.velocity = Vec3(gamePacket.game_cars[self.index].physics.velocity)
        self.me.rotation = Vec3(gamePacket.game_cars[self.index].physics.rotation)
        self.me.rvelocity = Vec3(gamePacket.game_cars[self.index].physics.angular_velocity)
        self.me.matrix = build_rotator_matrix(self.me.rotation)
        self.me.boost = gamePacket.game_cars[self.index].boost
        
        #load data about the ball
        self.ball.location = Vec3(gamePacket.game_ball.physics.location)
        self.ball.velocity = Vec3(gamePacket.game_ball.physics.velocity)
        self.ball.rotation = Vec3(gamePacket.game_ball.physics.rotation)
        self.ball.rvelocity = Vec3(gamePacket.game_ball.physics.angular_velocity)
        
        self.ball.local_location = to_local(self.ball.location, self.me.location)

def to_local(target_vector: Vec3, home_vector: Vec3, matrix) -> Vec3:
    absolute_vector = target_vector - home_vector
    x = absolute_vector.dot(matrix[0])
    y = absolute_vector.dot(matrix[1])
    z = absolute_vector.dot(matrix[2])
    return Vec3(x,y,z)

def build_rotator_matrix(rotation: Vec3):
    CP = math.cos(rotation.x)
    SP = math.sin(rotation.x)
    CR = math.cos(rotation.y)
    SR = math.sin(rotation.y)
    CY = math.cos(rotation.z)
    SY = math.sin(rotation.z)

    matrix = []
    matrix.append(Vec3([CP*CY, CP*SY, SP]))
    matrix.append(Vec3([CY*SP*SR-CR*SY, SY*SP*SR+CR*CY, -CP * SR]))
    matrix.append(Vec3([-CR*CY*SP-SR*SY, -CR*SY*SP+SR*CY, CP*CR]))
    return matrix
    
    
def find_movement(angle: float, distance: float):
    #values are throttle, steer
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
    return speed, turn_rate

def find_correction(current: Vec3, ideal: Vec3) -> float:
    # Finds the angle from current to ideal vector in the xy-plane. Angle will be between -pi and +pi.

    # The in-game axes are left handed, so use -x
    current_in_radians = math.atan2(current.y, -current.x)
    ideal_in_radians = math.atan2(ideal.y, -ideal.x)

    diff = ideal_in_radians - current_in_radians

    # Make sure that diff is between -pi and +pi.
    if abs(diff) > math.pi:
        if diff < 0:
            diff += 2 * math.pi
        else:
            diff -= 2 * math.pi

    return diff


def draw_debug(renderer, car, ball, action_display):
    renderer.begin_rendering()
    # draw a line from the car to the ball
    renderer.draw_line_3d(car.physics.location, ball.physics.location, renderer.white())
    # print the action that the bot is taking
    renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())
    renderer.end_rendering()
