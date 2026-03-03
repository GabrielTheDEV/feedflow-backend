from enum import Enum

class Plan(str, Enum):
    free = "free"
    started = "started"
    growth = "growth"
    premium = "premium"