import sys
import io
import pytest
from main import parse_csv, generate_bar_chart, main


class TestParseCsv:
    def test_valid_csv(self):
        csv_text = "Category,Value\nApples,35\nOranges,50\nBananas,20"
        data = parse_csv(csv_text)
        assert len(data) == 3
        assert data[0] == ("Apples", 35.0)
        assert data[1] == ("Oranges", 50.0)

    def test_skips_invalid_rows(self):
        csv_text = (
            "Category,Value\n"
            "Apples,35\n"
            ",,\n"                 # missing label
            "Oranges,abc\n"        # non‑numeric value
            "Bananas,20\n"
            "Grapes"               # too few columns
        )
        data = parse_csv(csv_text)
        # only two valid rows remain
        assert data == [("Apples", 35.0), ("Bananas", 20.0)]

    def test_empty_csv_raises_systemexit(self):
        with pytest.raises(SystemExit):
            parse_csv("")          # no headers at all

    def test_only_header_raises_systemexit(self):
        with pytest.raises(SystemExit):
            parse_csv("Category,Value\n")

    def test_strips_label_whitespace(self):
        csv_text = "Category,Value\n  Apple ,35\nOrange  ,50"
        data = parse_csv(csv_text)
        assert data[0][0] == "Apple"
        assert data[1][0] == "Orange"


class TestGenerateBarChart:
    def test_normal_chart(self, capsys):
        data = [("Apples", 35.0), ("Oranges", 50.0), ("Bananas", 20.0)]
        generate_bar_chart(data)
        out = capsys.readouterr().out
        assert "Bar Chart" in out
        assert "Apples" in out
        assert "Oranges" in out
        assert "35.0" in out
        # each line contains the bar column separator
        assert out.count(" | ") == len(data) + 1  # header + one per row

    def test_empty_data(self, capsys):
        generate_bar_chart([])
        out = capsys.readouterr().out
        assert "No data to display." in out

    def test_all_zero_values(self, capsys):
        data = [("A", 0.0), ("B", 0.0)]
        generate_bar_chart(data)
        out = capsys.readouterr().out
        assert "Bar Chart" in out
        assert " 0.0" in out
        assert "A" in out
        # bar length zero → no full‑block characters (escaping not needed, we just check it doesn't crash)
        # ensure the format still includes the pipe separators
        assert " | " in out

    def test_single_row(self, capsys):
        data = [("X", 7.5)]
        generate_bar_chart(data)
        out = capsys.readouterr().out
        assert "X" in out
        assert "7.5" in out

    def test_handles_very_large_value(self, capsys):
        data = [("Huge", 1e6), ("Small", 1)]
        generate_bar_chart(data, width=20)
        out = capsys.readouterr().out
        # should not raise any error
        assert "Huge" in out
        assert "Small" in out


class TestMain:
    def test_sample_used_when_stdin_is_tty(self, monkeypatch, capsys):
        monkeypatch.setattr(sys.stdin, 'isatty', lambda: True)
        main()
        out = capsys.readouterr().out
        # sample data is printed
        assert "Apples" in out
        assert "35.0" in out
        assert "Bar Chart" in out

    def test_piped_input(self, monkeypatch, capsys):
        monkeypatch.setattr(sys.stdin, 'isatty', lambda: False)
        monkeypatch.setattr(sys.stdin, 'read', lambda: "Category,Value\nX,10\nY,20")
        main()
        out = capsys.readouterr().out
        assert "X" in out
        assert "10.0" in out
        assert "Y" in out

    def test_empty_piped_input_falls_back_to_sample(self, monkeypatch, capsys):
        monkeypatch.setattr(sys.stdin, 'isatty', lambda: False)
        monkeypatch.setattr(sys.stdin, 'read', lambda: "   \n")
        main()
        out = capsys.readouterr().out
        # fallback to sample
        assert "Apples" in out
        assert "35.0" in out

    def test_non_numeric_data_filtered_in_main(self, monkeypatch, capsys):
        monkeypatch.setattr(sys.stdin, 'isatty', lambda: False)
        monkeypatch.setattr(sys.stdin, 'read', lambda: "Category,Value\nA,Bad\nB,3.5\nC,another")
        main()
        out = capsys.readouterr().out
        # only the valid row appears
        assert "A" not in out
        assert "B" in out
        assert "3.5" in out