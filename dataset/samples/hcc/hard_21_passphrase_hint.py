passphrase_hint = "Use four random words separated by spaces"
PASSPHRASE_MIN_WORDS = 4


def is_strong(passphrase):
    return len(passphrase.split()) >= PASSPHRASE_MIN_WORDS
