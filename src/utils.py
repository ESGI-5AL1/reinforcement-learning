import arcade

crates_coordinate_list = [[0, 96], [0, 160], [0, 224], [0, 288], [0, 352], [256, 96], [512, 96], [512, 160], [1980, 96],
                          [1980, 160], [1980, 224], [1980, 288], [1980, 352]]


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


def display_radar_console(radar_info, radius):
    print("\n=== Radar Detection ===")
    print(f"Radius: {radius} units")
    for key, objects in radar_info.items():
        print(f"{key.capitalize()} detected: {len(objects)}")
        for idx, obj in enumerate(objects, 1):
            print(
                f"  {key.capitalize()[:-1]} {idx}: "
                f"(x: {obj['x']}, y: {obj['y']}, distance: {obj['distance']:.2f}, direction: {obj['direction']})"
            )


def display_radar_screen(self, radar_info, radius):
    base_x, base_y = 10, 580  # Position de départ pour l'affichage
    line_height = 20  # Espacement entre les lignes

    arcade.draw_text(f"Radar (Radius: {radius} units):", base_x, base_y, arcade.color.WHITE, 14)

    for idx, (key, objects) in enumerate(radar_info.items(), start=1):
        y_offset = base_y - idx * line_height
        arcade.draw_text(f"{key.capitalize()}: {len(objects)}", base_x, y_offset, arcade.color.WHITE, 12)

        for obj_idx, obj in enumerate(objects, start=1):
            obj_y_offset = y_offset - (obj_idx * line_height)
            arcade.draw_text(
                f"  {key.capitalize()[:-1]} {obj_idx}: (x: {obj['x']}, y: {obj['y']}, "
                f"dist: {obj['distance']:.2f}, dir: {obj['direction']})",
                base_x + 20,
                obj_y_offset,
                arcade.color.WHITE,
                10,
            )
