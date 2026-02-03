#!/usr/bin/env python3
from enum import Enum


class ResizeRegion(Enum):
    """..."""
    NONE = 'NONE'
    TOP = 'TOP'
    RIGHT = 'RIGHT'
    BOTTOM = 'BOTTOM'
    LEFT = 'LEFT'
    TOPLEFT = 'TOPLEFT'
    TOPRIGHT = 'TOPRIGHT'
    BOTTOMLEFT = 'BOTTOMLEFT'
    BOTTOMRIGHT = 'BOTTOMRIGHT'

    def __repr__(self) -> str:
        return self.__class__.__name__
