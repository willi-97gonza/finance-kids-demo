from django.test import TestCase
from django.contrib.auth.models import User

from game.models import Tema, UserProfile


class TemaStrTests(TestCase):

	def test_tema_str_returns_titulo(self):
		"""Line 16: Tema.__str__ must return its titulo."""
		tema = Tema(numero_tema=1, titulo='Ahorro', descripcion='Tema de ahorro', orden=1)
		self.assertEqual(str(tema), 'Ahorro')


class UserProfileStrTests(TestCase):

	def test_userprofile_str_returns_username(self):
		"""Line 55: UserProfile.__str__ must return the related user's username."""
		user = User.objects.create_user(username='testprofile', password='pass')
		profile = UserProfile.objects.create(usuario=user)
		self.assertEqual(str(profile), 'testprofile')
