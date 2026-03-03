from enum import Enum


class IntegrationService(str, Enum):
    slack = "slack"
    jira = "jira"
    trello = "trello"