"""Read CSV (from stdin or built-in sample) and print a text-based bar chart."""
import sys
import csv
import io

SAMPLE_CSV = """\
Category,Value
Apples,35
Oranges,50
Bananas,20
Grapes,45
Peaches,30
"""


def parse_csv(text: str) -> list[tuple[str, float]]:
    """Parse CSV text and return list of (label, value) pairs.

    Uses the first two columns of every row, skipping rows that
    cannot be converted to a numeric value.
    """
    reader = csv.reader(io.StringIO(text))
    try:
        headers = next(reader)
    except StopIteration:
        print("Error: empty CSV input", file=sys.stderr)
        sys.exit(1)

    rows = []
    for raw_row in reader:
        if len(raw_row) < 2:
            continue
        label = raw_row[0].strip()
        try:
            value = float(raw_row[1])
        except ValueError:
            continue
        rows.append((label, value))
    return rows


def generate_bar_chart(data: list[tuple[str, float]], width: int = 50) -> None:
    """Print a Unicode bar chart for the given (label, value) pairs."""
    if not data:
        print("No data to display.")
        return

    max_value = max(val for _, val in data)
    if max_value <= 0:
        scale = 0.0
    else:
        scale = width / max_value

    max_label_len = max(len(label) for label, _ in data)

    print("\nBar Chart\n" + "-" * (max_label_len + width + 6 + 8))
    for label, val in data:
        bar_len = int(round(val * scale))
        bar = "\u2588" * bar_len          # full block, escaped to avoid encoding issues
        padded_label = label.ljust(max_label_len)
        print(f"{padded_label} | {bar} | {val:>7.1f}")


def main() -> None:
    """Entry point: read CSV, produce bar chart."""
    if not sys.stdin.isatty():
        csv_text = sys.stdin.read()
        # If piped input is empty (e.g., no data provided), fall back to the built-in sample.
        if not csv_text.strip():
            csv_text = SAMPLE_CSV
    else:
        csv_text = SAMPLE_CSV

    data = parse_csv(csv_text)
    generate_bar_chart(data)


if __name__ == "__main__":
    main()