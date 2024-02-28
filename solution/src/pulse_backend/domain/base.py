from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ErrorResponse:
    reason: str
