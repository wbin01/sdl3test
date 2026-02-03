#!/usr/bin/env python3
from enum import Enum


class ResizeRegion(Enum):
    """..."""
    NONE = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3
    LEFT = 4
    TOPLEFT = 5
    TOPRIGHT = 6
    BOTTOMLEFT = 7
    BOTTOMRIGHT = 8

    def __repr__(self) -> str:
        return self.__class__.__name__
