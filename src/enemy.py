import arcade

CHARACTER_SCALING = 1


class Enemy(arcade.AnimatedWalkingSprite):
    def __init__(self, x, y):
        super().__init__(scale=CHARACTER_SCALING)

        self.stand_right_textures = [
            arcade.load_texture(":resources:images/animated_characters/zombie/zombie_idle.png")]
        self.stand_left_textures = [
            arcade.load_texture(":resources:images/animated_characters/zombie/zombie_idle.png", mirrored=True)]
        self.walk_right_textures = [
            arcade.load_texture(f":resources:images/animated_characters/zombie/zombie_walk{i}.png") for i in range(8)
        ]
        self.walk_left_textures = [
            arcade.load_texture(f":resources:images/animated_characters/zombie/zombie_walk{i}.png", mirrored=True)
            for i in range(8)
        ]

        self.texture = self.stand_right_textures[0]

        self.set_hit_box(self.texture.hit_box_points)

        self.center_x = x
        self.center_y = y
        self.change_x = 2

    def update(self):
        self.center_x += self.change_x

        if self.center_x < 1600 or self.center_x > 1800:
            self.change_x *= -1
