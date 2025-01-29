import arcade
import random
import pickle
import os

from matplotlib import pyplot as plt

from utils import place_multi_planet_tiles, crates_coordinate_list

# Original game constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
WORLD_WIDTH = 3000
SCREEN_TITLE = "MR ROBOT Q-LEARNING"

CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

# Q-Learning constants
ACTIONS = ['IDLE', 'LEFT', 'RIGHT', 'JUMP', 'JUMP_LEFT', 'JUMP_RIGHT']
REWARD_GOAL = 1000
REWARD_DEFAULT = -1
REWARD_FALL = -100

FILE_AGENT = 'robot_qtable.pkl'


class QTable:
    def __init__(self, learning_rate=0.2, discount_factor=0.99):
        self.dic = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    @staticmethod
    def get_state_key(x, y, can_jump):
        # Discretize the state space to make it manageable
        x_discrete = int(x / 32)
        y_discrete = int(y / 32)
        return x_discrete, y_discrete, can_jump

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


class QlearningGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.set_update_rate(1/10000)
        # Game attributes
        self.previous_distance = 0
        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = arcade.Camera(self.width, self.height)
        self.spawn_x = 64
        self.spawn_y = 128

        # Q-learning attributes
        self.qtable = QTable()
        self.current_state = None
        self.exploration_rate = 0.75
        self.episode_steps = 0
        self.max_steps = 2000
        self.episodes = 0
        self.total_reward = 0

        # Training history
        self.episode_rewards = []
        self.episode_steps_history = []

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        # Load Q-table if exists
        if os.path.exists(FILE_AGENT):
            with open(FILE_AGENT, 'rb') as f:
                self.qtable.dic = pickle.load(f)

    def setup(self):
        self.camera = arcade.Camera(self.width, self.height)
        self.scene = arcade.Scene()

        # Setup player
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/robot/robot_idle.png",
            CHARACTER_SCALING
        )
        self.player_sprite.center_x = self.spawn_x
        self.player_sprite.center_y = self.spawn_y
        self.scene.add_sprite("Player", self.player_sprite)

        # Setup environment
        place_multi_planet_tiles(self, 0, 2000, 64, ":resources:images/tiles/planet.png", TILE_SCALING, 32)
        place_multi_planet_tiles(self, 1000, 1300, 64, ":resources:images/tiles/planet.png", TILE_SCALING, 450)
        place_multi_planet_tiles(self, 1000, 1400, 64, ":resources:images/tiles/planet.png", TILE_SCALING, 200)
        place_multi_planet_tiles(self, 1528, 1700, 64, ":resources:images/tiles/planet.png", TILE_SCALING, 300)

        for coordinate in crates_coordinate_list:
            wall = arcade.Sprite(":resources:images/tiles/brickGrey.png", TILE_SCALING)
            wall.position = coordinate
            self.scene.add_sprite("Walls", wall)

        green_flag = arcade.Sprite(":resources:images/items/flagGreen2.png", COIN_SCALING)
        green_flag.center_x = 1900
        green_flag.center_y = 96
        self.scene.add_sprite("Flag", green_flag)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Walls"]
        )

        self.current_state = self.qtable.get_state_key(
            self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.physics_engine.can_jump()
        )

    def get_reward(self):
        # Get flag position
        flag_sprite = self.scene["Flag"][0]
        flag_position = (flag_sprite.center_x, flag_sprite.center_y)

        # Calculate distance to goal
        current_distance = ((self.player_sprite.center_x - flag_position[0]) ** 2 +
                            (self.player_sprite.center_y - flag_position[1]) ** 2) ** 0.5

        # Check if reached flag
        flag_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Flag"]
        )
        if flag_hit_list:
            return REWARD_GOAL

        # Check if fell off
        if self.player_sprite.center_y < 0:
            return REWARD_FALL

        # Progressive reward based on distance to goal
        if hasattr(self, 'previous_distance'):
            distance_reward = self.previous_distance - current_distance
            self.previous_distance = current_distance
            return distance_reward * 5  # Scale the reward to make it more significant

        self.previous_distance = current_distance
        return REWARD_DEFAULT

    def execute_action(self, action):
        # Maintain horizontal momentum instead of resetting to 0
        current_x_speed = self.player_sprite.change_x

        # Apply horizontal movement with smooth acceleration
        if action in ['LEFT', 'JUMP_LEFT']:
            target_speed = -PLAYER_MOVEMENT_SPEED
            self.player_sprite.change_x = max(target_speed, current_x_speed - 0.5)
        elif action in ['RIGHT', 'JUMP_RIGHT']:
            target_speed = PLAYER_MOVEMENT_SPEED
            self.player_sprite.change_x = min(target_speed, current_x_speed + 0.5)
        else:
            # Gradually slow down when no horizontal input
            if abs(current_x_speed) < 0.5:
                self.player_sprite.change_x = 0
            elif current_x_speed > 0:
                self.player_sprite.change_x = current_x_speed - 0.5
            else:
                self.player_sprite.change_x = current_x_speed + 0.5

        # Handle jumping
        if 'JUMP' in action and self.physics_engine.can_jump():
            self.player_sprite.change_y = PLAYER_JUMP_SPEED

    def reset_episode(self):
        # Save episode data only if it's not the first episode
        if self.episode_steps > 0:  # Make sure we don't record empty episodes
            self.episode_rewards.append(self.total_reward)
            self.episode_steps_history.append(self.episode_steps)
            print(f"Saved metrics - Total Reward: {self.total_reward}, Steps: {self.episode_steps}")

        self.player_sprite.center_x = self.spawn_x
        self.player_sprite.center_y = self.spawn_y
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0
        self.episode_steps = 0
        self.total_reward = 0
        self.episodes += 1
        self.current_state = self.qtable.get_state_key(
            self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.physics_engine.can_jump()
        )


    def on_update(self, delta_time):
        # Update less frequently to give actions time to complete

        current_state = self.qtable.get_state_key(
            self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.physics_engine.can_jump()
        )

        # Choose and execute action
        action = self.qtable.best_action(current_state, self.exploration_rate)
        self.execute_action(action)

        # Update physics every frame for smooth movement
        self.physics_engine.update()

        # Get new state and reward
        new_state = self.qtable.get_state_key(
            self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.physics_engine.can_jump()
        )
        reward = self.get_reward()

        # Update Q-table
        self.qtable.set(current_state, action, reward, new_state)
        self.total_reward += reward
        self.episode_steps += 1

        # Check if episode should end
        if reward == REWARD_GOAL:
            self.exploration_rate *= 0.95
            self.reset_episode()
        elif reward == REWARD_FALL or self.episode_steps >= self.max_steps:
            self.reset_episode()

            # Save Q-table periodically
            if self.episodes % 100 == 0:
                with open(FILE_AGENT, 'wb') as f:
                    pickle.dump(self.qtable.dic, f)

        self.center_camera_to_player()
    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)
        self.camera.move_to((max(screen_center_x, 0), max(screen_center_y, 0)))

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()

        # Draw training info
        arcade.draw_text(
            f"Episode: {self.episodes} Steps: {self.episode_steps} "
            f"Exploration: {self.exploration_rate:.2f} Reward: {self.total_reward}",
            10, 10, arcade.color.WHITE, 14
        )


def main():
    window = QlearningGame()
    window.setup()

    try:
        arcade.run()
    except KeyboardInterrupt:
        pass
    finally:
        # Save Q-table
        with open(FILE_AGENT, 'wb') as f:
            pickle.dump(window.qtable.dic, f)

        # Plot training metrics
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # Plot rewards
        ax1.plot(window.episode_rewards, label='Episode Reward')
        ax1.set_title('Training Progress')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Total Reward')
        ax1.grid(True)
        ax1.legend()

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()