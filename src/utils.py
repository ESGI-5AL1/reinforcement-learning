import pickle
import matplotlib.pyplot as plt
import os

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


def display_menu(self):
    while True:
        print("\n=== Menu ===")
        print("1. Continuer l'apprentissage")
        print("2. Quitter le jeu")
        print("3. Afficher la QTable")
        print("4. Afficher l'évolution des scores")
        choice = input("Veuillez entrer votre choix (1, 2, 3 ou 4) : ")

        if choice == "1":
            print("L'apprentissage continue...")
            self.reset_agent()
            break
        elif choice == "2":
            print("Merci d'avoir joué !")
            self.close()
            break
        elif choice == "3":
            self.qtable.print_qtable()
        elif choice == "4":
            plot_scores()  # Tracer la courbe des scores
        else:
            print("Choix invalide. Veuillez réessayer.")



def save_qtable(qtable, file_path="robot.qtable"):
    """
    Sauvegarde la QTable dans un fichier.
    :param qtable: L'instance de la QTable à sauvegarder.
    :param file_path: Le chemin du fichier où sauvegarder la QTable.
    """
    with open(file_path, "wb") as file:
        pickle.dump(qtable, file)
    print(f"QTable sauvegardée dans {file_path}.")


def load_qtable(file_path="robot.qtable"):
    """
    Charge une QTable depuis un fichier.
    :param file_path: Le chemin du fichier contenant la QTable.
    :return: L'instance de la QTable chargée ou None si le fichier n'existe pas.
    """
    try:
        with open(file_path, "rb") as file:
            qtable = pickle.load(file)
            print(f"QTable chargée depuis {file_path}.")
            return qtable
    except FileNotFoundError:
        print(f"Aucun fichier trouvé à {file_path}. Une nouvelle QTable sera créée.")
        return None


def print_qtable(qtable):
    """
    Affiche les éléments de la QTable dans la console.
    """
    print("\n=== QTable ===")
    for state, actions in qtable.dic.items():
        print(f"State: {state}")
        for action, value in actions.items():
            print(f"  Action: {action}, Value: {value:.2f}")


def plot_scores(filename="scores.pkl"):
    """
    Charge les scores depuis un fichier et affiche l'évolution des scores avec un graphique.
    Si le fichier n'existe pas, il est initialisé avec une liste vide.
    """

    if not os.path.exists(filename):
        print(f"Le fichier {filename} n'existe pas. Aucun score à afficher.")
        return

    # chargemetn des scrores
    with open(filename, "rb") as f:
        scores = pickle.load(f)

    if not scores:
        print("Aucun score enregistré. Le graphique ne sera pas généré.")
        return


    plt.figure(figsize=(10, 6))
    plt.plot(scores, label="Scores", marker="o")
    plt.title("Évolution des scores")
    plt.xlabel("Itération")
    plt.ylabel("Score")
    plt.legend()
    plt.grid(True)
    plt.show()

