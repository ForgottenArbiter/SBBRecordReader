from __future__ import annotations

import pickle
import datetime
import os
import pathlib
import pprint
import json
from typing import List

from construct import GreedyRange

from record_parser import STRUCT_ACTION, id_to_action_name


# Copied from SBB Tracker's template ID mapping
# (https://github.com/SBBTracker/SBBTracker/blob/main/assets/template-ids.json)
template_id_dict = json.load(open("template-ids.json", 'r'))


class Unit:

    def __init__(self, health, attack, name, zone, keywords=None, subtypes=None):
        self.health = health
        self.attack = attack
        self.name = name
        self.zone = zone
        if keywords is None:
            self.keywords = []
        else:
            self.keywords = keywords
        if subtypes is None:
            self.subtypes = []
        else:
            self.subtypes = subtypes

    def __repr__(self):
        return "{} ({}/{})".format(self.name, self.attack, self.health)

    @classmethod
    def from_unit_struct(cls, unit_struct):
        if unit_struct is None:
            return None
        health = unit_struct.health
        attack = unit_struct.attack
        if unit_struct.is_golden:
            template_id = unit_struct.template_id - 1
        else:
            template_id = unit_struct.template_id
        if str(template_id) in template_id_dict:
            name = template_id_dict[str(template_id)]["Name"]
        else:
            name = "Unknown"
        zone = unit_struct.zone
        subtypes = [str(subtype) for subtype in unit_struct.subtypes]
        keywords = [str(keyword) for keyword in unit_struct.keywords]
        return cls(health, attack, name, zone, keywords, subtypes)


class Board:

    def __init__(self, hero, units, treasures):
        self.hero = hero
        self.units = units
        self.treasures = treasures


class Player:

    def __init__(self, hero, health, level, experience, name, player_id):
        self.hero = hero
        self.health = health
        self.level = level
        self.experience = experience
        self.name = name
        self.id = player_id


class TreasureChoice:

    def __init__(self, choices, tier):
        self.choices = choices
        self.tier = tier
        self.chosen = "Skip"

    def choose_treasure(self, treasure):
        self.chosen = treasure


class Game:

    def __init__(self):
        self.shops = []
        self.bought = []
        self.boards = []
        self.enemy_boards = []
        self.leaderboards = []
        self.spells = []
        self.turn = 0
        self.mmr_change = 0
        self.game_over = False
        self.final_results = []
        self.placement = 0
        self.treasure_choices = []
        self.build_id = None
        self.final_board = None

    def start_new_turn(self):
        self.turn += 1
        self.shops.append([])
        self.bought.append([])
        self.spells.append([])
        self.leaderboards.append([])

    def add_shop(self, shop: List[Unit]):
        self.shops[self.turn - 1].append(shop)
        self.bought[self.turn - 1].append([])

    def cast_spell(self, spell: Unit):
        self.spells[self.turn - 1].append(spell)

    def add_battle(self, board: Board, enemy_board: Board):
        self.boards.append(board)
        self.enemy_boards.append(enemy_board)


def extract_game_from_record_file(filename):
    with open(filename, 'rb') as f:
        result = GreedyRange(STRUCT_ACTION).parse_stream(f)
        remaining_binary_contents = f.read()
    if len(remaining_binary_contents) != 0:
        print("Could not parse entire record file successfully.")
        # raise RuntimeError("Could not parse entire record file successfully.")
    game = Game()
    all_cards = {}
    iterator = iter(result)
    populate_treasure = False
    for record in iterator:
        action_name = id_to_action_name[record.action_id]
        if action_name == "ActionConnectionInfo":
            game.build_id = record.build_id
        if action_name in ["ActionUpdateCard", "ActionCreateCard"]:
            card = Unit.from_unit_struct(record.card)
            all_cards[record.card.card_id] = card
            if card.zone == "treasure" and action_name == "ActionCreateCard" and populate_treasure:
                game.treasure_choices[-1].choose_treasure(card.name)
                populate_treasure = False
        if action_name in ["ActionEnterShopPhase", "ActionRoll"]:
            if action_name == "ActionEnterShopPhase":
                game.start_new_turn()
            shop = []
            record = next(iterator)
            while (action_name := id_to_action_name[record.action_id]) in \
                    ["ActionModifyXP", "ActionModifyLevel", "ActionModifyNextLevelXP", "ActionUpdateCard", "ActionRemoveCard", "ActionCreateCard", "ActionModifyGold", "ActionPlayFX", "ActionPresentDiscover", "ActionUpdateEmotes", "ActionAddPlayer"]:
                if action_name == "ActionCreateCard":
                    card_struct = record.card
                    card = Unit.from_unit_struct(card_struct)
                    all_cards[card_struct.card_id] = card
                    if card_struct.zone == "shop":
                        shop.append(card)
                record = next(iterator)
            if len(shop) == 0:
                print("hmm")
            game.add_shop(shop)
            action_name = id_to_action_name[record.action_id]
        if action_name == "ActionEnterBrawlPhase":
            populate_treasure = False
        if action_name == "ActionMoveCard":
            if all_cards[record.card_id].zone == "shop":
                if record.target_zone == "character":
                    game.bought[-1][-1].append(all_cards[record.card_id])
                elif record.target_zone == "hand":
                    game.bought[-1][-1].append(all_cards[record.card_id])
        if action_name == "ActionCastSpell":
            game.cast_spell(all_cards[record.card_id])
        if action_name == "ActionPresentDiscover":
            if record.choice_text == "Choose a Treasure":
                treasures = [Unit.from_unit_struct(treasure) for treasure in record.treasures]
                game.treasure_choices.append(TreasureChoice([treasure.name for treasure in treasures], record.treasures[0].cost))
                populate_treasure = True
        if action_name == "ActionEnterResultsPhase":
            game.mmr_change = record.rank_reward
            game.game_over = True
            game.final_level = record.level
            game.placement = record.placement
            hero = template_id_dict[str(record.player_card_template_id)]["Name"]
            units = []
            treasures = []
            for character in record.characters:
                if character is None:
                    continue
                units.append(Unit.from_unit_struct(character))
            for treasure in record.treasures:
                if treasure is None:
                    continue
                treasures.append(Unit.from_unit_struct(treasure))
            board = Board(hero, units, treasures)
            game.final_board = board
        if action_name == "ActionAddPlayer":
            player_hero = template_id_dict[str(record.template_id)]["Name"]
            player = Player(player_hero, record.health, record.level, record.experience, record.player_name, record.player_id)
            if game.game_over:
                game.final_results.append(player)
            elif game.turn > 0:
                game.leaderboards[-1].append(player)
    return game


def get_build_id_from_record_file(filename):
    with open(filename, 'rb') as f:
        result = GreedyRange(STRUCT_ACTION).parse_stream(f)
        remaining_binary_contents = f.read()
    if len(remaining_binary_contents) != 0:
        print("Could not parse entire record file successfully.")
        # raise RuntimeError("Could not parse entire record file successfully.")
    player_id = None
    player_name = None
    build_id = None
    for record in result:
        if id_to_action_name[record.action_id] == "ActionAddPlayer" and player_id is None:
            if record.player_name not in ['ForgottenArbiter', 'Forgotten Arbiter', 'Quincunx']:
                continue
            player_id = record.player_id
            player_name = record.player_name
        if id_to_action_name[record.action_id] == "ActionConnectionInfo":
            build_id = record.build_id
    return player_id, player_name, build_id


def extract_endgame_stats_from_record_file(filename):
    with open(filename, 'rb') as f:
        result = GreedyRange(STRUCT_ACTION).parse_stream(f)
        remaining_binary_contents = f.read()
    if len(remaining_binary_contents) != 0:
        raise RuntimeError("Could not parse entire record file successfully.")
    players = []
    mmr_change = 0
    game_over = False
    board = []
    treasures = []
    for record in result:
        action_name = id_to_action_name[record.action_id]
        if action_name == "ActionEnterResultsPhase":
            mmr_change = record.rank_reward
            game_over = True
            for character in record.characters:
                if character is None:
                    continue
                if character.is_golden:
                    board.append(Unit(character.health, character.attack, template_id_dict[str(character.template_id - 1)]["Name"]))
                else:
                    board.append(Unit(character.health, character.attack, template_id_dict[str(character.template_id)]["Name"]))
            for treasure in record.treasures:
                if treasure is None:
                    continue
                treasures.append(template_id_dict[str(treasure.template_id)]["Name"])

        if game_over and action_name == "ActionAddPlayer":
            player_hero = template_id_dict[str(record.template_id)]["Name"]
            players.append((record.player_name, player_hero, record.place))
    players.sort(key=lambda x: x[2])
    print("Final board: ")
    pprint.pprint(board)
    print("Treasures: ")
    pprint.pprint(treasures)
    print("Final placements: ")
    pprint.pprint(players)
    print("MMR gained: {}".format(mmr_change))
    print("#################################")


def shop_has_card_name(shop: List[Unit], card_name: str):
    for unit in shop:
        if unit.name == card_name:
            return True
    return False


if __name__ == "__main__":
    save_dir = pathlib.Path(os.environ["APPDATA"]).parent.joinpath("LocalLow/Good Luck Games/Storybook Brawl")
    filenames = save_dir.glob("record_*.txt")
    sorted_by_recent = sorted(filenames, key=os.path.getctime, reverse=True)
    most_recent_games = sorted_by_recent[:200]
    has_tree = 0
    bought_tree = 0
    total_placement_has_tree = 0
    total_placement_bought_tree = 0
    total_placement_overall = 0
    games = []
    for game in most_recent_games:
        # Restricted to my games from the current patch
        if datetime.datetime.fromtimestamp(os.path.getctime(game)) < datetime.datetime.fromisoformat("2022-02-12"):
            break
        games.append(extract_game_from_record_file(game))
        # extract_endgame_stats_from_record_file(game)
        # time = datetime.datetime.fromtimestamp(os.path.getctime(game)).strftime('%Y-%m-%dT%H:%M:%S')
        # print(time, get_build_id_from_record_file(game))
    pickle.dump(games, open("games.pkl", "wb"))
