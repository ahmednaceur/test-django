from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from random import randint


class TokenPassword(): # generate  password reset code
    def _make_random_value(self):
        random = ''
        for index in range(4):
            random += str(randint(1, 9))
        return random


account_password_token = TokenPassword()


class TokenGenerator(PasswordResetTokenGenerator): # generate token for active account, email verification
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator()
