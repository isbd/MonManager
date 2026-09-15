from enum import StrEnum


class EventType(StrEnum):
    """Enums for websocket events."""

    CHALLENGE_RECEIVED = "challenge_received"
    CHALLENGE_RESPONSE = "challenge_response"
    CHALLENGE_CANCELED = "challenge_canceled"
    ROUND_PENDING_YOUR_MOVE = "round_pending_your_move"
    ROUND_RESOLVED = "round_resolved"
    ENCOUNTER_OVER = "encounter_over"
    BATTLE_FORFEITED = "battle_forfeited"
    TURN_NOTIFICATION = "turn_notificiation"
    SOCKET_CLOSED = "challenge_result"
