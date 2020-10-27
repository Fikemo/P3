README

Team Members: Finn Morrison, Adrian Vasquez

Modifications:
In mcts_modified.py, we decided to use the provided rollout_bot.py script as a basis for the new rollout method.
The number of rollouts performed was changed to 3 and each rollout simulated new moves up to a depth of 2.
These smaller simulations would continue until the game reached its end and the branch that led to the greatest
estimate for win potential would be selected.