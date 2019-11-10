import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation
from util.vec import Vec3

class MyBot(BaseAgent):

    def initialize_agent(self):
        # This runs once before the bot starts up
        self.controller_state = SimpleControllerState()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        ball_location = Vec3(packet.game_ball.physics.location)

        my_car = packet.game_cars[self.index]
        car_location = Vec3(my_car.physics.location)

        car_to_ball = ball_location - car_location

        # Find the direction of our car using the Orientation class
        car_orientation = Orientation(my_car.physics.rotation)
        car_direction = car_orientation.forward

        steer_correction_radians = find_correction(car_direction, car_to_ball)
        
        #calculate the amount of turning to do to face the ball
        distance = math.sqrt(math.pow(car_to_ball.x, 2) + math.pow(car_to_ball.y, 2))
        #turn = find_turn(steer_correction_radians)
        #speed = find_speed(steer_correction_radians, distance)
        
        speed, turn = find_movement(steer_correction_radians, distance)
            
        self.controller_state.throttle = speed
        self.controller_state.steer = turn
        
        message = f"speed: {speed} | turn: {turn}"
        action_display = message

        draw_debug(self.renderer, my_car, packet.game_ball, action_display)

        return self.controller_state
    
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

def find_turn(angle: float) -> float:
    if angle > math.pi / 12:
        turnRate = -1.0
    elif angle < -math.pi / 12:
        turnRate = 1.0
    else:
        turnRate = 0
        
    return turnRate

def find_speed(angle:float, distance: float) -> float:
    return 1.0

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
