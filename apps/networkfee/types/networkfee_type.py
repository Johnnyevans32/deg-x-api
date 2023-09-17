from enum import Enum


class TxnSpeedOption(str, Enum):
    SLOW = "slow"
    STANDARD = "standard"
    FAST = "fast"
    INSTANT = "instant"
