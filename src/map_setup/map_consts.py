
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 650
WORLD_WIDTH = 3000

SCREEN_TITLE = "MR ROBOT Q-LEARNING"
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1

PLAYER_JUMP_SPEED = 20



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
   [3350, 96], [3350, 160], [3350, 224],[3350,288],[3350, 352] # mur final

]

# ENEMIES_POSITIONS = [
#    (1000, 128),    
#    (1600, 128),   
#    (2400, 128),   
#    (1296, 296),   
#    (2560, 396),  
#    (3100, 396)    
# ]

#3 enemies setup 
# ENEMIES_POSITIONS = [
#    (1000, 128),    
#    (2400, 128),    
#    (3100, 396)    
# ]

ENEMIES_POSITIONS = [
   (1000, 128),    
   (2560, 396),    
   (3100, 396),
   (2150, 128),    
]