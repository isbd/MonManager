from enum import StrEnum


class EventType(StrEnum):
    CHALLENGE_RECEIVED = "challenged_received"
    CHALLENGE_RESPONSE = "challenge_response"
    CHALLENGE_CANCELED = "challenge_canceled"
    TURN_NOTIFICATION = "turn_notificiation"
    SOCKET_CLOSED = "challenge_result"
