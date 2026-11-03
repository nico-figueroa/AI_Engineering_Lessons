from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

X = [
    "free money now",
    "win free cash",
    "project update",
    "meeting schedule"
]

y = ["spam", "spam", "ham", "ham"]

vectorizer = CountVectorizer()
X_vectors = vectorizer.fit_transform(X)

model = MultinomialNB()
model.fit(X_vectors, y)

test = vectorizer.transform(["free money"])

print("Test input:", ["free money"])
print("Test vector:", test)
print("Prediction:", model.predict(test)[0])