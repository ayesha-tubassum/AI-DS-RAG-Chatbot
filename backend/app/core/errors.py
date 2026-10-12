"""
Custom exception types for the backend.

Keeping exceptions in one place ensures consistent error messages and
makes it easy to add structured logging or Sentry capture later.
"""


class NotConfiguredError(Exception):
    """
    Raised when a feature is called but the required configuration
    (API key, service URL, etc.) is missing from the environment.

    This is intentionally NOT an HTTP exception — the API layer translates
    it into a 503 response so internal configuration details are never
    exposed to callers.
    """

    def __init__(self, feature: str, missing_vars: list[str]) -> None:
        self.feature = feature
        self.missing_vars = missing_vars
        # The message names the feature, but NOT the secret values.
        super().__init__(
            f"Feature '{feature}' is not available: "
            f"missing environment variable(s): {', '.join(missing_vars)}"
        )


class RetrievalError(Exception):
    """
    Raised when a Qdrant search fails at the network/protocol level
    (distinct from "no results found", which is a valid empty response).
    """

    def __init__(self, message: str) -> None:
        super().__init__(f"Vector search failed: {message}")


class EmbeddingError(Exception):
    """Raised when the embedding API call fails."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Embedding generation failed: {message}")


class GenerationError(Exception):
    """Raised when the answer-generation API call fails."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Answer generation failed: {message}")
