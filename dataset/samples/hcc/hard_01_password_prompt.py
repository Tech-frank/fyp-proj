from getpass import getpass

password_prompt = "Enter your database password: "


def ask_password():
    return getpass(password_prompt)
