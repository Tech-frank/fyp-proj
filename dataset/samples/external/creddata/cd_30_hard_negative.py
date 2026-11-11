def decode(text, key):
    assert isinstance(text, six.string_types), "Expected 'bytes', got '{}'".format(type(text))
    assert isinstance(key, six.string_types), "Expected 'str' type, got '{}'".format(type(key))
    key = _ascii_key(key)
    res = ""
    for i, c in enumerate(text):
        if c not in CHARS:
            res += c
        else:
            text_index = CHARS.index(c)
            key_index = CHARS.index(key[i % len(key)])
            res += CHARS[(text_index - key_index) % len(CHARS)]
    return res
