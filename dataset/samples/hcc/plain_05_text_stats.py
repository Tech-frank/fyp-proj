from collections import Counter


def top_words(text, n=10):
    words = [w.strip(".,;:!?").lower() for w in text.split()]
    return Counter(w for w in words if w).most_common(n)
