def rows_to_csv(rows):
    lines = []
    for row in rows:
        fields = []
        for value in row:
            text = "" if value is None else str(value)
            if "," in text:
                text = f'"{text}"'
            fields.append(text)
        lines.append(",".join(fields))
    return "\n".join(lines) + ("\n" if lines else "")
