import random

JUMP = "JUMP"
LEFT = "LEFT"
RIGHT = "RIGHT"
JUMP_RIGHT = "JUMP_RIGHT"
JUMP_LEFT = "JUMP_LEFT"
ACTIONS = [LEFT, RIGHT, JUMP, JUMP_RIGHT, JUMP_LEFT]

class QTable:
    def __init__(self, learning_rate=0.1, discount_factor=0.8):
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


    #ici ajouter cas ennemis, tire si ennemis mort bonus, sinon penalité
    
    def choose_action(self, state):
        if state not in self.dic:
            return random.choice(ACTIONS)

        if random.random() < 0.1:
            return random.choice(ACTIONS)

        actions_values = self.dic[state]
        max_value = max(actions_values.values())
        best_actions = [action for action, value in actions_values.items() if value == max_value]

        return random.choice(best_actions)

        
    def print_rewards(self):

        for state, actions in self.dic.items():
            print(f"State: {state}")
            for action, value in actions.items():
                print(f"  Action: {action}, Value: {value}")

    def print_qtable(self):
        print("--- Q-Table Summary ---")
        print(f"Total States: {len(self.dic)}")
        
        if not self.dic:
            print("Q-Table is empty")
            return
        
        sorted_states = sorted(self.dic.items(), key=lambda x: max(x[1].values()), reverse=True)
        
        for state, actions in sorted_states[:10]:  # Print top 10 states
            print(f"\nState: {state}")
            sorted_actions = sorted(actions.items(), key=lambda x: x[1], reverse=True)
            for action, value in sorted_actions:
                print(f"  {action}: {value:.2f}")
        

    def clear(self):
        self.dic = {}
