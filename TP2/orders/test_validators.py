"""A2: email, password messages and age validation."""

from django.test import SimpleTestCase

from orders.validators import is_valid_age, is_valid_email, is_valid_password


class ValidatorTests(SimpleTestCase):
    def test_should_accept_email(self):
        self.assertEqual(is_valid_email("user@example.com"), True)

    def test_should_accept_tag_email(self):
        self.assertEqual(is_valid_email("user.name+tag@domain.co"), True)

    def test_should_reject_email_without_at(self):
        self.assertEqual(is_valid_email("invalid"), False)

    def test_should_reject_email_without_local(self):
        self.assertEqual(is_valid_email("@domain.com"), False)

    def test_should_reject_email_without_domain(self):
        self.assertEqual(is_valid_email("user@"), False)

    def test_should_reject_empty_email(self):
        self.assertEqual(is_valid_email(""), False)

    def test_should_reject_null_email(self):
        self.assertEqual(is_valid_email(None), False)

    def test_should_accept_password(self):
        self.assertEqual(is_valid_password("Passw0rd!"), {"valid": True, "errors": []})

    def test_should_reject_short_password(self):
        self.assertEqual(
            is_valid_password("short"),
            {
                "valid": False,
                "errors": [
                    "Minimum 8 caractères.",
                    "Au moins une majuscule.",
                    "Au moins un chiffre.",
                    "Au moins un caractère spécial (!@#$%^&*).",
                ],
            },
        )

    def test_should_require_uppercase(self):
        self.assertEqual(is_valid_password("alllowercase1!")["errors"], ["Au moins une majuscule."])

    def test_should_require_lowercase(self):
        self.assertEqual(is_valid_password("ALLUPPERCASE1!")["errors"], ["Au moins une minuscule."])

    def test_should_require_digit(self):
        self.assertEqual(is_valid_password("NoDigits!here")["errors"], ["Au moins un chiffre."])

    def test_should_require_special(self):
        self.assertEqual(is_valid_password("NoSpecial1here")["errors"], ["Au moins un caractère spécial (!@#$%^&*)."])

    def test_should_reject_empty_password(self):
        self.assertEqual(len(is_valid_password("")["errors"]), 5)

    def test_should_reject_null_password(self):
        self.assertEqual(is_valid_password(None), {"valid": False, "errors": ["Le mot de passe est requis."]})

    def test_should_validate_age_0(self):
        self.assertEqual(is_valid_age(25), True)

    def test_should_validate_age_1(self):
        self.assertEqual(is_valid_age(0), True)

    def test_should_validate_age_2(self):
        self.assertEqual(is_valid_age(150), True)

    def test_should_validate_age_3(self):
        self.assertEqual(is_valid_age(-1), False)

    def test_should_validate_age_4(self):
        self.assertEqual(is_valid_age(151), False)

    def test_should_validate_age_5(self):
        self.assertEqual(is_valid_age(25.5), False)

    def test_should_validate_age_6(self):
        self.assertEqual(is_valid_age("25"), False)

    def test_should_validate_age_7(self):
        self.assertEqual(is_valid_age(None), False)

    def test_should_validate_age_8(self):
        self.assertEqual(is_valid_age(True), False)
