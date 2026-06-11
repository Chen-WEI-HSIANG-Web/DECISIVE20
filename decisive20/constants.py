from __future__ import annotations

"""Shared constants, status vocabulary, and display labels for Decisive 20."""


class ZoneStatus:
    FRIENDLY = "friendly"
    CONTESTED = "contested"
    ENEMY_CONTROLLED = "enemy_controlled"
    CUT_OFF = "cut_off"
    DESTROYED = "destroyed"

    ALL = {FRIENDLY, CONTESTED, ENEMY_CONTROLLED, CUT_OFF, DESTROYED}
    # Statuses the enemy can meaningfully assault.
    ATTACKABLE = {FRIENDLY, CONTESTED, CUT_OFF}


# How a zone degrades one step when an enemy assault succeeds.
DEGRADE_STATUS = {
    ZoneStatus.FRIENDLY: ZoneStatus.CONTESTED,
    ZoneStatus.CONTESTED: ZoneStatus.ENEMY_CONTROLLED,
    ZoneStatus.CUT_OFF: ZoneStatus.ENEMY_CONTROLLED,
    ZoneStatus.ENEMY_CONTROLLED: ZoneStatus.ENEMY_CONTROLLED,
    ZoneStatus.DESTROYED: ZoneStatus.DESTROYED,
}

STATUS_LABELS = {
    ZoneStatus.FRIENDLY: "我方控制",
    ZoneStatus.CONTESTED: "爭奪中",
    ZoneStatus.ENEMY_CONTROLLED: "敵方控制",
    ZoneStatus.CUT_OFF: "被切斷",
    ZoneStatus.DESTROYED: "已破壞",
}


class Ending:
    VICTORY = "victory"
    FAILURE = "failure"
    INCOMPLETE = "incomplete"


# --------------------------------------------------------------------------- #
# Balance knobs
# --------------------------------------------------------------------------- #
# Intel needed before the next enemy assault's targets are revealed to the
# player (the "recon / telegraph" loop). Investing in recon buys foresight;
# spending intel on counter-ops gives it up.
INTEL_TELEGRAPH_THRESHOLD = 4

# Command Point cost to deploy (or redeploy) a force to a zone.
DEPLOY_CP_COST = 1


VALID_VICTORY_TYPES = {
    "survive_rounds",
    "hold_min_core_zones",
    "enemy_pressure_zero",
}

VALID_FAILURE_TYPES = {
    "morale_zero",
    "political_pressure_max",
    "enemy_controls_zones",
    "supply_zero",
    "core_zones_lost",
}

SUPPORTED_EFFECT_KEYS = {
    "supply",
    "intel",
    "morale",
    "political_pressure",
    "enemy_pressure",
    "cp",
    "zone_defense",
    "zone_status",
    "force_value",
}

# Resource fields that are clamped to the 0..100 band.
BOUNDED_RESOURCES = {"morale", "political_pressure"}

# ANSI colors, keyed by status; used only when color output is enabled.
STATUS_COLORS = {
    ZoneStatus.FRIENDLY: "92",        # bright green
    ZoneStatus.CONTESTED: "93",       # yellow
    ZoneStatus.ENEMY_CONTROLLED: "91",  # red
    ZoneStatus.CUT_OFF: "95",         # magenta
    ZoneStatus.DESTROYED: "90",       # grey
}
