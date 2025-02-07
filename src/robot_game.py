import time
import arcade
import pickle
import os

from matplotlib import pyplot as plt

from qlearning.qlearning_consts import *
from enemy import Enemy
from qlearning.qtable import QTable
from map_setup.map_setup import *
from radar_utils import compute_checkpoint_position, compute_ennemy_position, compute_flag_positon



class RobotGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.set_update_rate(1/1000000)
        self.previous_distance = 0
        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = arcade.Camera(self.width, self.height)
        self.spawn_x = 64
        self.spawn_y = 128
        self.enemy_list = None

        self.qtable = QTable()
        self.current_state = None
        self.exploration_rate = EXPLORATION_RATE
        self.episode_steps = 0
        self.episodes = 0
        self.total_reward = 0

        self.episode_rewards = []
        self.episode_steps_history = []

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        if os.path.exists(FILE_AGENT):
            with open(FILE_AGENT, 'rb') as f:
                self.qtable.dic = pickle.load(f)


    def setup(self):
        self.camera = arcade.Camera(self.width, self.height)
        self.scene = arcade.Scene()
        self.player_sprite = setup_player(self, self.spawn_x, self.spawn_y)
        setup_enemies(self)
        setup_plateformes(self)
        setup_flag(self)
        setup_plateformes(self)
        setup_walls(self)
        setup_flag(self)
        setup_physics(self)
        setup_coins(self)
    


    def get_reward(self):
        if arcade.check_for_collision_with_list(self.player_sprite, self.scene["Flag"]):
            return REWARD_GOAL
        
        if arcade.check_for_collision_with_list(self.player_sprite, self.scene["Checkpoint"]):
            return REWARD_CHECKPOINT
        
        if arcade.check_for_collision_with_list(self.player_sprite, self.scene["Enemies"]):
            return REWARD_DEATH
            
        if self.player_sprite.center_y < 0:
            return REWARD_FALL
        
        if arcade.check_for_collision_with_list(self.player_sprite, self.scene["Coins"]):
            return REWARD_COIN
            
        return REWARD_DEFAULT  
    
    def execute_action(self, action):
        current_time = time.time()
        if not hasattr(self, 'last_jump_time'):
            self.last_jump_time = 0
        
        current_x_speed = self.player_sprite.change_x
        if action in ['LEFT', 'JUMP_LEFT']:
            self.player_sprite.change_x = self.player_sprite.change_x - 0.5
        elif action in ['RIGHT', 'JUMP_RIGHT']:
            self.player_sprite.change_x =self.player_sprite.change_x+ 0.5
        else:
            if abs(current_x_speed) < 0.5:
                self.player_sprite.change_x = 0
            elif current_x_speed > 0:
                self.player_sprite.change_x = current_x_speed - 0.5
            else:
                self.player_sprite.change_x = current_x_speed + 0.5

        if 'JUMP' in action and self.physics_engine.can_jump():
            if current_time - self.last_jump_time > 0.5:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                if 'RIGHT' in action:
                    self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED * 1.2
                elif 'LEFT' in action:
                    self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED * 1.2
                self.last_jump_time = current_time
    

    def reset_episode(self):
        if self.episode_steps > 0:  
            self.episode_rewards.append(self.total_reward)
            self.episode_steps_history.append(self.episode_steps)
            print(f"Saved metrics - Total Reward: {self.total_reward}, Steps: {self.episode_steps}")

        respawn(self)
        
        self.current_state = self.qtable.get_state_key(
            self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.physics_engine.can_jump(),
            self.get_state_from_radar()
        )

        remove_sprites(self)
        setup_coins(self)
        setup_flag(self)
        setup_enemies(self) 
    
    def on_update(self, delta_time):
        if self.current_state is None:
                self.current_state = self.qtable.get_state_key(
                    self.player_sprite.center_x,
                    self.player_sprite.center_y,
                    self.physics_engine.can_jump(),
                    self.get_state_from_radar()
                )
        self.enemy_list.update()
        self.enemy_list.update_animation()
        current_state = self.qtable.get_state_key(
            self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.physics_engine.can_jump(),
            self.get_state_from_radar()
        )
        action = self.qtable.best_action(current_state, self.exploration_rate)
        self.execute_action(action)
        self.physics_engine.update()

        new_state = self.qtable.get_state_key(
            self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.physics_engine.can_jump(),
            self.get_state_from_radar()
        )

        reward = self.get_reward()
        self.qtable.set(current_state, action, reward, new_state)
        self.total_reward += reward
        self.episode_steps += 1

        if reward == REWARD_GOAL:
            self.exploration_rate *= 0.85
            self.reset_episode()
        elif reward == REWARD_DEATH:
            self.reset_episode()
        elif reward == REWARD_COIN:
            coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Coins"])
            for coin in coin_hit_list:
                coin.remove_from_sprite_lists()
        elif arcade.check_for_collision_with_list(self.player_sprite, self.scene["Checkpoint"]):
            checkpoint_hit = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Checkpoint"])
            for flag in checkpoint_hit:
                flag.remove_from_sprite_lists()
            if self.episodes % 100 == 0:
                with open(FILE_AGENT, 'wb') as f:
                    pickle.dump(self.qtable.dic, f)

        self.center_camera_to_player()

    def get_state_from_radar(self):
        
        enemy_detected = False
        
        player_x = self.player_sprite.center_x
        player_y = self.player_sprite.center_y
        
        radar = {
            'enemy_N': False,
            'enemy_S': False, 
            'enemy_E': False,
            'enemy_W': False,
            'flag_east': False,
            'flag_close': False,
            'chekpoint_east':False,
            'checkpoint_close':False
        }
        enemy_detected= compute_ennemy_position(self,player_x,player_y,radar,enemy_detected)
        compute_flag_positon(self,player_x,player_y,radar)
        compute_checkpoint_position(self,player_x,player_y,radar)         
            
        update_player_color(self, enemy_detected, radar['flag_close'])
        
        return tuple(radar.values())

        
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
