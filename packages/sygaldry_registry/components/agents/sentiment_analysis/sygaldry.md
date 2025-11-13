# Sentiment Analysis Agent

## Overview

Multi-dimensional sentiment analysis with emotion detection, aspect-based analysis, and intensity assessment.

## Features

- Overall sentiment classification (positive/negative/neutral/mixed)
- Polarity scoring (-1.0 to 1.0)
- Subjectivity assessment (0.0 to 1.0)
- Emotion detection (joy, sadness, anger, fear, surprise, disgust)
- Aspect-based sentiment analysis
- Key phrase extraction
- Intensity assessment
- Context-aware analysis

## Installation

```bash
sygaldry add sentiment_analysis_agent
```

## Quick Start

```python
from sentiment_analysis import analyze_sentiment

result = await analyze_sentiment(
    text="The product is great but expensive!",
    analysis_depth="detailed"
)
```

## License

MIT License
