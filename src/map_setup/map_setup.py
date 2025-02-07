import matplotlib.pyplot as plt
import arcade
from qlearning.qlearning_consts import *
from enemy import Enemy
from map_setup.map_consts import *



def place_multi_planet_tiles(self, start, stop, step, PLANET_TILE, TILE_SCALING, center_y):
    for x in range(start, stop, step):
        wall = arcade.Sprite(PLANET_TILE, TILE_SCALING)
        wall.center_x = x
        wall.center_y = center_y
        self.scene.add_sprite("Walls", wall)


def place_multi_coins_tiles(self, start, stop, step, COIN_TILE, COIN_SCALING, center_y):
    for x in range(start, stop, step):
        coin = arcade.Sprite(COIN_TILE, COIN_SCALING)
        coin.center_x = x
        coin.center_y = center_y
        self.scene.add_sprite("Coins", coin)


def setup_player(game, spawn_x, spawn_y):
    player_sprite = arcade.Sprite(
        ":resources:images/animated_characters/robot/robot_idle.png",
        CHARACTER_SCALING
    )
    player_sprite.center_x = spawn_x 
    player_sprite.center_y = spawn_y
    game.scene.add_sprite("Player", player_sprite)
    game.player_sprite = player_sprite
    return player_sprite


def setup_enemies(game):
    game.enemy_list = arcade.SpriteList()
    
    # enemy_positions = [ENEMIES_POSITIONS[0], ENEMIES_POSITIONS[-1]] if game.episodes < 50 else \
    #                  ENEMIES_POSITIONS[:4] if game.episodes < 100 else \
    #                  ENEMIES_POSITIONS
    # enemy_positions =[ENEMIES_POSITIONS[0], ENEMIES_POSITIONS[-1]]
    for pos in ENEMIES_POSITIONS:
        enemy = Enemy(pos[0], pos[1])
        game.enemy_list.append(enemy)
        game.scene.add_sprite("Enemies", enemy)
    


def setup_plateformes(game):
    for start_x, end_x, height in plateform_coordinate_list:
        place_multi_planet_tiles(game, start_x, end_x, 64, ":resources:images/tiles/planet.png", TILE_SCALING, height)


def setup_walls(game):
    for coordinate in crates_coordinate_list:
        wall = arcade.Sprite(":resources:images/tiles/brickGrey.png", TILE_SCALING)
        wall.position = coordinate
        game.scene.add_sprite("Walls", wall)

def setup_coins(game):
    for start_x, end_x, height in plateform_coordinate_list[1:]:
        place_multi_coins_tiles(game, start_x, end_x, 128, ":resources:images/items/gold_1.png", COIN_SCALING, height + 64)

    height_groups = {}
    for x, y in crates_coordinate_list:
        if x not in height_groups:
            height_groups[x] = []
        height_groups[x].append(y)
    
    for x, heights in height_groups.items():
        if x>0:
            max_height = max(heights)
            coin = arcade.Sprite(":resources:images/items/gold_1.png", COIN_SCALING)
            coin.center_x = x
            coin.center_y = max_height + 64
            game.scene.add_sprite("Coins", coin)
        
    for x in range(1920, 2100, 30):  
        coin = arcade.Sprite(":resources:images/items/gold_1.png", COIN_SCALING)
        coin.center_x = x
        coin.center_y = 96  # Hauteur du sol
        game.scene.add_sprite("Coins", coin)



def setup_flag(game):
   green_flag = arcade.Sprite(":resources:images/items/flagGreen2.png", COIN_SCALING)
   green_flag.center_x = 1900
   green_flag.center_y = 96
   game.scene.add_sprite("Checkpoint", green_flag)
   final_flag = arcade.Sprite(":resources:images/items/flagGreen2.png", COIN_SCALING)
   final_flag.center_x = 3740
   final_flag.center_y = 96
   game.scene.add_sprite("Flag", final_flag)

   

def setup_physics(game):
    game.physics_engine = arcade.PhysicsEnginePlatformer(
        game.player_sprite, gravity_constant=GRAVITY, walls=game.scene["Walls"]
    )
   


def update_player_color(game, enemy_detected, flag_detected):
    if enemy_detected:
        game.player_sprite.color = (255, 0, 0)  # Rouge
    elif flag_detected:
        game.player_sprite.color = (0, 128, 0) 
    else:
        game.player_sprite.color = (255, 255, 255) 


def remove_sprites(game):
    for sprite in game.scene["Coins"]:
            sprite.remove_from_sprite_lists()
    for sprite in game.scene["Checkpoint"]:
            sprite.remove_from_sprite_lists()
    for sprite in game.scene["Flag"]:
            sprite.remove_from_sprite_lists()
    for sprite in game.scene["Enemies"]:  
            sprite.remove_from_sprite_lists()

def respawn(game):
    game.player_sprite.center_x = game.spawn_x
    game.player_sprite.center_y = game.spawn_y
    game.player_sprite.change_x = 0
    game.player_sprite.change_y = 0
    game.episode_steps = 0
    game.total_reward = 0
    game.episodes += 1
















