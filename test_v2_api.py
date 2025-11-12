"""Test file to understand Mirascope v2 API changes."""
from mirascope import llm
from pydantic import BaseModel, Field


# Test 1: Simple functional prompt (v2 pattern)
@llm.prompt
def simple_prompt(question: str) -> str:
    return f"Answer this question: {question}"


# Test 2: LLM call with response model (format replaces response_model)
class Answer(BaseModel):
    response: str = Field(..., description="The answer")
    confidence: float = Field(..., description="Confidence score")


@llm.call(provider="openai:completions", model_id="gpt-4o-mini", format=Answer)
async def answer_question(question: str) -> str:
    return f"Answer: {question}"


# Test 3: Tool definition
@llm.tool
def search_web(query: str) -> str:
    """Search the web for information.

    Args:
        query: Search query

    Returns:
        Search results
    """
    return f"Mock results for: {query}"


# Test 4: Context-based prompt
@llm.prompt
def context_prompt(ctx: llm.Context[str], question: str) -> str:
    return f"Using context {ctx.deps}, answer: {question}"


if __name__ == "__main__":
    # Test imports
    print("✓ Imports successful")

    # Test simple prompt
    messages = simple_prompt(question="What is AI?")
    print(f"✓ Simple prompt: {len(messages)} messages")

    # Test tool
    result = search_web(query="test")
    print(f"✓ Tool result: {result}")

    # Test context prompt
    ctx = llm.Context(deps="Some context")
    messages = context_prompt(ctx=ctx, question="What is AI?")
    print(f"✓ Context prompt: {len(messages)} messages")

    print("\nAll v2 API tests passed!")
