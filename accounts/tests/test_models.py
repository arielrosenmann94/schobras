import uuid

from django.test import TestCase

from accounts.models import User


class UserModelTests(TestCase):
    def test_user_pk_is_uuid7(self):
        user = User.objects.create_user(username="editora", password="x" * 12)
        self.assertIsInstance(user.id, uuid.UUID)
        self.assertEqual(user.id.version, 7)
