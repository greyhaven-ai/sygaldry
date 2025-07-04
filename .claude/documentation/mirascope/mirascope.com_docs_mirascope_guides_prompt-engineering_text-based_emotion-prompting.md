---
url: "https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/emotion-prompting"
title: "Emotion Prompting | Mirascope"
---

# Emotion Prompting [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/emotion-prompting\#emotion-prompting)

[Emotion Prompting](https://arxiv.org/pdf/2307.11760) is a prompt engineering technique where you end your original prompt with a phrase of psychological importance. It is most helpful for open ended tasks, but can still improve some analytical prompts:

Mirascope Concepts Used

```
from mirascope.core import openai, prompt_template

emotion_augment = "This is very important to my career."

@openai.call(model="gpt-4o-mini")
@prompt_template("{query} {emotion_augment}")
def call(query: str, emotion_prompt: bool = False) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "emotion_augment": emotion_augment if emotion_prompt else "",
        }
    }

prompt = """Write me an email I can send to my boss about how I need to
take a day off for mental health reasons."""

print(call(query=prompt, emotion_prompt=True))
```

Subject: Request for a Day Off

Dear \[Boss's Name\],

I hope this message finds you well. I am writing to formally request a day off for mental health reasons on \[specific date\]. I believe taking this time will allow me to recharge and return to work with renewed focus and energy.

I understand the importance of maintaining productivity and teamwork, and I will ensure that any pressing tasks are managed before my absence. I will also make sure to communicate with the team so that there are no disruptions.

Thank you for your understanding and support regarding my request. I’m committed to maintaining my well-being, which ultimately contributes to my overall performance and our team's success.

Best regards,

\[Your Name\]

\[Your Position\]

\[Your Contact Information\]

This example demonstrates how to implement emotion prompting using Mirascope. The `emotion_augment` variable contains the emotional phrase that will be added to the end of the prompt when `emotion_prompt` is set to `True`.

## Benefits of Emotion Prompting [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/emotion-prompting\#benefits-of-emotion-prompting)

1. **Increased Engagement**: Adding emotional context can make the LLM's responses more empathetic and engaging.
2. **Improved Relevance**: Emotional prompts can help guide the LLM to provide responses that are more relevant to the user's emotional state or needs.
3. **Enhanced Creativity**: For open-ended tasks, emotion prompting can lead to more creative and nuanced responses.
4. **Better Problem Solving**: In some cases, emotion prompting can help the LLM focus on more critical aspects of a problem or question.

Effective Emotion Prompting

- **Choose Appropriate Emotions**: Select emotional phrases that are relevant to the context of your query.
- **Be Authentic**: Use emotional prompts that genuinely reflect the importance or emotional weight of the task.
- **Experiment**: Try different emotional phrases to see which produces the best results for your specific use case.
- **Balance**: Be careful not to overuse emotional prompting, as it may not be appropriate for all types of queries.
- **Combine with Other Techniques**: Emotion prompting can be used in conjunction with other prompt engineering techniques for even better results.

By leveraging emotion prompting, you can guide the LLM to provide responses that are more emotionally attuned and potentially more helpful for tasks that benefit from emotional context.

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