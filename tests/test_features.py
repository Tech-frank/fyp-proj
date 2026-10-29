"""Part 7: the feature extractor's contract and the value features."""
import ast
import math

from feature_extractor import FEATURE_NAMES, extract_features


def feats(source):
    return extract_features(ast.parse(source))


def test_same_keys_in_same_order_for_any_input():
    for source in ("", "x = 1", 'def f(c, u):\n    c.execute("SELECT " + u)\n'):
        assert tuple(feats(source)) == FEATURE_NAMES


def test_all_values_are_finite_floats():
    values = feats('import os\nPASSWORD = "x9$Kq2!vL"\nprint(f"{PASSWORD}")\n').values()
    assert all(isinstance(v, float) and math.isfinite(v) for v in values)


def test_works_on_a_single_function_node():
    tree = ast.parse('def f(c, u):\n    c.execute(f"SELECT * FROM t WHERE id={u}")\n')
    f = extract_features(tree.body[0])
    assert f["execute_direct_dynamic"] == 1.0 and f["has_select"] == 1.0


def test_value_features_separate_a_secret_from_a_prompt():
    secret = feats('DB_PASSWORD = "x9$Kq2!vLp0@Zr7"')
    prompt = feats('DB_PASSWORD_PROMPT = "Please enter your password"')
    assert secret["has_credential_str"] == prompt["has_credential_str"] == 1.0
    assert secret["cred_value_has_space"] == 0.0 and prompt["cred_value_has_space"] == 1.0
    assert secret["cred_value_entropy"] > prompt["cred_value_entropy"]
    assert secret["cred_value_char_classes"] == 4.0


def test_environment_variable_is_not_a_credential_string():
    f = feats('import os\nDB_PASSWORD = os.environ["DB_PASSWORD"]\n')
    assert f["has_env_access"] == 1.0 and f["has_credential_str"] == 0.0


def test_known_prefix_and_uri():
    assert feats('k = "ghp_abcdef123456"')["has_known_prefix"] == 1.0
    assert feats('u = "postgresql://admin:pw@db/app"')["has_hardcoded_url"] == 1.0


def test_parameterised_query_vs_dynamic_query():
    safe = feats('def f(c, u):\n    c.execute("SELECT * FROM t WHERE id=?", (u,))\n')
    unsafe = feats('def f(c, u):\n    c.execute("SELECT * FROM t WHERE id=%s" % u)\n')
    assert safe["execute_with_params"] == 1.0 and safe["execute_direct_dynamic"] == 0.0
    assert unsafe["execute_direct_dynamic"] == 1.0 and unsafe["sql_dynamic_count"] == 1.0


def test_logged_fstring_is_seen_as_logging_not_execution():
    f = feats('def f(log, u):\n    log.info(f"loading {u}")\n')
    assert f["dynamic_string_logged"] == 1.0 and f["execute_direct_dynamic"] == 0.0


def test_does_not_use_the_rule_engine():
    import feature_extractor
    source = open(feature_extractor.__file__, encoding="utf-8").read()
    assert "static_analyzer" not in source.replace("static analyzer", "")
