from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.


def get_urgent_child(node, opponent):
    def get_UCT(node, node_child, opponent):
        # uses equation xj + sqrt((2 * ln(n)) / ni) where xj is the win rate of the current node, n is the current node's visits, and nj is the child node's visits
        # adversarial planning - if the bot is the opponent, the win rate is (1 - bot's win rate) = (1 - node.wins / node.visits)

        xj = node_child.wins / node_child.visits if not opponent else 1 - (node_child.wins / node_child.visits)

        return xj + (explore_faction * sqrt((2 * log(node.visits) / node_child.visits)))

    prev_bound = 0
    urgent_child = choice(list(node.child_nodes.values()))

    for child in node.child_nodes.values():
        current_bound = get_UCT(node, child, opponent)
        if current_bound > prev_bound:
            prev_bound = current_bound
            urgent_child = child

    return urgent_child


def traverse_nodes(node, board, state, identity):

    if node.untried_actions:  # still more actions to try
        return node, state
    if not node.child_nodes:  # no children
        return node, state
    else:
        player = board.current_player(state)  # get current player
        urgent_child = get_urgent_child(node, False if player == identity else True)  # get the urgent child which is the next node to go to in the tree
        state = board.next_state(state, urgent_child.parent_action)  # update the board with the move that the node takes
        return traverse_nodes(urgent_child, board, state, identity)  # recursively call the function until we get to a end criterion is met

    #Hint: return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    if not node.untried_actions:
        if not node.child_nodes:
            return node, state
        else:
            print("error: node was traversed to without untried actions, but with child nodes")


    exp_move = choice(node.untried_actions)  # makes a random choice
    # declares a new node with that random node, and a new state
    state = board.next_state(state, exp_move)
    new_child = MCTSNode(parent=node, parent_action=exp_move, \
                         action_list=board.legal_actions(board.next_state(state, exp_move)))

    # removes the random choice from tried choices
    # and declares at that index in child_nodes as the new node

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

    while not board.is_ended(state):
        rdm_choice = choice(board.legal_actions(state))  # makes a random choice while the board isnt in end condition
        state = board.next_state(state, rdm_choice)  # keeps reanitializing if it won or lost

    return state  # win or lost returned after board has ended (no more moves)


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    '''if won == 0:
        while node != None:
            node.visits = node.visits + 1
            node = node.parent
        return

    while node != None:
        node.visits = node.visits + 1
        node.wins = node.wins + 1
        node = node.parent'''

    if node:
        node.visits += 1
        node.wins += won
        backpropagate(node.parent, won)

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

        '''if board.points_values(sampled_game) == 1:
            won = 1
        else:
            won = 0'''

        won = board.points_values(sampled_game)[identity_of_bot]

        backpropagate(new_child, won)
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.

    best_winrate = 0
    rdm_node = choice(list(root_node.child_nodes.values()))

    for child in root_node.child_nodes.values():
        winrate = child.wins / child.visits
        if winrate > best_winrate:
            best_winrate = winrate
            rdm_node = child

    return rdm_node.parent_action

