import math

from util.vec import Vec3

"""Field Dimensions"""
FIELD_LENGTH = 10240 #uu
FIELD_WIDTH = 8192 #uu
FIELD_HEIGHT = 2044 #uu

"""Goal Dimensions"""
GOAL_WIDTH = 1786 #uu
GOAL_HEIGHT = 643 #uu
GOAL_HEIGHT_EXACT = 642.775 #uu

"""Boost Pad Measurements"""
BOOST_HEIGHT_SMALL = 165 #uu
BOOST_RADIUS_SMALL = 144 #uu
BOOST_AMOUNT_SMALL = 12
BOOST_HEIGHT_LARGE = 168 #uu
BOOST_RADIUS_LARGE = 208 #uu
BOOST_AMOUNT_LARGE = 100

"""Physics Measurements"""
ACCELERATION_GRAVITY = 650 #uu/s^2
ACCELERATION_BOOST = 991.66 #uu/s^2
ACCELERATION_BRAKE = -3500 #uu/s^2
ACCELERATION_COAST = -525 #uu/s^2

"""Car Measurements"""
MAX_SPEED_CAR = 2300 #uu/s
SUPERSONIC = 2200 #uu/s
FULL_SPEED_CAR = 1400 #uu/s
MASS_CAR = 180 #arbitrary units
BOOST_CONSUMPTION_RATE = 33.3 #boost/s
JUMP_VELOCITY = 300 #uu/s instantaneous increase
JUMP_MAX_DURATION = 200 #ms
JUMP_VELOCITY_ACCELERATION = 1400 #uu/s^2 during duration of jump
BOOST+MAX_AMOUNT = 100
BOOST_START_AMOUNT = 33.3

"""Ball Measurements"""
BALL_RADIUS_EXACT = 92.75 #uu
BALL_RADIUS = 93 #uu
BALL_RESTITUTION_COEFFIECIENT = 0.6

def predict_ball_path(agent):
    """Predicts the path of the ball using the rlBot framework
    
    Args:
        agent (BaseAgent): The bot
        
    Returns:
        An array of Vec3 containing the predicted locations of the ball. Each location is seperated in time by
        1/60 of a second, or one game tick.
    """
    locations = []
    
    ball_prediction = agent.get_ball_prediction_struct()
    if ball_prediction is not None:
        for i in range(0, ball_prediction.num_slices):
            prediction_slice = ball_prediction.slices[i]
            locations.append(prediction_slice.physics.location)
    
    return locations

def turn_radius(velocity):
    """Calculates the turn radius of a car given a speed
    
    Values come from the RLBot wiki.
    
    Args:
        v (float): magnitude of the car's velocity
        
    Returns:
        float: the tightest radius the car can turn at given the velocity.
    
    """
    if velocity == 0:
        return 0
    return 1.0 / turn_radius_helper(velocity)

def turn_radius_helper(v):
    """Helper function for turn_radius"""
    if 0.0 <= v < 500.0:
        return 0.006900 - 5.84e-6 * v
    elif 500.0 <= v < 1000.0:
        return 0.005610 - 3.26e-6 * v
    elif 1000.0 <= v < 1500.0:
        return 0.004300 - 1.95e-6 * v
    elif 1500.0 <= v < 1750.0:
        return 0.003025 - 1.10e-6 * v
    elif 1750.0 <= v < 2500.0:
        return 0.001800 - 0.40e-6 * v
    else:
        return 0.0


    