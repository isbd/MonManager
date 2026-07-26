from enum import StrEnum


class EventType(StrEnum):
    CHALLENGE_RECEIVED = "challenged_received"
    CHALLENGE_RESPONSE = "challenge_response"
    CHALLENGE_CANCELED = "challenge_canceled"
    ROUND_PENDING_YOUR_MOVE = "round_pending_your_move"
    ROUND_RESOLVED = "round_resolved"
    TURN_NOTIFICATION = "turn_notificiation"
    SOCKET_CLOSED = "challenge_result"
