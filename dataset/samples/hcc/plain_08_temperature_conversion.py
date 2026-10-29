def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32


def describe(c):
    return f"{c:.1f} C is {celsius_to_fahrenheit(c):.1f} F"
