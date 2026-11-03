from collections import Counter
import math

training_data = [
    ("free money now", "spam"),
    ("win free cash", "spam"),
    ("project update", "ham"),
    ("meeting schedule", "ham"),
]

class_counts = Counter()
word_counts = {
    "spam": Counter(),
    "ham": Counter()
}

vocabulary = set()

for text, label in training_data:
    class_counts[label] += 1

    for word in text.split():
        word_counts[label][word] += 1
        vocabulary.add(word)

total_documents = len(training_data)

print(class_counts)
print(vocabulary)

def score_document(text, label):
    words = text.split()

    # Prior probability
    log_prob = math.log(class_counts[label] / total_documents)

    total_words_in_class = sum(word_counts[label].values())
    vocab_size = len(vocabulary)

    for word in words:
        word_count = word_counts[label][word]

        # Laplace smoothing
        probability = (
            word_count + 1
        ) / (
            total_words_in_class + vocab_size
        )

        log_prob += math.log(probability)

    return log_prob

def predict(text):
    spam_score = score_document(text, "spam")
    ham_score = score_document(text, "ham")

    if spam_score > ham_score:
        return "spam"
    else:
        return "ham"

message = "free money"

print("Message:", message)
print("Spam score:", score_document(message, "spam"))
print("Ham score:", score_document(message, "ham"))
print("Prediction:", predict(message))