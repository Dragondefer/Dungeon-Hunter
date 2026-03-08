from os.path import exists

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
    if exists("ai/agent_wrapper.py"):
        from ai.agent_wrapper import get_agent
        agent_instance = get_agent()
        DEV_AGENT_MODE = True
except Exception as e:
    agent_instance = None
    DEV_AGENT_MODE = False


# AI dev integration
import os

agent_is_enabled = lambda *args, **kwargs: None
get_agent = lambda *args, **kwargs: None
aw = None

def setup_ai(choice):
    global agent_is_enabled, get_agent, aw
    try:
        if os.path.exists("./ai/agent.py") and os.path.exists("./ai/agent_wrapper.py"):
            try:
                from ai.agent_wrapper import agent_is_enabled as real_agent_is_enabled
                import ai.agent_wrapper as aw_module
                from ai.agent_wrapper import get_agent as real_get_agent
                agent_is_enabled = real_agent_is_enabled
                get_agent = real_get_agent
                aw = aw_module
            except Exception as e:
                print("Cannot import agent_wrapper")
            if choice == "y" and aw:
                aw.enable_agent()
            else:
                if aw: aw.disable_agent()
        else:
            pass
    except Exception as e:
        pass


# Developer mode flag

dev_mode = False

def set_dev_mode(enabled: bool):
    global dev_mode
    dev_mode = enabled

def is_dev_mode() -> bool:
    return dev_mode

