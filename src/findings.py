from dataclasses import InitVar, asdict, dataclass
from types import MappingProxyType
from typing import Literal


VulnClass = Literal["HCC", "SQLI"]

# Central registry: rule ID -> (vulnerability class, description)
RULES = MappingProxyType({
    "HCC001": ("HCC", "Hardcoded credential assignment"),
    "HCC002": ("HCC", "Hardcoded credential keyword argument"),
    "HCC003": ("HCC", "Hardcoded credential in connection URI"),
    "SQLI001": ("SQLI", "SQL query built using concatenation"),
    "SQLI002": ("SQLI", "SQL query built using an f-string"),
    "SQLI003": ("SQLI", "SQL query built using % formatting"),
    "SQLI004": ("SQLI", "SQL query built using .format()"),
})


def redact(text: str, secrets: tuple[str, ...]) -> str:
    """Replace known secrets, processing longer values first."""
    for secret in sorted(set(secrets), key=len, reverse=True):
        text = text.replace(secret, "[REDACTED]")
    return text


@dataclass(frozen=True, slots=True, kw_only=True)
class Finding:
    vuln_class: VulnClass
    rule_id: str
    file: str
    unit: str
    line: int
    snippet: str
    message: str
    remediation: str

    # Constructor-only input: never stored or included in asdict().
    # HCC rules must supply the credential values they extracted.
    # SQLI rules can supply an empty tuple.
    secrets: InitVar[tuple[str, ...]]

    def __post_init__(self, secrets: tuple[str, ...]) -> None:
        if self.rule_id not in RULES:
            raise ValueError("Unknown rule ID")

        expected_class, _ = RULES[self.rule_id]
        if self.vuln_class != expected_class:
            raise ValueError("Rule ID and vulnerability class do not match")

        if type(self.line) is not int or self.line < 1:
            raise ValueError("line must be a positive integer")

        if not isinstance(secrets, tuple) or any(
            not isinstance(secret, str) or not secret
            for secret in secrets
        ):
            raise ValueError("secrets must be a tuple of non-empty strings")

        if self.vuln_class == "HCC" and not secrets:
            raise ValueError("HCC findings require detected secret values")

        # Redact every report-facing text field, including messages.
        for field_name in (
            "file", "unit", "snippet", "message", "remediation"
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string")

            object.__setattr__(
                self, field_name, redact(value, secrets)
            )

    def to_dict(self) -> dict:
        return asdict(self)