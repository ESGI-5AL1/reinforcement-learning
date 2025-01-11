import os
import pickle
import time

# Utiliser un le rader pour limiter le nombre de tirs
# Utiliser variables globales pour recompenses
# ecrase le fichier existant avec une liste vide
# calculer distance drapeau, baisse -> bonus
# 


import arcade
import random
# from enemy import Enemy
from qtable import QTable
from utils import place_multi_coins_tiles, place_multi_planet_tiles, crates_coordinate_list, display_menu, load_qtable, plot_scores, \
    save_qtable

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
WORLD_WIDTH = 3000
SCREEN_TITLE = "MR ROBOT"

CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
BULLET_SPEED = 10

ROBOT_IDLE = ":resources:images/animated_characters/robot/robot_idle.png"
PLANET_TILE = ":resources:images/tiles/planet.png"
BRICK_GREY = ":resources:images/tiles/brickGrey.png"
COIN_TILE = ":resources:images/items/coinGold.png"
GREEN_FLAG = ":resources:images/items/flagGreen2.png"

SPAWN_X = 64
SPAWN_Y = 128

JUMP = "JUMP"
LEFT = "LEFT"
RIGHT = "RIGHT"
JUMP_RIGHT = "JUMP_RIGHT"
JUMP_LEFT = "JUMP_LEFT"
SHOOT = "SHOOT"
ACTIONS = [JUMP, LEFT, RIGHT, JUMP_RIGHT, JUMP_LEFT]

MAX_EPISODE_STEPS = 1000  # Maximum steps per episode
MAX_EPISODE_TIME = 60     # Maximum time in seconds per episode
GOAL_X = 1900            # Flag X position
OUT_OF_BOUNDS_Y = 0      # Death height

QTABLE = None

rewards = {
    # Existing rewards
    "basic_action": -1,
    "enemy_collision": -100,
    "flag_collision": +3000,
    "coin_collision": +500,
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



class Game(arcade.Window):

    def __init__(self):

        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)


        # Add episode tracking variables
        self.last_distance = 0
        self.episode_steps = 0
        self.episode_start_time = time.time()
        self.previous_x = SPAWN_X  # Track position to detect stuck agent
        self.stuck_counter = 0
        self.steps_without_progress = 0




        self.set_update_rate(1 / 10000000)
        self.scores = []
        global QTABLE
        if QTABLE is None:
            loaded_qtable = load_qtable()
            self.qtable = loaded_qtable if loaded_qtable else QTable()
        else:
            self.qtable = QTABLE

        self.current_state = None
        self.last_action = None

        
        self.time_elapsed = 0 


        self.scene = None
        # Déterminer si le joueur ou l'agent a le contrôle
        self.manual = False
        self.player_sprite = None

        self.physics_engine = None

        self.camera = None

        self.gui_camera = arcade.Camera(self.width, self.height)

        self.current_agent_score = 0
        self.reward = 0
        self.iteration = 0
        self.last_score = 0
        self.no_reward_steps = 0
        self.no_reward_limit = 1000
        self.can_jump = True
        self.flag_reached = False  # Variable pour indiquer si le drapeau est atteint

        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        ##self.shoot_sound = arcade.load_sound(":resources:sounds/laser1.wav")

        self.spawn_x = SPAWN_X
        self.spawn_y = SPAWN_Y

        self.bullet_list = arcade.SpriteList()

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def check_termination(self):
        """Check if episode should terminate and return (done, reason)"""
        current_time = time.time()
        episode_time = current_time - self.episode_start_time

        # Check various termination conditions
        termination_conditions = {
            # Time limit exceeded
            "timeout": episode_time >= MAX_EPISODE_TIME,

            # Agent fell off the map
            "fell_off": self.player_sprite.center_y <= OUT_OF_BOUNDS_Y,

            # Agent is stuck (no x-position change for too long)
            "stuck": abs(self.player_sprite.center_x - self.previous_x) < 1
                     and self.stuck_counter > 100,

            # No progress towards goal
            "no_progress": self.steps_without_progress > 500,

            # Goal reached
            "success": self.flag_reached,
        }

        done = any(termination_conditions.values())
        reason = next((key for key, value in termination_conditions.items()
                       if value), None)

        return done, reason

    def calculate_final_reward(self, termination_reason):
        """Calculate final reward based on termination reason"""
        final_rewards = {
            "timeout": rewards["time_is_up"],
            "fell_off": -200,
            "stuck": -150,
            "no_progress": -100,
            "success": rewards["flag_collision"]
        }

        return final_rewards.get(termination_reason, 0)

    def reset_episode(self):
        """Reset the environment for a new episode"""
        self.episode_steps = 0
        self.episode_start_time = time.time()
        self.previous_x = SPAWN_X
        self.stuck_counter = 0
        self.steps_without_progress = 0
        self.current_agent_score = 0
        self.reward = 0
        self.flag_reached = False

        # Clear existing coins first
        # if "Coins" in self.scene.name_mapping:
        #     self.scene["Coins"].clear()

        # Add new coins
        # self.add_coins()

        # Reset player position
        self.player_sprite.center_x = SPAWN_X
        self.player_sprite.center_y = SPAWN_Y
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        # Reset flag
        if "Flag" in self.scene.name_mapping:
            self.scene["Flag"].clear()
        green_flag = arcade.Sprite(GREEN_FLAG, COIN_SCALING)
        green_flag.center_x = GOAL_X
        green_flag.center_y = 96
        self.scene.add_sprite("Flag", green_flag)

    def setup(self):
        self.camera = arcade.Camera(self.width, self.height)

        self.scene = arcade.Scene()

        self.player_sprite = arcade.AnimatedWalkingSprite(scale=CHARACTER_SCALING)
        self.player_sprite.stand_right_textures = [arcade.load_texture(ROBOT_IDLE)]
        self.player_sprite.stand_left_textures = [arcade.load_texture(ROBOT_IDLE, mirrored=True)]
        self.player_sprite.walk_right_textures = [
            arcade.load_texture(f":resources:images/animated_characters/robot/robot_walk{i}.png") for i in range(8)
        ]
        self.player_sprite.walk_left_textures = [
            arcade.load_texture(f":resources:images/animated_characters/robot/robot_walk{i}.png",
                                mirrored=True) for i in range(8)
        ]
        self.player_sprite.center_x = SPAWN_X
        self.player_sprite.center_y = SPAWN_Y
        self.player_sprite.facing_right = True
        self.scene.add_sprite("Player", self.player_sprite)

        # self.add_coins()

        place_multi_planet_tiles(self, 0, 2000, 64, PLANET_TILE, TILE_SCALING, 32)
        place_multi_planet_tiles(self, 1000, 1300, 64, PLANET_TILE, TILE_SCALING, 450)
        place_multi_planet_tiles(self, 1000, 1400, 64, PLANET_TILE, TILE_SCALING, 200)
        place_multi_planet_tiles(self, 1528, 1700, 64, PLANET_TILE, TILE_SCALING, 300)

        for coordinate in crates_coordinate_list:
            wall = arcade.Sprite(BRICK_GREY, TILE_SCALING)
            wall.position = coordinate
            self.scene.add_sprite("Walls", wall)

        green_flag = arcade.Sprite(GREEN_FLAG, COIN_SCALING)
        green_flag.center_x = 1900
        green_flag.center_y = 96
        self.scene.add_sprite("Flag", green_flag)

        # for x in range(1600, 1800, 100):
        #     enemy = Enemy(x, 128)
        #     self.scene.add_sprite("Enemies", enemy)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Walls"]
        )

    def add_coins(self):
        place_multi_coins_tiles(self, 128, 1250, 256, COIN_TILE, COIN_SCALING, 96)
        place_multi_coins_tiles(self, 1000, 1300, 128, COIN_TILE, COIN_SCALING, 270)
        place_multi_coins_tiles(self, 1000, 1300, 128, COIN_TILE, COIN_SCALING, 520)
        place_multi_coins_tiles(self, 1528, 1700, 128, COIN_TILE, COIN_SCALING, 370)

        coin = arcade.Sprite(COIN_TILE, COIN_SCALING)
        coin.center_x = 256
        coin.center_y = 164
        self.scene.add_sprite("Coins", coin)

        coin = arcade.Sprite(COIN_TILE, COIN_SCALING)
        coin.center_x = 512
        coin.center_y = 228
        self.scene.add_sprite("Coins", coin)

        coin = arcade.Sprite(COIN_TILE, COIN_SCALING)
        coin.center_x = 768
        coin.center_y = 356
        self.scene.add_sprite("Coins", coin)

    def reset_agent(self, save_score=True):
        """
        Réinitialise l'agent pour une nouvelle itération.
        Sauvegarde le score uniquement si le drapeau a été atteint.
        """
        print(self.current_agent_score)

        self.current_agent_score=0

            # print(f"Score sauvegardé pour l'itération {self.iteration}: {self.reward}")

        # Réinitialiser les paramètres pour la prochaine itération
        self.flag_reached = False  # Réinitialiser le drapeau pour la prochaine itération
        # self.reward = 0
        self.iteration += 1
        self.player_sprite.center_x = SPAWN_X
        self.player_sprite.center_y = SPAWN_Y
        self.no_reward_steps = 0


    def get_state(self):
        x = int(self.player_sprite.center_x / 50)
        y = int(self.player_sprite.center_y / 50)
        #radar_info = self.radar_detection()

        state = (
            x,
            y,
            #len(radar_info["coins"]),
            # len(radar_info["enemies"]),
            #len(radar_info["walls"]),
        )
        return state

    #def shoot(self):
    #    bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", 0.8)
    #    bullet.change_x = BULLET_SPEED if self.player_sprite.facing_right else -BULLET_SPEED
    #    bullet.center_x = self.player_sprite.center_x
    #    bullet.center_y = self.player_sprite.center_y
    #    self.bullet_list.append(bullet)
        # arcade.play_sound(self.shoot_sound)

    def on_draw(self):
        self.clear()

        self.camera.use()

        self.scene.draw()

        self.bullet_list.draw()

        self.gui_camera.use()

        score_text = f"Score: {self.current_agent_score}"

        arcade.draw_text(score_text, 10, 10, arcade.csscolor.WHITE, 18)
        arcade.draw_text(f"Itération numéro {self.iteration}", 10, 30, arcade.csscolor.WHITE, 18)
        if hasattr(self, 'radar_info'):
            from utils import display_radar_screen
            # display_radar_screen(self, self.radar_info, radius=150)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            self.player_sprite.facing_right = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            self.player_sprite.facing_right = True
        #elif key == arcade.key.SPACE:
        #    self.shoot()

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)
        self.camera.move_to((max(screen_center_x, 0), max(screen_center_y, 0)))

    def reset_player(self):
        global QTABLE
        QTABLE = self.qtable
        self.player_sprite.center_x = SPAWN_X
        self.player_sprite.center_y = SPAWN_Y

    def on_close(self):
        global QTABLE
        QTABLE = self.qtable
        save_qtable(QTABLE)
        super().on_close()

    def on_update(self, delta_time):

        self.reward = 0
        if self.physics_engine.can_jump():
            self.can_jump = True
        # self.radar_info = self.radar_detection(radius=150, display_mode="screen")
        self.current_state = self.get_state()
        self.physics_engine.update()
        self.player_sprite.update_animation(delta_time)
        self.bullet_list.update()


        if not self.manual:

            self.episode_steps += 1

            if abs(self.player_sprite.center_x - self.previous_x) < 1:
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0

            # Choose and execute action
            self.current_state = self.get_state()
            action = self.qtable.choose_action(self.current_state)
            self.reward += rewards["action_costs"][action]

            if action == JUMP:
                if self.physics_engine.can_jump() and self.can_jump:
                    self.player_sprite.change_y = PLAYER_JUMP_SPEED
                    self.can_jump = False
            elif action == JUMP_RIGHT:
                if self.physics_engine.can_jump() and self.can_jump:
                    self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
                    self.player_sprite.change_y = PLAYER_JUMP_SPEED
                    self.can_jump = False
            elif action == JUMP_LEFT:
                if self.physics_engine.can_jump() and self.can_jump:
                    self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
                    self.player_sprite.change_y = PLAYER_JUMP_SPEED
                    self.can_jump = False
            elif action == LEFT:
                self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
                self.player_sprite.facing_right = False
            elif action == RIGHT:
                self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
                self.player_sprite.facing_right = True
                #elif action == SHOOT:
                #    self.shoot()
                #    radar = self.radar_detection()
                #    self.reward = rewards["basic_action"]
                    # if not radar["enemies"]:
                    #     print("pas d'ennemis")
                    #     self.reward -= 40

            # Add progress-based rewards
            distance_to_flag = abs(1900 - self.player_sprite.center_x)  # Flag is at x=1900
            progress_reward = -0.01 * distance_to_flag  # Negative reward based on distance
            self.reward += progress_reward

            # Add height penalty to discourage unnecessary jumping
            if self.player_sprite.center_y > 200:  # Adjust threshold as needed
                height_penalty = -0.5 * (self.player_sprite.center_y - 200)
                self.reward += height_penalty

            # Add energy efficiency bonus
            if self.physics_engine.can_jump() and abs(self.player_sprite.change_x) < 0.1:
                self.reward += 1

            # coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Coins"])
            # for coin in coin_hit_list:
            #     self.reward = rewards["coin_collision"]
            #     coin.remove_from_sprite_lists()
            #     arcade.play_sound(self.collect_coin_sound)

            # if arcade.check_for_collision_with_list(self.player_sprite, self.scene["Enemies"]):
            #     self.reward -= 100
            #     self.reset_agent()

            flag_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Flag"])
            for flag in flag_hit_list:
                self.reward = rewards["flag_collision"]
                self.flag_reached = True
                flag.remove_from_sprite_lists()
                arcade.play_sound(self.collect_coin_sound)
                # display_menu(self)
                self.reset_agent()
                self.reset_episode()

            if arcade.check_for_collision_with_list(self.player_sprite, self.scene["Walls"]):
                self.reward = rewards["wall_collision"]

            new_state = self.get_state()
            

            self.qtable.set(self.current_state, action, self.reward, new_state, done=self.flag_reached)

            # self.qtable.print_training_stats()

            self.last_action = action
            self.current_state = new_state

            # if not positive_reward:
            #     self.no_reward_steps += 1
            #     if self.no_reward_steps >= self.no_reward_limit:
            #         print("DEBUG: Trop longtemps sans récompense. Réinitialisation sans sauvegarde.")
            #         self.flag_reached = False  
            #         self.reset_agent(save_score=False)  

            # else:
            #     self.no_reward_steps = 0

        # for enemy in self.scene["Enemies"]:
        #     enemy.update()

        # for bullet in self.bullet_list:
        #     hit_wall_list = arcade.check_for_collision_with_list(bullet, self.scene["Walls"])
        #     if hit_wall_list:
        #         bullet.remove_from_sprite_lists()

        #     hit_enemy_list = arcade.check_for_collision_with_list(bullet, self.scene["Enemies"])
        #     if hit_enemy_list:
        #         bullet.remove_from_sprite_lists()
        #         for enemy in hit_enemy_list:
        #             enemy.remove_from_sprite_lists()
        #             self.reward+=5
        for bullet in self.bullet_list:
            if bullet.right < 0 or bullet.left > WORLD_WIDTH:
                bullet.remove_from_sprite_lists()

        done, termination_reason = self.check_termination()

        if done:
            # Add final reward based on termination reason
            final_reward = self.calculate_final_reward(termination_reason)
            self.reward += final_reward

            # Log episode information
            print(f"Episode {self.iteration} terminated: {termination_reason}")
            print(f"Steps: {self.episode_steps}, Score: {self.current_agent_score}")

            # Get final state
            new_state = self.get_state()

            # Update Q-table with terminal state
            self.qtable.set(self.current_state, action, self.reward, new_state, done=True)

            # Reset for next episode
            self.reset_episode()
            self.iteration += 1
        else:
            # Normal step update
            new_state = self.get_state()
            self.qtable.set(self.current_state, action, self.reward, new_state, done=False)

        self.current_agent_score += self.reward
        self.center_camera_to_player()

    def radar_detection(self, radius=150, display_mode="console"):
        radar_info = {"coins": [], "walls": []}
        # reucperer tout les ennemis -> ffaux - recuperer le plus proche
        for sprite_list, key in [
            # (self.scene["Coins"], "coins"),
            # (self.scene["Enemies"], "enemies"),
            (self.scene["Walls"], "walls"),
        ]:
            for sprite in sprite_list:
                distance = arcade.get_distance_between_sprites(self.player_sprite, sprite)
                if distance <= radius:
                    direction_x = "right" if sprite.center_x > self.player_sprite.center_x else "left"
                    direction_y = "up" if sprite.center_y > self.player_sprite.center_y else "down"
                    direction = f"{direction_x} {direction_y}"

                    radar_info[key].append(
                        {
                            "x": round(sprite.center_x, 2),
                            "y": round(sprite.center_y, 2),
                            "distance": round(distance, 2),
                            "direction": direction,
                        }
                    )

        return radar_info


def main():
    window = Game()
    window.setup()
    arcade.run()
    plot_scores()


if __name__ == "__main__":
    main()
