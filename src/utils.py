import matplotlib.pyplot as plt

import arcade

from consts import *
from enemy import Enemy



plateform_coordinate_list = [
   (0, 4000, 32),    # Sol 1
   (1600, 1780, 300),
   (950, 1480, 200),
   (1200, 1400, 370),
   (2200, 2300, 200),

   (2400, 2600, 300),
   (2660, 2900, 200),
   (2960, 2900, 400),
   (3000, 3200, 300)
]

crates_coordinate_list = [
   [0, 96], [0, 160], [0, 224], [0, 288], [0, 352], #mur 1
   [256, 96], 
   [512, 96], [512, 160],
    [720, 96], [720, 160], [720, 200],
   [3800, 96], [3800, 160], [3800, 224],[3800,288],[0, 288], [0, 352] # mur final

]

ENEMIES_POSITIONS = [
   (1000, 128),    
   (1600, 128),   
   (2400, 128),   

 
   (1296, 296),   
   (2560, 396),  
   (3100, 396)    
]
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
    
    enemy_positions = [ENEMIES_POSITIONS[0], ENEMIES_POSITIONS[-1]] if game.episodes < 3 else \
                     ENEMIES_POSITIONS[:4] if game.episodes < 5 else \
                     ENEMIES_POSITIONS
    
    for pos in enemy_positions:
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
    # Pièces sur toutes les plateformes sauf le sol
    for start_x, end_x, height in plateform_coordinate_list[1:]:
        place_multi_coins_tiles(game, start_x, end_x, 128, ":resources:images/items/gold_1.png", COIN_SCALING, height + 64)

    # Colonnes de pièces
    height_groups = {}
    for x, y in crates_coordinate_list:
        if x not in height_groups:
            height_groups[x] = []
        height_groups[x].append(y)
    
    # Ajouter pièces au sommet de chaque colonne
    for x, heights in height_groups.items():
        max_height = max(heights)
        coin = arcade.Sprite(":resources:images/items/gold_1.png", COIN_SCALING)
        coin.center_x = x
        coin.center_y = max_height + 64
        game.scene.add_sprite("Coins", coin)
        
    # Ajout de pièces au sol après le checkpoint
    for x in range(1920, 2100, 30):  
        coin = arcade.Sprite(":resources:images/items/gold_1.png", COIN_SCALING)
        coin.center_x = x
        coin.center_y = 96  # Hauteur du sol
        game.scene.add_sprite("Coins", coin)

def setup_flag(game):
   # Drapeau intermédiaire
   green_flag = arcade.Sprite(":resources:images/items/flagGreen2.png", COIN_SCALING)
   green_flag.center_x = 1900
   green_flag.center_y = 96
   game.scene.add_sprite("Checkpoint", green_flag)
   
   # Drapeau final
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

















