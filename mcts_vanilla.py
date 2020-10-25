from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 5.


def get_urgent_child(node, opponent):
    def get_UCT(node, node_child, opponent):
        # uses equation xj + sqrt((2 * ln(n)) / ni) where xj is the win rate of the current node, n is the current node's visits, and nj is the child node's visits
        # adversarial planning - if the bot is the opponent, the win rate is (1 - bot's win rate) = (1 - node.wins / node.visits)

        xj = node_child.wins / node_child.visits if not opponent else 1 - (node_child.wins / node_child.visits)  # maybe the opponent one should be the absolute value?
        return xj + (explore_faction * sqrt((2 * log(node.visits) / node_child.visits)))

    urgent_child = list(node.child_nodes.values())[0]
    ucb = get_UCT(node, urgent_child, opponent)

    for child in node.child_nodes.values():
        current_bound = get_UCT(node, child, opponent)
        if current_bound > ucb:
            ucb = current_bound
            urgent_child = child

    return urgent_child


def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    '''highest_child = node
    opponent = None

    while len(highest_child.child_nodes) != 0:
        urgent_child = highest_child.child_nodes[0]

        if board.current_player(state) == identity:
            opponent = 0
        else:
            opponent = 1

        upp_bound = (abs(opponent * urgent_child.visits - urgent_child.wins) / urgent_child.visit) + \
                    explore_faction * sqrt((2 * log * urgent_child.parent.visits) / urgent_child.visits)

        for child in highest_child.child_nodes:

            child_bound = (abs(opponent * child.visits - child.wins) / child.visits) + \
                          explore_faction * sqrt((2 * log * child.parent.visits) / child.visits)
            if (upp_bound < child_bound):
                urgent_child = child
                upp_bound = child_bound

        highest_child = urgent_child
        state = board.next_state(state, highest_child.parent_action)  # added fix here (state is reavaluated)

    return highest_child, state'''

    if node.untried_actions:  # still more actions to try
        return node, state
    elif not node.child_nodes:  # no children
        return node, state
    else:
        player = board.current_player(state)  # get current player
        urgent_child = get_urgent_child(node,
                                        False if player == identity else True)  # get the urgent child which is the next node to go to in the tree
        state = board.next_state(state, urgent_child.parent_action)  # update the board with the move that the node takes
        return traverse_nodes(urgent_child, board, state, identity)  # recursively call the function until we get to a end criterion is met

    # Hint: return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """

    if len(node.untried_actions) == 0:
        return node, state

    next_move = choice(node.untried_actions)  # makes a random move
    state = board.next_state(state, next_move)
    available_actions = board.legal_actions(state)

    new_child = MCTSNode(parent=node, parent_action=next_move, action_list=available_actions)

    node.untried_actions.remove(next_move)
    node.child_nodes[next_move] = new_child

    return new_child, state

    '''exp_move = choice(node.untried_actions)  # makes a random choice
    # declares a new node with that random node, and a new state
    new_child = MCTSNode(parent=node, parent_action=exp_move, action_list=board.legal_actions(board.next_state(state, exp_move)))

    # removes the random choice from tried choices
    # and declares at that index in child_nodes as the new node

    node.untried_actions.remove(exp_move)
    node.child_nodes[exp_move] = new_child

    #

    return new_child, board.next_state(state, exp_move)'''

    # Hint: return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """

    while not board.is_ended(state):
        next_move = choice(board.legal_actions(state))
        state = board.next_state(state, next_move)

    '''while not board.is_ended(state):
        rdm_choice = choice(board.legal_actions(state))  # makes a random choice while the board isn't in end condition
        outcome = board.next_state(state, rdm_choice)  # keeps reinitializing if it won or lost

    return outcome  # win or lost returned after board has ended (no more moves)'''

    return state


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """

    if node:
        node.visits += 1
        node.visits += int(won)
        backpropagate(node.parent, won)

    '''if (won == 0):
        while (node != None):
            node.visits = node.visits + 1
            node = node.parent
        return

    while (node != None):
        node.visits = node.visits + 1
        node.wins = node.wins + 1
        node = node.parent

    return'''

    pass


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
        current_node, sampled_game = traverse_nodes(node, board, sampled_game, identity_of_bot)

        next_node, sampled_game = expand_leaf(current_node, board, sampled_game)

        sampled_game = rollout(board, sampled_game)

        score = board.points_values(sampled_game)
        won = 1 if score[identity_of_bot] == 1 else 0
        backpropagate(next_node, won)

    # calculate which node to return
    next_node = choice(list(root_node.child_nodes.values()))
    max_winrate = 0

    for child in root_node.child_nodes.values():
        winrate = child.wins / child.visits

        if winrate > max_winrate:
            max_winrate = winrate
            next_node = child

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    return next_node.parent_action

    '''identity_of_bot = board.current_player(state)
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

        if (outcome[identity_of_bot] == 1):
            won = 1
        else:
            won = 0

        backpropagate(new_child, won)
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.'''

    return None
