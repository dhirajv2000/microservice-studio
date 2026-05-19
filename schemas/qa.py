from pydantic import BaseModel, Field


class QAVerdict(BaseModel):
    passed: bool = Field(description="True if all tests passed")
    test_code: str = Field(description="The final test code that was run (for the output zip)")
    summary: str = Field(description="One-line summary of the test results")