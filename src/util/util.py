import math

from util.vec import Vec3

def predict_ball_path(agent):
    locations = []
    
    ball_prediction = agent.get_ball_prediction_struct()
    if ball_prediction is not None:
        for i in range(0, ball_prediction.num_slices):
            prediction_slice = ball_prediction.slices[i]
            locations.append(prediction_slice.physics.location)
    
    return locations