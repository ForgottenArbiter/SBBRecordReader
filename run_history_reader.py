from __future__ import annotations

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

    def __init__(self, health, attack, name, zone):
        self.health = health
        self.attack = attack
        self.name = name
        self.zone = zone

    def __repr__(self):
        return "{} ({}/{})".format(self.name, self.attack, self.health)

    @classmethod
    def from_unit_struct(cls, unit_struct):
        if unit_struct is None:
            return None
        health = unit_struct.health
        attack = unit_struct.attack
        if unit_struct.is_golden:
            name = template_id_dict[str(unit_struct.template_id - 1)]["Name"]
        elif str(unit_struct.template_id) in template_id_dict:
            name = template_id_dict[str(unit_struct.template_id)]["Name"]
        else:
            name = "Unknown"
        zone = unit_struct.zone
        return cls(health, attack, name, zone)


class Board:

    def __init__(self, hero, units, treasures):
        self.hero = hero
        self.units = units
        self.treasures = treasures


class Game:

    def __init__(self):
        self.shops = []
        self.bought = []
        self.boards = []
        self.enemy_boards = []
        self.spells = []
        self.turn = 0
        self.mmr_change = 0
        self.game_over = False
        self.final_results = []
        self.placement = 0

    def start_new_turn(self):
        self.turn += 1
        self.shops.append([])
        self.bought.append([])
        self.spells.append([])

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
        raise RuntimeError("Could not parse entire record file successfully.")
    game = Game()
    all_cards = {}
    iterator = iter(result)
    for record in iterator:
        action_name = id_to_action_name[record.action_id]
        if action_name in ["ActionUpdateCard", "ActionCreateCard"]:
            card = Unit.from_unit_struct(record.card)
            all_cards[record.card.card_id] = card
        if action_name in ["ActionEnterShopPhase", "ActionRoll"]:
            if action_name == "ActionEnterShopPhase":
                game.start_new_turn()
            shop = []
            record = next(iterator)
            while (action_name := id_to_action_name[record.action_id]) in \
                    ["ActionModifyXP", "ActionModifyLevel", "ActionModifyNextLevelXP", "ActionUpdateCard", "ActionRemoveCard", "ActionCreateCard", "ActionModifyGold", "ActionPlayFX", "ActionPresentDiscover"]:
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
            pass  # TODO: Finish this
        if action_name == "ActionMoveCard":
            if all_cards[record.card_id].zone == "shop" and record.target_zone == "character":
                game.bought[-1][-1].append(all_cards[record.card_id])
        if action_name == "ActionCastSpell":
            game.cast_spell(all_cards[record.card_id])
        if action_name == "ActionEnterResultsPhase":
            game.mmr_change = record.rank_reward
            game.game_over = True
            game.placement = record.placement
        if game.game_over and action_name == "ActionAddPlayer":
            player_hero = template_id_dict[str(record.template_id)]["Name"]
            game.final_results.append((record.player_name, player_hero, record.place))
    return game


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
    most_recent_games = sorted_by_recent[:100]
    has_tree = 0
    bought_tree = 0
    total_placement_has_tree = 0
    total_placement_bought_tree = 0
    total_placement_overall = 0
    for game in most_recent_games:
        # extract_endgame_stats_from_record_file(game)
        parsed_game = extract_game_from_record_file(game)
        placement = parsed_game.placement
        total_placement_overall += placement
        if shop_has_card_name(parsed_game.shops[0][0], "Happy Little Tree"):
            has_tree += 1
            total_placement_has_tree += placement
            if shop_has_card_name(parsed_game.bought[0][0], "Happy Little Tree"):
                bought_tree += 1
                total_placement_bought_tree += placement
    print(has_tree)
    print(bought_tree)
    print(total_placement_has_tree / has_tree)
    print(total_placement_bought_tree / bought_tree)
    print(total_placement_overall / 100)
