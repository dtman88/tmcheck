# tmcheck

This repository contains code and scripts for an automated trademark-checking system used in an ecommerce/RPA pipeline.

## Project Goal

The goal of this project is to process free-text input (such as product titles or descriptions) and break them into subphrases to check for potential trademark violations.

## Getting Started

Use the `extract_trademark_phrases` function from within your Python code:

```python
from trademark_extractor import extract_trademark_phrases

phrases = extract_trademark_phrases("funny t-shirt for cat lovers")
print(phrases)
# ['funny', 'cat', 'cat lovers']
```
