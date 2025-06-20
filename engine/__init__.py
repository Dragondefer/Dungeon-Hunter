from sys import path
from os.path import abspath, dirname, join
# Define the root of the project
path.append(abspath(join(dirname(__file__), '..')))

from .difficulty import (
    GameMode,
    HardcoreMode,
    NormalMode,
    SoulsEnjoyerMode,
    RealisticMode,
    PuzzleMode
)
