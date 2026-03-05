import os

# Global game speed setting and multipliers
game_speed = "normal"
speed_multipliers: dict[str, float] = {
    "slow": 2.0,
    "normal": 1.0,
    "fast": 0.5,
    "instant": 0.0
}

# Global game speed multiplier, default 1.0 (normal speed)
game_speed_multiplier = 1.0

def set_game_speed_multiplier(multiplier: float):
    global game_speed_multiplier
    game_speed_multiplier = multiplier


# Agent managment for DEVS

try:
    DEV_AGENT_MODE = False
    if os.path.exists("ai/agent_wrapper.py"):
        from ai.agent_wrapper import get_agent
        agent_instance = get_agent()
        DEV_AGENT_MODE = True
except Exception as e:
    agent_instance = None
    DEV_AGENT_MODE = False


# Developer mode flag

dev_mode = False

def set_dev_mode(enabled: bool):
    global dev_mode
    dev_mode = enabled

def is_dev_mode() -> bool:
    return dev_mode

