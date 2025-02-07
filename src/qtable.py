import random
from consts import ACTIONS
#  remettre l'exploration a zero lors de la
class QTable:
    def __init__(self, learning_rate=0.2, discount_factor=0.99):
        self.dic = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    @staticmethod
    def get_state_key(x, y, can_jump, radar_state):
        x_discrete = int(x / 256)
        y_discrete = int(y / 128)
        return (x_discrete, y_discrete, can_jump) + radar_state

    def set(self, state, action, reward, new_state):
        if state not in self.dic:
            self.dic[state] = {action: 0 for action in ACTIONS}
        if new_state not in self.dic:
            self.dic[new_state] = {action: 0 for action in ACTIONS}

        # Q-learning update formula
        current_q = self.dic[state][action]
        next_max_q = max(self.dic[new_state].values())
        self.dic[state][action] = current_q + self.learning_rate * (
                reward + self.discount_factor * next_max_q - current_q
        )

    def best_action(self, state, exploration_rate=0):
        if state not in self.dic or random.random() < exploration_rate:
            return random.choice(ACTIONS)
        return max(self.dic[state].items(), key=lambda x: x[1])[0]
