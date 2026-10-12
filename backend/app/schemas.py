"""
Pydantic request/response schemas for the chat API.

All user-facing models are defined here so both the API layer and tests
can import from a single source of truth.
"""

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Incoming chat question from the user."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The user's question about the book content.",
    )

    @field_validator("question", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip leading/trailing whitespace before length validation."""
        if isinstance(v, str):
            return v.strip()
        return v


class Source(BaseModel):
    """A single book passage that contributed to the answer."""

    title: str = Field(description="Chapter or section title.")
    section: str = Field(description="Sub-section heading, if available.")
    path: str = Field(description="Docusaurus URL path for this page.")
    score: float = Field(description="Cosine similarity score [0, 1].")


class ChatResponse(BaseModel):
    """Response returned by POST /api/chat."""

    answer: str = Field(description="The answer text (or refusal message).")
    grounded: bool = Field(
        description=(
            "True when the answer is grounded in retrieved book content; "
            "False when no evidence was found and the refusal message is returned."
        )
    )
    sources: list[Source] = Field(
        default_factory=list,
        description="Book passages used to generate the answer.",
    )


class ErrorResponse(BaseModel):
    """Standard error envelope returned for all non-2xx responses."""

    detail: str = Field(description="Human-readable error description.")
    # Never include stack traces, secrets, or internal paths here.
