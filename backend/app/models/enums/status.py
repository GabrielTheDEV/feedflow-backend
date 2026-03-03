from enum import Enum

class Status(str, Enum):
    working = "working"
    paused = "paused"
    stopped = "stopped"
