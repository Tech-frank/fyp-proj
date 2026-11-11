def combine(rule_fired: bool, ml_positive: bool) -> str:
    """Hybrid decision layer (chapter 3.7.4)."""
    if rule_fired and ml_positive:
        return "Critical"
    if rule_fired:
        return "High"
    if ml_positive:
        return "Medium"
    return "No finding"
