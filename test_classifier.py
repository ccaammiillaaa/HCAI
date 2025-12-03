from main import classify_text

# Test cases
test_inputs = [
    "I want a train",
    "Can I have a teddy bear?",
    "Give me a robot",
    "The weather is nice today"
]

print("Testing LLM Classifier...\n")

for text in test_inputs:
    category = classify_text(text)
    print(f"Input: '{text}' → Category: '{category}'")