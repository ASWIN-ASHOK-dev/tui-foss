"""Tests for Aswin's quest data. Independent of engine/UI code."""
import pytest

from cybershell.game.quests import (
    ALLOWED_PREDICATES,
    FIELD_MANUAL,
    QUEST_DATA,
    STORY_INTRO,
)


def _vfs_has(vfs, path):
    node = vfs
    for part in [p for p in path.split("/") if p]:
        if not isinstance(node, dict) or node.get("_type") == "file" or part not in node:
            return False
        node = node[part]
    return True


def test_six_sectors_in_order():
    assert len(QUEST_DATA) == 6
    assert [q["index"] for q in QUEST_DATA] == [0, 1, 2, 3, 4, 5]


def test_unique_ids():
    quest_ids = [q["id"] for q in QUEST_DATA]
    obj_ids = [o["id"] for q in QUEST_DATA for o in q["objectives"]]
    loot_ids = [q["loot"]["id"] for q in QUEST_DATA]
    assert len(set(quest_ids)) == 6
    assert len(set(obj_ids)) == len(obj_ids)
    assert len(set(loot_ids)) == 6


@pytest.mark.parametrize("quest", QUEST_DATA, ids=lambda q: q["id"])
def test_quest_shape(quest):
    for key in ("name", "npc", "intro", "outro", "start_cwd", "vfs", "loot"):
        assert quest[key], f"{quest['id']} missing {key}"
    assert len(quest["objectives"]) == 3
    for o in quest["objectives"]:
        assert o["description"] and o["hint"]
        assert o["xp"] > 0
        assert o["check"][0] in ALLOWED_PREDICATES


@pytest.mark.parametrize("quest", QUEST_DATA, ids=lambda q: q["id"])
def test_start_cwd_exists(quest):
    assert _vfs_has(quest["vfs"], quest["start_cwd"]) or quest["start_cwd"].startswith("/home")


@pytest.mark.parametrize("quest", QUEST_DATA, ids=lambda q: q["id"])
def test_check_targets_are_reachable(quest):
    """Predicates that inspect existing things must point at real paths."""
    for o in quest["objectives"]:
        name, path = o["check"][0], o["check"][1]
        if name in ("file_not_exists", "permission_equals"):
            assert _vfs_has(quest["vfs"], path), f"{o['id']} targets missing {path}"


def test_boss_has_three_timed_stages():
    boss = QUEST_DATA[5]
    hp = [o["boss_hp_pct"] for o in boss["objectives"]]
    assert all(o["time_limit_s"] > 0 for o in boss["objectives"])
    assert hp == sorted(hp, reverse=True)
    assert hp[-1] == 0


def test_field_manual_and_story():
    assert "COMMAND BASICS" in FIELD_MANUAL
    assert "chmod" in FIELD_MANUAL
    assert len(STORY_INTRO) > 50
