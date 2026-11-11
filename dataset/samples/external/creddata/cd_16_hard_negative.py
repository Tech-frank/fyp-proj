def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
    if key in self._has_been_read:
        raise EnvironError(
            f"Attempting to set environ['{key}'], but the value has already been "
            "read."
        )
    self._environ.__setitem__(key, value)
