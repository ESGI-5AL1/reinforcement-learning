import random

JUMP = "JUMP"
LEFT = "LEFT"
RIGHT = "RIGHT"
JUMP_RIGHT = "JUMP_RIGHT"
JUMP_LEFT = "JUMP_LEFT"
ACTIONS = [LEFT, RIGHT, JUMP, JUMP_RIGHT, JUMP_LEFT]

class QTable:
    def __init__(self, learning_rate=0.1, discount_factor=2):
        self.dic = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    def set(self, state, action, reward, new_state):
        if state not in self.dic:
            self.dic[state] = {a: 0 for a in ACTIONS}
        if new_state not in self.dic:
            self.dic[new_state] = {a: 0 for a in ACTIONS}

        # Q(s, a) = Q(s, a) + alpha * [reward + gamma * max(S', a) - Q(s, a)]
        delta = reward + self.discount_factor * max(self.dic[new_state].values()) - self.dic[state][action]
        self.dic[state][action] += self.learning_rate * delta

    def best_action(self, state):
        if state in self.dic:
            return max(self.dic[state], key=self.dic[state].get)
        else:
            return random.choice(ACTIONS)

    def print_rewards(self):

        for state, actions in self.dic.items():
            print(f"State: {state}")
            for action, value in actions.items():
                print(f"  Action: {action}, Value: {value}")

    def clear(self):
        self.dic = {}
