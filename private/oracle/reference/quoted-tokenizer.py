def tokenize(text):
    tokens = []
    current = []
    quoted = False
    escape = False
    token_started = False
    for char in text:
        if escape:
            current.append(char)
            token_started = True
            escape = False
        elif char == "\\":
            escape = True
            token_started = True
        elif char == '"':
            quoted = not quoted
            token_started = True
        elif char.isspace() and not quoted:
            if token_started:
                tokens.append("".join(current))
                current = []
                token_started = False
        else:
            current.append(char)
            token_started = True
    if quoted:
        raise ValueError("unterminated quote")
    if escape:
        current.append("\\")
    if token_started:
        tokens.append("".join(current))
    return tokens
