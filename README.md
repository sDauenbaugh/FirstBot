# FirstBot

FirstBot is designed by Sam Dauenbaugh
Bot behaviors will be documented in this file for future reference

# Behaviors

The bot's top priority is to defend when the ball is on it's own side of the field. This is done by moving to the goal, then hitting the ball away when it comes close.

When the ball is on the opponent's side FirstBot will attempt to move toward the ball. If FirstBot manages to get the ball between itself and the goal, it will attempt to shoot the ball. Otherwise it will continue to push the ball around until the defense or shot states can be used.
