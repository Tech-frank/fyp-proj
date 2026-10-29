"""Parts 2-5: the test-case tables from the build guide, as executable tests.

Run from the project root:  python -m pytest
A failure here means the rules changed behaviour: check whether that was
intended, then update chapter 4 (and this file) to match.
"""
import pytest

from parser import collect_units, read_and_parse
from static_analyzer import analyze_source


def rules(source):
    return [f.rule_id for f in analyze_source(source)]


SHOULD_FLAG = {
    "plain password": ('password = "hunter2"', "HCC001"),
    "underscore part": ('DB_PASSWORD = "Sup3r!"', "HCC001"),
    "camelCase part": ('dbPassword = "Sup3r!"', "HCC001"),
    "token part": ('GITHUB_TOKEN = "ghp_abc"', "HCC001"),
    "adjacent api key": ('STRIPE_API_KEY = "sk_live_x"', "HCC001"),
    "capital run": ('APIKey = "sk_live_x"', "HCC001"),
    "secret key": ('SECRET_KEY = "django-insecure-x"', "HCC001"),
    "client secret": ('CLIENT_SECRET = "abc123"', "HCC001"),
    "attribute": ('class A:\n    def __init__(self):\n        self.password = "hunter2"', "HCC001"),
    "annotated": ('password: str = "hunter2"', "HCC001"),
    "keyword argument": ('connect(user="admin", password="hunter2")', "HCC002"),
    "chained target": ('a = b_password = "hunter2"', "HCC001"),
    "connection uri": ('URL = "postgresql://admin:hunter2@db.example.com/app"', "HCC003"),
    "sql concatenation": ('def f(c, uid):\n    c.execute("SELECT * FROM u WHERE id=" + uid)', "SQLI001"),
    "sql f-string": ('def f(c, uid):\n    c.execute(f"SELECT * FROM u WHERE id={uid}")', "SQLI002"),
    "sql % formatting": ('def f(c, uid):\n    c.execute("SELECT * FROM u WHERE id=%s" % uid)', "SQLI003"),
    "sql .format()": ('def f(c, uid):\n    c.execute("SELECT * FROM u WHERE id={}".format(uid))', "SQLI004"),
    "sql via variable": ('def f(c, uid):\n    q = f"SELECT * FROM u WHERE id={uid}"\n    c.execute(q)', "SQLI002"),
    "sql built in steps": ('def f(c, uid):\n    q = "SELECT * FROM u "\n    q += "WHERE id=" + uid\n    c.execute(q)', "SQLI001"),
    "executemany": ('def f(c, x, rows):\n    c.executemany("INSERT INTO t VALUES (%s)" % x, rows)', "SQLI003"),
    "execute nested in a call": ('def f(c, uid):\n    out.append(c.execute(f"SELECT {uid}"))', "SQLI002"),
}

SHOULD_BE_CLEAN = {
    "not a whole part": 'tokenizer = "bert-base"',
    "key alone": 'cache_key = "user:42"',
    "empty string": 'password = ""',
    "placeholder": 'password = "password"',
    "environment variable": 'import os\npassword = os.environ["DB_PASS"]',
    "annotation without value": 'password: str',
    "integer": 'password_length = 8',
    "boolean": 'secret_enabled = True',
    "plural": 'tokens = "a,b,c"',
    "literal query": 'def f(c):\n    c.execute("SELECT * FROM t")',
    "? parameter": 'def f(c, uid):\n    c.execute("SELECT * FROM u WHERE id=?", (uid,))',
    "%s parameter": 'def f(c, uid):\n    c.execute("SELECT * FROM u WHERE id=%s", (uid,))',
    "concatenation outside execute": 'print("a" + b)',
    "f-string that is logged": 'def f(log, uid):\n    log.info(f"user {uid}")',
    "literal-only concatenation": 'def f(c):\n    c.execute("SELECT * " + "FROM t")',
    "variable reassigned to safe query": 'def f(c, uid):\n    q = f"SELECT {uid}"\n    q = "SELECT * FROM t"\n    c.execute(q)',
}


@pytest.mark.parametrize("name", sorted(SHOULD_FLAG))
def test_should_flag(name):
    source, rule_id = SHOULD_FLAG[name]
    assert rule_id in rules(source)


@pytest.mark.parametrize("name", sorted(SHOULD_BE_CLEAN))
def test_should_be_clean(name):
    assert rules(SHOULD_BE_CLEAN[name]) == []


def test_ambiguous_prompt_is_flagged_by_design():
    # Decision 8: the rule flags it; the ML is there to judge it.
    assert rules('password_prompt = "Enter your password"') == ["HCC001"]


def test_secret_never_appears_in_findings():
    source = 'DB_PASSWORD = "Sup3rS3cret!"\nURL = "postgresql://admin:p%40ss@h/db"\n'
    for finding in analyze_source(source):
        text = str(finding.to_dict())
        assert "Sup3rS3cret!" not in text
        assert "p%40ss" not in text and "p@ss" not in text


# ---------------------------------------------------------------- Part 2

def write(tmp_path, name, text):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8") if isinstance(text, str) else text)
    return path


def test_two_functions_and_module_code_give_three_units(tmp_path):
    path = write(tmp_path, "a.py", "def a():\n    pass\n\ndef b():\n    pass\n\nX = 1\n")
    assert [u.name for u in collect_units(path)] == ["a", "b", "<module>"]


def test_methods_are_named_class_dot_method(tmp_path):
    path = write(tmp_path, "c.py", "class C:\n    def m1(self):\n        pass\n    def m2(self):\n        pass\n")
    names = [u.name for u in collect_units(path)]
    assert "C.m1" in names and "C.m2" in names


def test_syntax_error_is_skipped_without_crashing(tmp_path):
    path = write(tmp_path, "bad.py", "def broken(:\n")
    assert collect_units(path) == []


def test_folder_with_one_bad_file_still_returns_good_units(tmp_path):
    write(tmp_path, "f/bad.py", "def broken(:\n")
    write(tmp_path, "f/good.py", "def ok():\n    pass\n")
    assert [u.name for u in collect_units(tmp_path / "f")] == ["ok"]


def test_file_saved_with_windows_byte_order_mark_is_parsed(tmp_path):
    # Notepad's "UTF-8 with BOM" adds 3 bytes that utf-8 (not utf-8-sig) keeps.
    path = write(tmp_path, "bom.py", b'\xef\xbb\xbfPASSWORD = "hunter2"\n')
    assert read_and_parse(path) is not None
