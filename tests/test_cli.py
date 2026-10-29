"""Part 11: end-to-end CLI behaviour on small files."""
import json
import sys
import types

import pytest

import cli


def write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_static_mode_exit_codes(tmp_path, capsys):
    bad = write(tmp_path, "bad.py", 'DB_PASSWORD = "Sup3r!"\n')
    good = write(tmp_path, "good.py", 'import os\nDB_PASSWORD = os.environ["DB"]\n')
    assert cli.main(["--mode", "static", str(bad)]) == 1
    assert "Sup3r!" not in capsys.readouterr().out
    assert cli.main(["--mode", "static", str(good)]) == 0


def test_broken_file_does_not_stop_scan(tmp_path):
    write(tmp_path, "broken.py", "def broken(:\n")
    write(tmp_path, "bad.py", 'password = "hunter2"\n')
    assert cli.main(["--mode", "static", str(tmp_path)]) == 1


def test_json_report_is_valid_and_redacted(tmp_path):
    src = write(tmp_path, "bad.py", 'password = "hunter2"\n')
    out = tmp_path / "report.json"
    cli.main(["--mode", "static", "--output", str(out), str(src)])
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["findings"][0]["rule_id"] == "HCC001"
    assert "hunter2" not in out.read_text(encoding="utf-8")


def test_missing_models_exit_code_3(tmp_path):
    src = write(tmp_path, "a.py", "x = 1\n")
    assert cli.main(["--mode", "ml", "--models", str(tmp_path / "none"), str(src)]) == 3


def test_bad_usage_exit_code_2():
    with pytest.raises(SystemExit) as exc:
        cli.main(["--mode", "nonsense", "x.py"])
    assert exc.value.code == 2


def test_finding_mapped_to_smallest_enclosing_unit(tmp_path):
    src = write(tmp_path, "m.py",
                'class C:\n    def m(self, c, uid):\n        c.execute("SELECT " + uid)\n')
    records = cli.scan_file(src, "static", None, None)
    assert records[0]["unit"] == "C.m"


def test_hybrid_labels_with_fake_model(tmp_path, monkeypatch):
    """Rule + ML agree -> Critical; ML only -> Medium. Uses stand-ins for Parts 7 and 9."""
    hybrid = pytest.importorskip("hybrid")
    if not hasattr(hybrid, "combine"):
        pytest.skip("Part 9 (hybrid.combine) not written yet")

    class AlwaysYes:
        classes_ = [0, 1]

        def predict_proba(self, X):
            return [[0.1, 0.9] for _ in X]

    fake_features = types.ModuleType("feature_extractor")
    fake_features.extract_features = lambda node: {"f": 1.0}
    monkeypatch.setitem(sys.modules, "feature_extractor", fake_features)
    bundle = {"model": AlwaysYes(), "threshold": 0.5, "feature_names": ["f"]}
    bundles = {"sqli": bundle, "hcc": bundle}

    src = write(tmp_path, "h.py", 'def f(c, uid):\n    c.execute("SELECT " + uid)\n')
    records = cli.scan_file(src, "hybrid", bundles, hybrid.combine)
    labels = {(r["vuln_class"], r["confidence"]) for r in records}
    assert ("SQLI", "Critical") in labels
    assert ("HCC", "Medium") in labels
