from pydantic import BaseModel, Field
class SecurityVerdict(BaseModel):
    approved: bool = Field(description="True only if zero real security issues were found")
    issues: list[str] = Field(
        default_factory=list,
        description="List of concrete security issues, one per line. Empty if approved.",
    )