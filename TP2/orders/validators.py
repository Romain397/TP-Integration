"""Input validators used by unit and integration tests."""

import re


def is_valid_email(email):
    if not isinstance(email, str):
        return False
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email))


def is_valid_password(password):
    errors = []
    if not isinstance(password, str):
        return {"valid": False, "errors": ["Le mot de passe est requis."]}
    if len(password) < 8:
        errors.append("Minimum 8 caractères.")
    if not re.search(r"[A-Z]", password):
        errors.append("Au moins une majuscule.")
    if not re.search(r"[a-z]", password):
        errors.append("Au moins une minuscule.")
    if not re.search(r"\d", password):
        errors.append("Au moins un chiffre.")
    if not re.search(r"[!@#$%^&*]", password):
        errors.append("Au moins un caractère spécial (!@#$%^&*).")
    return {"valid": not errors, "errors": errors}


def is_valid_age(age):
    return isinstance(age, int) and not isinstance(age, bool) and 0 <= age <= 150
