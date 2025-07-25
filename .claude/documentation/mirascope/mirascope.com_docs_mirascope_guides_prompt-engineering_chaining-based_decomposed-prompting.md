---
url: "https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/decomposed-prompting"
title: "Decomposed Prompting: Enhancing LLM Problem-Solving with Tool-Based Subproblems | Mirascope"
---

# Decomposed Prompting: Enhancing LLM Problem-Solving with Tool-Based Subproblems [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/decomposed-prompting\#decomposed-prompting-enhancing-llm-problem-solving-with-tool-based-subproblems)

This recipe demonstrates how to implement the Decomposed Prompting (DECOMP) technique using Large Language Models (LLMs) with Mirascope. DECOMP is a prompt engineering method that enhances an LLM's problem-solving capabilities by breaking down complex problems into subproblems and utilizing tools to solve each step.

Mirascope Concepts Used

Background

[Decomposed Prompting](https://arxiv.org/pdf/2210.02406) (DECOMP) is an extension of [least-to-most](https://arxiv.org/abs/2205.10625) whereby tools are used to execute each subproblem in the problem solving process. A pre-trained call (in our case, a one shot prompt) demonstrates how to break a problem down into subproblems within the context of its given tool calls, and the output of each tool call is added to the chat's history until the problem is solved. Just like least-to-most, DECOMP shows improvements on mathematical reasoning and symbolic manipulation tasks, with better results than least-to-most.

## Implementation [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/decomposed-prompting\#implementation)

Let's implement the Decomposed Prompting technique using Mirascope:

```
import json

from mirascope.core import openai, prompt_template
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field

class Problem(BaseModel):
    subproblems: list[str] = Field(
        ..., description="The subproblems that the original problem breaks down into"
    )

@openai.call(model="gpt-4o", response_model=Problem)
@prompt_template(
    """
    Your job is to break a problem into subproblems so that it may be solved
    step by step, using at most one function call at each step.

    You have access to the following functions which you can use to solve a
    problem:
    split: split a string into individual words
    substring: get the ith character of a single string.
    concat: concatenate some number of strings.

    Here is an example of how it would be done for the problem: Get the first two
    letters of the phrase 'Round Robin' with a period and space in between them.
    Steps:
    split 'Round Robin' into individual words
    substring the 0th char of 'Round'
    substring the 0th char of 'Robin'
    concat ['R', '.', ' ', 'R']

    Now, turn this problem into subtasks:
    {query}
    """
)
def break_into_subproblems(query: str): ...

def split_string_to_words(string: str) -> str:
    """Splits a string into words."""
    return json.dumps(string.split())

def substring(index: int, string: str) -> str:
    """Gets the character at the index of a string."""
    return string[index]

def concat(strings: list[str]) -> str:
    """Concatenates some number of strings."""
    return "".join(strings)

@openai.call(model="gpt-4o-mini", tools=[split_string_to_words, substring, concat])
@prompt_template(
    """
    SYSTEM: You are being fed subproblems to solve the actual problem: {query}
    MESSAGES: {history}
    """
)
def solve_next_step(history: list[ChatCompletionMessageParam], query: str): ...

def decomposed_prompting(query: str):
    problem = break_into_subproblems(query=query)
    response = None
    history: list[ChatCompletionMessageParam] = []
    for subproblem in problem.subproblems:
        history.append({"role": "user", "content": subproblem})
        response = solve_next_step(history, query)
        history.append(response.message_param)
        if tool := response.tool:
            output = tool.call()
            history += response.tool_message_params([(tool, output)])
            response = solve_next_step(history, query)

            # This should never return another tool call in DECOMP so don't recurse
            history.append(response.message_param)
    return response

query = """Take the last letters of the words in "Augusta Ada King" and concatenate them using a space."""

print(decomposed_prompting(query))
```

The concatenated characters are "aag".

This implementation consists of several key components:

1. `Problem` class: Defines the structure for breaking down a problem into subproblems.
2. `break_into_subproblems`: Uses GPT-4o-mini to break the main problem into subproblems.
3. Tool functions: `split`, `substring`, and `concat` for manipulating strings.
4. `solve_next_step`: Uses GPT-3.5-turbo to solve each subproblem, utilizing the available tools.
5. `decomposed_prompting`: Orchestrates the entire process, solving subproblems sequentially and maintaining conversation history.

## Benefits and Considerations [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/decomposed-prompting\#benefits-and-considerations)

The Decomposed Prompting implementation offers several advantages:

1. Improved problem-solving capabilities for complex tasks.
2. Better handling of multi-step problems that require different operations.
3. Increased transparency in the problem-solving process.
4. Potential for solving problems that are beyond the scope of a single LLM call.

When implementing this technique, consider:

- Carefully designing the set of available tools to cover a wide range of problem-solving needs.
- Balancing the complexity of subproblems with the capabilities of the chosen LLM.
- Implementing error handling and recovery mechanisms for cases where a subproblem solution fails.
- Optimizing the prompt for breaking down problems to ensure effective decomposition.

Additional Real-World Applications

- **Code Generation**: Break down complex programming tasks into smaller, manageable steps.
- **Data Analysis**: Decompose complex data analysis queries into a series of data manipulation and calculation steps.
- **Natural Language Processing**: Break down complex NLP tasks like sentiment analysis or named entity recognition into subtasks.
- **Automated Reasoning**: Solve complex logical or mathematical problems by breaking them into simpler, solvable steps.
- **Task Planning**: Create detailed, step-by-step plans for complex projects or processes.

When adapting this recipe to your specific use-case, consider:

- Tailoring the available tools to your domain for better performance.
- Implementing a feedback loop to refine the problem decomposition process based on solution accuracy.
- Combining Decomposed Prompting with other techniques like Chain of Thought for even more powerful problem-solving capabilities.
- Developing a mechanism to handle interdependencies between subproblems.

By leveraging Mirascope's `call` decorator, response models, and dynamic configuration, you can easily implement and customize the Decomposed Prompting technique to enhance your LLM's problem-solving capabilities across a wide range of applications.

Copy as Markdown

#### Provider

OpenAI

#### On this page

Copy as Markdown

#### Provider

OpenAI

#### On this page

## Cookie Consent

We use cookies to track usage and improve the site.

RejectAccept