# Dungeon Hunter - (c) Dragondefer 2025
# Licensed under CC BY-NC 4.0

from sys import path
from os.path import abspath, dirname, join
# Define the root of the project
path.append(abspath(join(dirname(__file__), '..')))

from .difficulty import (
    Difficulty,
    HardcoreDifficulty,
    NormalDifficulty,
    SoulsDifficulty,
    RealisticDifficulty,
    PuzzleDifficulty
)

