import csv
import io


def rows_to_csv(rows):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerows(
        ["" if value is None else value for value in row]
        for row in rows
    )
    return output.getvalue()
