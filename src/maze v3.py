from random import choice, random
import arcade
import os
import pickle
import matplotlib.pyplot as plt

MAZE = """
?..x....
....xxx.
xxx.....
....x.xx
..xxx.x.
....x...
....x.x.
......x!
"""

FILE_AGENT = 'mouse.qtable'

TILE_WALL = 'x'

ACTION_UP = 'U'
ACTION_DOWN = 'D'
ACTION_LEFT = 'L'
ACTION_RIGHT = 'R'
ACTIONS = [ACTION_UP, ACTION_DOWN, ACTION_LEFT, ACTION_RIGHT]
REWARD_OUT = -100
REWARD_WALL = -100
REWARD_GOAL = 1000
REWARD_DEFAULT = -1

SPRITE_SIZE = 64

MOVES = {
    ACTION_UP: (-1, 0),
    ACTION_DOWN: (1, 0),
    ACTION_LEFT: (0, -1),
    ACTION_RIGHT: (0, 1)
}

def arg_max(table):
    return max(table, key=table.get)

class QTable:
    def __init__(self, learning_rate=0.9, discount_factor=0.9):
        self.dic = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    def set(self, state, action, reward, new_state):
        if state not in self.dic:
            self.dic[state] = {ACTION_UP: 0, ACTION_DOWN: 0, ACTION_LEFT: 0, ACTION_RIGHT: 0}
        if new_state not in self.dic:
            self.dic[new_state] = {ACTION_UP: 0, ACTION_DOWN: 0, ACTION_LEFT: 0, ACTION_RIGHT: 0}

        delta = reward + self.discount_factor * max(self.dic[new_state].values()) - self.dic[state][action]
        self.dic[state][action] += self.learning_rate * delta

    def best_action(self, position):
        if position in self.dic:
            return arg_max(self.dic[position])
        else:
            return choice(ACTIONS)

    def __repr__(self):
        res = ' ' * 11
        for action in ACTIONS:
            res += f'{action:5s}'
        res += '\r\n'
        for state in self.dic:
            res += str(state) + " "
            for action in self.dic[state]:
                res += f"{self.dic[state][action]:5d}"
            res += '\r\n'
        return res

class Agent:
    def __init__(self, env):
        self.env = env
        self.history = []
        self.score = None
        self.reset()
        self.qtable = QTable()
        self.exploration = 0

    def reset(self):
        if self.score is not None:
            self.history.append(self.score)
        self.position = env.start
        self.score = 0

    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump((self.qtable.dic, self.history), file)

    def load(self, filename):
        with open(filename, 'rb') as file:
            self.qtable.dic, self.history = pickle.load(file)

    def do(self, action=None):
        if not action:
            action = self.best_action()

        new_position, reward = self.env.move(self.position, action)
        self.qtable.set(self.position, action, reward, new_position)
        self.position = new_position
        self.score += reward

        return action, reward

    def best_action(self):
        if random() < self.exploration:
            self.exploration *= 0.999
            return choice(ACTIONS)
        else:
            return self.qtable.best_action(self.position)

    def detect_surroundings(self):
        surroundings = {}
        for action, move in MOVES.items():
            new_position = (self.position[0] + move[0], self.position[1] + move[1])
            if new_position in self.env.maze:
                surroundings[action] = self.env.maze[new_position]
            else:
                surroundings[action] = "OUT"  # Indique hors de la grille
        return surroundings

    def __repr__(self):
        return f"{self.position} score:{self.score} exploration:{self.exploration}"

class Environment:
    def __init__(self, text):
        rows = text.strip().split('\n')
        self.height = len(rows)
        self.width = len(rows[0])
        self.maze = {}
        for i in range(len(rows)):
            for j in range(len(rows[i])):
                self.maze[(i, j)] = rows[i][j]
                if rows[i][j] == '?':
                    self.start = (i, j)
                elif rows[i][j] == '!':
                    self.goal = (i, j)

    def move(self, position, action):
        move = MOVES[action]
        new_position = (position[0] + move[0], position[1] + move[1])

        if new_position not in self.maze:
            reward = REWARD_OUT
        elif self.maze[new_position] in [TILE_WALL]:
            reward = REWARD_WALL
        elif self.maze[new_position] == '!':
            reward = REWARD_GOAL
            position = new_position
        else:
            reward = REWARD_DEFAULT
            position = new_position

        return position, reward

class MazeWindow(arcade.Window):
    def __init__(self, agent):
        super().__init__(SPRITE_SIZE * env.width, SPRITE_SIZE * env.height, "Maze with Q-Learning")
        self.agent = agent
        self.env = agent.env
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        self.walls = arcade.SpriteList()
        for state in env.maze:
            if env.maze[state] == TILE_WALL:
                sprite = self.create_sprite(':resources:images/tiles/boxCrate_double.png', state)
                self.walls.append(sprite)

        self.goal = self.create_sprite(':resources:images/tiles/signExit.png', env.goal)
        self.player = self.create_sprite(':resources:images/enemies/mouse.png', agent.position)

    def create_sprite(self, resource, state):
        sprite = arcade.Sprite(resource, 0.5)
        sprite.center_x, sprite.center_y = (state[1] + 0.5) * SPRITE_SIZE, (env.height - state[0] - 0.5) * SPRITE_SIZE
        return sprite

    def on_draw(self):
        arcade.start_render()
        self.walls.draw()
        self.goal.draw()
        self.player.draw()

        # Afficher le score et l'exploration
        arcade.draw_text(f'{self.agent}', 10, 10, arcade.csscolor.WHITE, 20)

        # Afficher les informations de radar
        surroundings = self.agent.detect_surroundings()
        radar_text = "Radar: "
        for direction, value in surroundings.items():
            radar_text += f"{direction}: {value}  "
        arcade.draw_text(radar_text, 10, 40, arcade.csscolor.WHITE, 20)

    def on_update(self, delta_time):
        if self.agent.position == self.env.goal:
            print("L'agent a atteint l'objectif.")

            # Sauvegarder la Q-Table
            self.agent.save(FILE_AGENT)
            print("La Q-Table a été sauvegardée dans le fichier mouse.qtable.")

            # Afficher un menu pour l'utilisateur
            while True:
                print("\n=== MENU ===")
                print("1. Afficher la Q-Table")
                print("2. Continuer l'apprentissage")
                print("3. Quitter")
                choice = input("Votre choix : ")

                if choice == "1":
                    try:
                        with open(FILE_AGENT, 'rb') as file:
                            qtable_data, history = pickle.load(file)

                            print("\n=== Q-Table ===")
                            for state, actions in qtable_data.items():
                                print(f"State {state}: {actions}")

                            print("\n=== Historique des Scores ===")
                            print(history)

                            plt.plot(history)
                            plt.title("Évolution des scores")
                            plt.xlabel("Parties")
                            plt.ylabel("Scores")
                            plt.show()
                    except FileNotFoundError:
                        print("Erreur : Le fichier mouse.qtable n'existe pas.")
                elif choice == "2":
                    print("Continuer l'apprentissage...")
                    self.agent.reset()
                    self.player.center_x, self.player.center_y = (
                        (self.agent.position[1] + 0.5) * SPRITE_SIZE,
                        (self.env.height - self.agent.position[0] - 0.5) * SPRITE_SIZE
                    )
                    break
                elif choice == "3":
                    print("Programme terminé.")
                    arcade.close_window()
                    exit()
                else:
                    print("Choix invalide. Veuillez réessayer.")
        else:
            self.agent.do()
            self.player.center_x, self.player.center_y = (
                (self.agent.position[1] + 0.5) * SPRITE_SIZE,
                (env.height - self.agent.position[0] - 0.5) * SPRITE_SIZE
            )

if __name__ == "__main__":
    env = Environment(MAZE)
    agent = Agent(env)

    if os.path.exists(FILE_AGENT):
        agent.load(FILE_AGENT)

    window = MazeWindow(agent)
    window.setup()
    arcade.run()
