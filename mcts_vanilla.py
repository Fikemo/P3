
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    highest_child = node
    opponent = None

    while(len(highest_child.child_nodes) != 0):
        urgent_child = highest_child.child_nodes[0]

        
        if(board.current_player(state) == identity):
            opponent = 0
        else:
            opponent = 1

        upp_bound = (abs(opponent*urgent_child.visits - urgent_child.wins)/urgent_child.visit) + \
            explore_faction*sqrt((2*log * urgent_child.parent.visits) / urgent_child.visits)

        for child in highest_child.child_nodes:

            child_bound = (abs(opponent*child.visits - child.wins)/child.visits) + \
                explore_faction*sqrt((2*log * child.parent.visits) / child.visits)
            if(upp_bound < child_bound):
                
                urgent_child = child
                upp_bound = child_bound
        
        highest_child = urgent_child
        state = board.next_state(state, highest_child.parent_action)    #added fix here (state is reavaluated)


    return highest_child, state


    # Hint: return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    exp_move = choice(node.untried_actions) #makes a random choice
    #declares a new node with that random node, and a new state
    new_child = MCTSNode(parent=node, parent_action = exp_move, \
        action_list=board.legal_actions(board.next_state(state, exp_move)))

    #removes the random choice from tried choices
    #and declares at that index in child_nodes as the new node

    node.untried_actions.remove(exp_move)
    node.child_nodes[exp_move] = new_child

    #

    return new_child, board.next_state(state, exp_move)

    # Hint: return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    while(not board.is_ended(state)):
        rdm_choice = choice(board.legal_actions(state)) #makes a random choice while the board isnt in end condition
        outcome = board.next_state(state, rdm_choice)   #keeps reanitializing if it won or lost

    return outcome  #win or lost returned after board has ended (no more moves)


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    if(won == 0):
        while(node != None):
            node.visits = node.visits + 1
            node = node.parent
        return
    
    while(node != None):
        node.visits = node.visits + 1
        node.wins = node.wins + 1
        node = node.parent

    return


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!

        curr_node, sampled_game = traverse_nodes(node, board, sampled_game, identity_of_bot)
        new_child, sampled_game = expand_leaf(curr_node, board, sampled_game)
        sampled_game = rollout(board, sampled_game)

        outcome = board.points_values(sampled_game)

        if(outcome[identity_of_bot]==1):
            won = 1
        else:
            won = 0
        
        backpropagate(new_child, won)
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.



    return None
