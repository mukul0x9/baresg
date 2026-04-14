from .md_tokens import Token


def tokenize(text):
    tokens = []
    i = 0
    start_of_line = True

    while i < len(text):
        if start_of_line and text[i] == "#":
            count = 0
            while i < len(text) and text[i] == "#":
                count += 1
                i += 1

            if i < len(text) and text[i] == " ":
                i += 1
                tokens.append(Token("HEADING", count))
                start_of_line = False
                continue
            else:
                tokens.append(Token("TEXT", "#" * count))
                start_of_line = False
                continue

        elif text[i : i + 2] == "**":
            tokens.append(Token("BOLD"))
            i += 2

        elif text[i] == "*":
            tokens.append(Token("ITALIC"))
            i += 1

        elif text[i] == "`":
            tokens.append(Token("CODE"))
            i += 1

        elif text[i] == "\n":
            tokens.append(Token("NEWLINE"))
            i += 1
            start_of_line = True
            continue

        else:
            start = i
            while i < len(text) and text[i] not in "*`\n#":
                i += 1
            tokens.append(Token("TEXT", text[start:i]))

        start_of_line = False

    return tokens
