import os
import pathlib
import pprint
import json

from construct import GreedyRange

from record_parser import STRUCT_ACTION, id_to_action_name


# Copied from SBB Tracker's template ID mapping
# (https://github.com/SBBTracker/SBBTracker/blob/main/assets/template-ids.json)
template_id_dict = json.load(open("template-ids.json", 'r'))


class Unit:

    def __init__(self, health, attack, name):
        self.health = health
        self.attack = attack
        self.name = name

    def __repr__(self):
        return "{} ({}/{})".format(self.name, self.attack, self.health)


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


if __name__ == "__main__":
    save_dir = pathlib.Path(os.environ["APPDATA"]).parent.joinpath("LocalLow/Good Luck Games/Storybook Brawl")
    filenames = save_dir.glob("record_*.txt")
    sorted_by_recent = sorted(filenames, key=os.path.getctime, reverse=True)
    most_recent_games = sorted_by_recent[:3]
    for game in most_recent_games:
        extract_endgame_stats_from_record_file(game)
