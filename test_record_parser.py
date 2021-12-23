import record_parser
from typing import Tuple
import os
import math
import pytest

def load_binary_file(base_filename: str) -> bytes:
    binary_filename = base_filename + ".bin"
    binary_filename = os.path.join("test_samples", binary_filename)
    with open(binary_filename, 'rb') as f:
        binary_contents = f.read()
    return binary_contents


def test_action_enter_intro_phase():
    filename = "ActionEnterIntroPhase"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_ENTER_INTRO_PHASE.parse(binary)
    assert result is not None
    assert result.timestamp == 1


def test_action_add_player():
    filename = "ActionAddPlayer"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_ADD_PLAYER.parse(binary)
    assert result.timestamp == 12
    assert result.player_id == "429402B2E2AD1FA4"
    assert result.player_name == "Forgotten Arbiter"
    assert result.health == 40
    assert result.gold == 0
    assert result.experience == 0
    assert result.next_level_xp == 3
    assert result.level == 2
    assert result.place == 1
    assert result.card_id == "a32cee0ae050462d9b6cd0bc7815a347"
    assert result.template_id == 76


def test_action_attack():
    filename = "ActionAttack"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_ATTACK.parse(binary)
    assert result.timestamp == 185
    assert result.attacker == "ea8330c51fdf43759488e2590d9b8544"
    assert result.defender == "b14c29aeee334a1fabbb48ab3780eccb"


def test_action_brawl_complete():
    filename = "ActionBrawlComplete"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_BRAWL_COMPLETE.parse(binary)
    assert result.timestamp == 89
    assert result.round == 3
    assert result.player_id_1 == "DC2FAD1B1AA1679B"
    assert result.player_id_2 == "429402B2E2AD1FA4"


def test_action_cast_spell():
    filename = "ActionCastSpell"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_CAST_SPELL.parse(binary)
    assert result.timestamp == 130
    assert result.card_id == "436596ba5b124d66aeacd416f3d34422"
    assert result.target == "00000000000000000000000000000000"


def test_action_connection_info():
    filename = "ActionConnectionInfo"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_CONNECTION_INFO.parse(binary)
    assert result.timestamp == 4
    assert result.session_id == "81feb47c-320f-4b31-9cfc-d920a8f0d348"
    assert result.build_id == "65db41ce-7e96-4290-b951-e8713e8bd5bd"
    assert result.server_ip == "037d8616c36c65f798f63a4a27612b9e1663440034e55adb46c98516c347b1bd"


def test_action_create_card():
    filename = "ActionCreateCard"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_CREATE_CARD.parse(binary)
    assert result.timestamp == 10
    assert result.card.card_id == "a32cee0ae050462d9b6cd0bc7815a347"
    assert result.card.template_id == 76
    assert result.card.health == 40
    assert result.card.frame_override == "HEROFRAME_EARLYACCESS"
    assert result.card.player_id == "429402B2E2AD1FA4"


def test_action_deal_damage():
    filename = "ActionDealDamage"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_DEAL_DAMAGE.parse(binary)
    assert result.timestamp == 90
    assert result.target == "a32cee0ae050462d9b6cd0bc7815a347"
    assert result.source == "8541cfe6ba1542158f95e7649553f7d8"
    assert result.damage == 3


def test_action_death():
    filename = "ActionDeath"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_DEATH.parse(binary)
    assert result.timestamp == 188
    assert result.target == "b14c29aeee334a1fabbb48ab3780eccb"


def test_action_emote():
    filename = "ActionEmote"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_EMOTE.parse(binary)
    assert result.timestamp == 3622
    assert result.player_id == "A4CDF2864679BCAC"
    assert result.emote_name == "EMOTE_HAPPY"


def test_action_enter_brawl_phase():
    filename = "ActionEnterBrawlPhase"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_ENTER_BRAWL_PHASE.parse(binary)
    assert result.timestamp == 83
    assert result.player_1_id == "DC2FAD1B1AA1679B"
    assert result.player_1_name == "Andy"
    assert result.player_1_health == 38
    assert result.player_1_card_id == "8541cfe6ba1542158f95e7649553f7d8"
    assert result.player_1_card_template_id == 56
    assert result.player_2_id == "429402B2E2AD1FA4"
    assert result.player_2_name == "Forgotten Arbiter"
    assert result.player_2_health == 40
    assert result.player_2_card_id == "a32cee0ae050462d9b6cd0bc7815a347"
    assert result.player_2_card_template_id == 76


def test_action_enter_results_phase():
    filename = "ActionEnterResultsPhase"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_ENTER_RESULTS_PHASE.parse(binary)
    assert result.timestamp == 8627
    assert result.health == 23
    assert result.gold == 12
    assert result.experience == 0
    assert result.next_level_xp == 0
    assert result.level == 6
    assert result.place == 1
    assert result.player_hero_id == "bdfca10d105c445498ea291cbd7b508a"
    assert result.rank_reward == 48
    assert result.crown_reward == 1
    assert result.placement == 1
    assert result.first_win_dust_reward == 0
    assert len(result.characters) == 7
    assert len(result.treasures) == 3
    assert result.characters[2] is None


def test_action_enter_shop_phase():
    filename = "ActionEnterShopPhase"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_ENTER_SHOP_PHASE.parse(binary)
    assert result.timestamp == 30
    assert result.health == 40
    assert result.player_id == "429402B2E2AD1FA4"
    assert result.player_name == "Forgotten Arbiter"
    assert result.player_card_id == "a32cee0ae050462d9b6cd0bc7815a347"
    assert result.player_card_template_id == 76
    assert result.opponent_id == "DC2FAD1B1AA1679B"
    assert result.round == 1
    assert result.gold == 2


def test_action_modify_gold():
    filename = "ActionModifyGold"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_MODIFY_GOLD.parse(binary)
    assert result.timestamp == 32
    assert result.player_id == "429402B2E2AD1FA4"
    assert result.amount == 2


def test_action_modify_level():
    filename = "ActionModifyLevel"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_MODIFY_LEVEL.parse(binary)
    assert result.timestamp == 359
    assert result.player_id == "429402B2E2AD1FA4"
    assert result.amount == 1


def test_action_modify_next_level_xp():
    filename = "ActionModifyNextLevelXP"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_MODIFY_NEXT_LEVEL_XP.parse(binary)
    assert result.timestamp == 360
    assert result.player_id == "429402B2E2AD1FA4"
    assert result.new_value == 3


def test_action_modify_xp():
    filename = "ActionModifyXP"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_MODIFY_XP.parse(binary)
    assert result.timestamp == 100
    assert result.player_id == "429402B2E2AD1FA4"
    assert result.amount == 1


def test_action_move_card():
    filename = "ActionMoveCard"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_MOVE_CARD.parse(binary)
    assert result.timestamp == 70
    assert result.card_id == "09aace0eb23343d0962b4cdc4db786eb"
    assert result.target_zone == "character"
    assert result.target_index == 5


def test_action_play_fx():
    filename = "ActionPlayFX"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_PLAY_FX.parse(binary)
    assert result.timestamp == 34
    assert result.source == "3b941d8732a54f208730285f50e58537"
    assert result.content_id == "FX_SHOPROLL_ENTER_01"
    assert len(result.targets) == 1
    assert result.targets[0] == "3b941d8732a54f208730285f50e58537"


def test_action_present_discover():
    filename = "ActionPresentDiscover"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_PRESENT_DISCOVER.parse(binary)
    assert result.timestamp == 1275
    assert len(result.treasures) == 3
    assert result.treasures[0].player_id == "429402B2E2AD1FA4"
    assert result.treasures[2].player_id == "429402B2E2AD1FA4"
    assert result.treasures[2].template_id == 142


def test_action_present_hero_discover():
    filename = "ActionPresentHeroDiscover"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_PRESENT_HERO_DISCOVER.parse(binary)
    assert result.timestamp == 2
    assert len(result.heroes) == 4
    assert result.heroes[0].card.card_id == "56e6bda386f9422ab65b790ac619332e"
    assert result.heroes[3].card.card_id == "b68158c84260476a90e97dfc711ea7ef"
    assert result.heroes[2].prices[1].price == 100
    assert result.heroes[1].card.player_id == "429402B2E2AD1FA4"
    assert result.heroes[1].card.health == 40


def test_action_remove_card():
    filename = "ActionRemoveCard"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_REMOVE_CARD.parse(binary)
    assert result.timestamp == 173
    assert result.card_id == "8528d9367364490a98e439cac8673afa"


def test_action_roll():
    filename = "ActionRoll"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_ROLL.parse(binary)
    assert result.timestamp == 608


def test_action_update_card():
    filename = "ActionUpdateCard"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_CARD.parse(binary)
    assert result.timestamp == 35
    assert result.card.card_id == "3b941d8732a54f208730285f50e58537"
    assert result.card.cost == 2
    assert result.card.health == 3
    assert result.card.attack == 0
    assert result.card.slot == 2
    assert result.card.damage == 0
    assert "support" in result.card.keywords
    assert "good" in result.card.subtypes
    assert "treant" in result.card.subtypes
    assert result.card.is_movable
    assert not result.card.is_golden
    assert result.card.zone == "shop"


def test_action_update_emotes():
    filename = "ActionUpdateEmotes"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_EMOTES.parse(binary)
    assert result.timestamp == 11
    assert result.player_id == "429402B2E2AD1FA4"
    assert len(result.emotes) == 6
    assert result.emotes[5].emote_name == "EMOTE_HAPPY"


def test_action_update_turn_timer():
    filename = "ActionUpdateTurnTimer"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_TURN_TIMER.parse(binary)
    assert result.is_enabled
    assert result.timestamp == 3
    assert result.seconds_remaining == 55
    assert math.isclose(result.timer, 7.757417, abs_tol=1e-6)


def test_update_card_0():
    filename = "UpdateCardExample0"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_CARD.parse(binary)
    assert result.card.template_id == 378
    assert result.card.zone == "shop"
    assert result.card.cost == 6
    assert result.card.damage == 0
    assert result.card.slot == 0
    assert not result.card.is_golden
    assert result.card.is_movable
    assert not result.card.makes_triple
    assert not result.card.makes_pair
    assert not result.card.is_locked
    assert "mage" in result.card.subtypes


def test_update_card_1():
    filename = "UpdateCardExample1"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_CARD.parse(binary)
    assert result.card.template_id == 112
    assert result.card.zone == "shop"
    assert result.card.cost == 2
    assert not result.card.is_golden
    assert result.card.is_movable
    assert "mage" in result.card.subtypes
    assert "animal" in result.card.subtypes
    assert len(result.card.subtypes) == 2


def test_update_card_2():
    filename = "UpdateCardExample2"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_CARD.parse(binary)
    assert "good" in result.card.subtypes
    assert "animal" in result.card.subtypes
    assert "prince" in result.card.subtypes
    assert len(result.card.subtypes) == 3
    assert len(result.card.keywords) == 0


def test_update_card_3():
    filename = "UpdateCardExample3"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_CARD.parse(binary)
    assert result.card.is_golden
    assert result.card.template_id == 113
    assert result.card.counter == -1


def test_update_card_4():
    filename = "UpdateCardExample4"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_CARD.parse(binary)
    assert "evil" in result.card.subtypes
    assert "mage" in result.card.subtypes
    assert "slay" in result.card.keywords
    assert result.card.slot == 5


def test_update_card_5():
    filename = "UpdateCardExample5"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_CARD.parse(binary)
    assert "dwarf" in result.card.subtypes
    assert result.card.slot == -1
    assert result.card.zone == "none"
    assert result.card.template_id == 193


def test_update_card_6():
    filename = "UpdateCardExample6"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_CARD.parse(binary)
    assert "egg" in result.card.subtypes


def test_update_card_7():
    filename = "UpdateCardExample7"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_CARD.parse(binary)
    assert len(result.card.subtypes) == 3
    assert "brawl_spell" in result.card.subtypes
    assert "damage_spell" in result.card.subtypes
    assert "random_spell" in result.card.subtypes


def test_update_card_8():
    filename = "UpdateCardExample8"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_CARD.parse(binary)
    assert len(result.card.subtypes) == 2
    assert "good" in result.card.subtypes
    assert "princess" in result.card.subtypes
    assert "ranged" in result.card.keywords


def test_update_card_9():
    filename = "UpdateCardExample9"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_UPDATE_CARD.parse(binary)
    assert len(result.card.subtypes) == 2
    assert "random_spell" in result.card.subtypes
    assert "beneficial_spell" in result.card.subtypes
    assert result.card.is_targeted
    assert result.card.is_movable
    assert len(result.card.valid_targets) == 10
    assert "1c364760a6e14b4cb26edd66376eba1e" in result.card.valid_targets


def test_create_card_alt_art():
    filename = "CreateCardAltArt"
    binary = load_binary_file(filename)
    result = record_parser.STRUCT_ACTION_CREATE_CARD.parse(binary)
    assert result.card.zone == "hero"
    assert result.card.art_id == "SKIN_HERO_DRAGONMOTHERGWEN"





