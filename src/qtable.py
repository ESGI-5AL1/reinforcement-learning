import random

JUMP = "JUMP"
LEFT = "LEFT"
RIGHT = "RIGHT"
JUMP_RIGHT = "JUMP_RIGHT" 
JUMP_LEFT = "JUMP_LEFT"
SHOOT = "SHOOT"
ACTIONS = [JUMP, LEFT, RIGHT, JUMP_RIGHT, JUMP_LEFT, SHOOT]

REPLAY_MEMORY_SIZE = 10000  # Size of experience replay buffer
BATCH_SIZE = 32            # Number of experiences to learn from each update
LEARNING_RATE = 0.5        # How quickly to update Q-values
DISCOUNT_FACTOR = 0.8      # How much to value future rewards
EPSILON_START = 1.0        # Initial exploration rate
EPSILON_DECAY = 0.995      # How quickly to reduce exploration
EPSILON_MIN = 0.01        # Minimum exploration rate

rewards = {
    # Existing rewards
    "basic_action": -1,
    "enemy_collision": -100,
    "flag_collision": +3000,
    "coin_collision": +20,
    "wall_collision": -10,
    "time_is_up": -200,

    # Action-specific costs
    "action_costs": {
        "JUMP": -2,        # More costly since it's a powerful vertical move
        "LEFT": -1,        # Basic movement cost
        "RIGHT": -1,       # Basic movement cost
        "JUMP_RIGHT": -3,  # Costly since it's a powerful diagonal move
        "JUMP_LEFT": -3,   # Costly since it's a powerful diagonal move
        "SHOOT": -5        # Most costly since it's an attack action
    }
}

class QTable:
    def __init__(self, learning_rate=0.5, discount_factor=0.8, epsilon_start=1.0,
                 epsilon_decay=0.995, epsilon_min=0.01, batch_size=32):
        print("QTable initialized")
        self.dic = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon_start
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.replay_memory = ExperienceReplay(batch_size=batch_size)

        if not hasattr(self, 'epsilon'):
            self.epsilon = epsilon_start

    def set(self, state, action, reward, next_state, done=False):
        """Add experience to replay memory and perform batch learning."""
        # Add new experience to replay memory
        self.replay_memory.add_experience(state, action, reward, next_state, done)
        
        # Ensure state-action pairs exist in Q-table
        if state not in self.dic:
            self.dic[state] = {a: 0 for a in ACTIONS}
        if next_state not in self.dic:
            self.dic[next_state] = {a: 0 for a in ACTIONS}
            
        # Update Q-value for current state-action pair
        next_max = 0 if done else max(self.dic[next_state].values())
        delta = reward + self.discount_factor * next_max - self.dic[state][action]
        self.dic[state][action] += self.learning_rate * delta
        
        # Perform batch learning if enough experiences are available
        self._learn_from_batch()


    def _learn_from_batch(self):
        """Learn from a batch of experiences."""
        batch = self.replay_memory.sample_batch()
        if batch is None:
            return
            
        for state, action, reward, next_state, done in batch:
            # Ensure states exist in Q-table
            if state not in self.dic:
                self.dic[state] = {a: 0 for a in ACTIONS}
            if next_state not in self.dic:
                self.dic[next_state] = {a: 0 for a in ACTIONS}
                
            # Q-learning update
            next_max = 0 if done else max(self.dic[next_state].values())
            delta = reward + self.discount_factor * next_max - self.dic[state][action]
            self.dic[state][action] += self.learning_rate * delta

    def choose_action(self, state):
        """Choose action using epsilon-greedy policy."""
        if state not in self.dic:
            self.dic[state] = {a: 0 for a in ACTIONS}
            
        if random.random() < self.epsilon:
            action = random.choice(ACTIONS)
        else:
            actions_values = self.dic[state]
            max_value = max(actions_values.values())
            best_actions = [action for action, value in actions_values.items() 
                          if value == max_value]
            action = random.choice(best_actions)
            
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        return action
    

    def print_training_stats(self):
            """Print training statistics."""
            print(f"\nTraining Statistics:")
            print(f"Memory Size: {len(self.replay_memory)}")
            print(f"Current Epsilon: {self.epsilon:.4f}")
            print(f"Number of Known States: {len(self.dic)}")
            
            if self.dic:
                max_q = max(max(actions.values()) for actions in self.dic.values())
                min_q = min(min(actions.values()) for actions in self.dic.values())
                print(f"Q-value range: [{min_q:.2f}, {max_q:.2f}]")
    
    def clear(self):
        self.dic = {}


from collections import deque


class ExperienceReplay:
    def __init__(self, max_size=10000, batch_size=32):
        self.memory = deque(maxlen=max_size)
        self.batch_size = batch_size

    def add_experience(self, state, action, reward, next_state, done):
        """Add a new experience to memory."""
        self.memory.append((state, action, reward, next_state, done))
        
    def sample_batch(self):
        """Sample a random batch of experiences."""
        if len(self.memory) < self.batch_size:
            return None
        return random.sample(self.memory, self.batch_size)

    def __len__(self):
        return len(self.memory)