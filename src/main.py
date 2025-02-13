import arcade
import pickle


from matplotlib import pyplot as plt

from qlearning.qlearning_consts import FILE_AGENT
from robot_game import RobotGame



def main():
    window = RobotGame()
    window.setup()
    try:
        arcade.run()
    except KeyboardInterrupt:
        pass
    finally:
        with open(FILE_AGENT, 'wb') as f:
            pickle.dump(window.qtable.dic, f)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        ax1.plot(window.episode_rewards, label='Episode Reward')
        ax1.set_title('Training Progress')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Total Reward')
        ax1.grid(True)
        ax1.legend()
        
        plt.tight_layout()
        if window.manual_control is False:
            plt.show()


if __name__ == "__main__":
    main()