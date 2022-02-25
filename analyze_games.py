import pickle
import pandas as pd
import numpy as np
import itertools

from run_history_reader import Game, Unit, Board, Player, TreasureChoice


def is_main(game: Game):
    results = game.final_results
    for i, item in enumerate(results):
        # My main account's ID
        if item.id == "429402B2E2AD1FA4":
            return True
    return False


def get_final_level(game: Game):
    results = game.final_results
    for i, item in enumerate(results):
        if item.id == "429402B2E2AD1FA4":
            return item.level
    return 0


def get_current_level(game: Game, turn_number: int):
    leaderboard = game.leaderboards[turn_number - 1]
    for i, item in enumerate(leaderboard):
        if item.id == "429402B2E2AD1FA4":
            return item.level


if __name__ == "__main__":
    games = pickle.load(open("games.pkl", "rb"))

    count = 0
    made_to_6 = 0
    treasures = {2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
    treasure_choices = []
    comps = []
    purchases = []
    for game in games:
        if not is_main(game):
            continue
        count += 1
        was_6 = get_final_level(game) == 6
        if was_6:
            made_to_6 += 1
        for choice in game.treasure_choices:
            if choice.chosen != "Skip":
                treasure_record = pd.Series({"tier": choice.tier, "placement": game.placement, "name": choice.chosen})
                treasure_choices.append(treasure_record)
        for turn in range(1, game.turn + 1):
            player_level = get_current_level(game, turn)
            for purchase in itertools.chain.from_iterable(game.bought[turn-1]):
                purchase_record = pd.Series({"name": purchase.name, "level": player_level, "placement": game.placement, "game": count})
                purchases.append(purchase_record)
        trees = 0
        evils = 0
        mages = 0
        slays = 0
        dwarves = 0
        good_boys = 0
        for unit in game.final_board.units:
            if "slay" in unit.keywords:
                slays += 1
            if "mage" in unit.subtypes:
                mages += 1
            if "treant" in unit.subtypes:
                trees += 1
            if "evil" in unit.subtypes:
                evils += 1
            if "dwarf" in unit.subtypes:
                dwarves += 1
            if unit.name == "Good Boy":
                good_boys += 1
            if unit.name in ["Baba Yaga", "Grim Soul", "Riverwish Mermaid", "Lightning Dragon"]:
                slays += 1
        if good_boys > 0:
            comp = {"comp": "Good Boy", "placement": game.placement}
        elif slays > 1:
            comp = {"comp": "Slay", "placement": game.placement}
        elif trees > 4:
            comp = {"comp": "Pure Trees", "placement": game.placement}
        elif dwarves > 3:
            comp = {"comp": "Dwarves", "placement": game.placement}
        elif evils > 5:
            comp = {"comp": "Evil", "placement": game.placement}
        elif mages > 2:
            comp = {"comp": "Mages", "placement": game.placement}
        else:
            comp = {"comp": "Other", "placement": game.placement}
            print(game.final_board.units)
        if was_6:
            comps.append(pd.Series(comp))

    treasure_choices = pd.DataFrame(treasure_choices)
    for tier in [2, 3, 4, 5, 6, 7]:
        my_list = []
        for treasure in treasure_choices[treasure_choices['tier'] == tier].name.unique():
            df_subset = treasure_choices[treasure_choices['name'] == treasure]
            my_list.append((treasure, len(df_subset), np.mean(df_subset.placement)))
        my_list = sorted(my_list, key=lambda x: x[1], reverse=True)
        print(my_list)

    comps = pd.DataFrame(comps)
    my_list = []
    for comp in comps.comp.unique():
        df_subset = comps[comps["comp"] == comp]
        my_list.append((comp, len(df_subset), np.mean(df_subset.placement)))
    my_list = sorted(my_list, key=lambda x: x[1], reverse=True)
    print(my_list)

    purchases = pd.DataFrame(purchases)
    purchases = purchases.drop_duplicates()
    for level in [2, 3, 4, 5, 6]:
        my_list = []
        for unit in purchases[purchases['level'] == level].name.unique():
            df_subset = purchases[purchases['level'] == level]
            df_subset = df_subset[df_subset['name'] == unit]
            my_list.append((unit, len(df_subset), np.mean(df_subset.placement)))
        my_list = sorted(my_list, key=lambda x: x[1], reverse=True)
        print("Level {} purchases:".format(level))
        print(my_list[:10])

    print("Hit level 6: {}/{}".format(made_to_6, count))





