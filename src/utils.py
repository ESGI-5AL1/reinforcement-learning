import pickle
import matplotlib.pyplot as plt
import os

import arcade

from consts import *
from enemy import Enemy



crates_coordinate_list = [[0, 96], [0, 160], [0, 224], [0, 288], [0, 352], [256, 96], [512, 96], [512, 160],[720, 96], [720, 160],[720,200], [1980, 96], [1980, 160], [1980, 224], [1980, 288], [1980, 352]]

plateform_coordinate_list = [
    (0, 2000, 32),
    (1000, 1300, 450),
    (1000, 1400, 200),
    (1528, 1700, 300)
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

def setup_flag(game):
    green_flag = arcade.Sprite(":resources:images/items/flagGreen2.png", COIN_SCALING)
    green_flag.center_x = 1900
    green_flag.center_y = 96
    game.scene.add_sprite("Flag", green_flag)

def setup_physics(game):
    game.physics_engine = arcade.PhysicsEnginePlatformer(
        game.player_sprite, gravity_constant=GRAVITY, walls=game.scene["Walls"]
    )
    game.current_state = game.qtable.get_state_key(
        game.player_sprite.center_x,
        game.player_sprite.center_y,
        game.physics_engine.can_jump(),
        game.get_state_from_radar()
    )


def update_player_color(game, enemy_detected, flag_detected):
    if enemy_detected:
        game.player_sprite.color = (255, 0, 0)  # Rouge
    elif flag_detected:
        game.player_sprite.color = (0, 128, 0) 
    else:
        game.player_sprite.color = (255, 255, 255) 

















