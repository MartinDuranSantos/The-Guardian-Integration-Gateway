import asyncio
import time
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(Exception):
    """Raised when the circuit breaker is OPEN and a call is attempted."""
    pass


class CircuitBreaker:
    """
    Async circuit breaker. After `failure_threshold` consecutive failures,
    the circuit snaps OPEN and instantly rejects calls with a fallback.
    After `recovery_timeout` seconds, it enters HALF_OPEN to test recovery.
    """

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self._lock = asyncio.Lock()

    async def call(self, func, *args, **kwargs):
        # ── Fast-fail check (no lock held during I/O) ───────────────────────
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self.last_failure_time and (time.time() - self.last_failure_time) >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitBreakerOpenError("Service Busy")

        # ── Execute protected function ──────────────────────────────────────
        try:
            result = await func(*args, **kwargs)
            async with self._lock:
                self._on_success()
            return result
        except Exception as e:
            async with self._lock:
                self._on_failure()
            raise e

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN