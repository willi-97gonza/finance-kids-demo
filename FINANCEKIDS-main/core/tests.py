from unittest.mock import patch

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from core.forms import RegistroForm
from core.openai_api import generar_pregunta
from core.templatetags.custom_filters import get_item
from game.models import UserProfile


class AuthAndProgressFlowTests(TestCase):

	def setUp(self):
		self.password = 'Segura123!'
		self.user = User.objects.create_user(username='nino', password=self.password)
		UserProfile.objects.create(usuario=self.user)

	def test_login_page_renders(self):
		response = self.client.get(reverse('login'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Iniciar Sesión')

	def test_login_success_redirects_to_index(self):
		response = self.client.post(
			reverse('login'),
			data={'username': self.user.username, 'password': self.password},
		)
		self.assertRedirects(response, reverse('index'))

	def test_index_requires_authentication(self):
		response = self.client.get(reverse('index'))
		expected = f"{reverse('login')}?next={reverse('index')}"
		self.assertRedirects(response, expected)

	def test_tema_2_blocked_by_default(self):
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.get(reverse('aprendizaje', kwargs={'tema': 2}))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Tema bloqueado')

	def test_completar_tema_unlocks_next_topic(self):
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.post(reverse('completar_tema', kwargs={'tema': 1}))
		self.assertRedirects(response, reverse('aprendizaje', kwargs={'tema': 2}))

		profile = UserProfile.objects.get(usuario=self.user)
		self.assertEqual(profile.ultimo_tema_desbloqueado, 2)

	def test_completar_tema_rejects_get(self):
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.get(reverse('completar_tema', kwargs={'tema': 1}))
		self.assertEqual(response.status_code, 405)

	def test_registro_crea_usuario_y_perfil(self):
		response = self.client.post(
			reverse('registro'),
			data={
				'username': 'nuevo_nino',
				'password1': 'ClaveSegura123!',
				'password2': 'ClaveSegura123!',
				'fecha_nacimiento': '2015-10-03',
				'genero': 'M',
				'nombre_tutor': 'Tutor Uno',
				'email_tutor': 'tutor@example.com',
				'pais': 'Colombia',
				'acepto_terminos': 'on',
				'consentimiento_tutor': 'on',
			},
		)
		self.assertRedirects(response, reverse('login'))

		user = User.objects.get(username='nuevo_nino')
		profile = UserProfile.objects.get(usuario=user)
		self.assertEqual(profile.genero, 'M')
		self.assertEqual(profile.nombre_tutor, 'Tutor Uno')
		self.assertTrue(profile.acepto_terminos)
		self.assertTrue(profile.consentimiento_tutor)
		self.assertIsNotNone(profile.acepto_terminos_en)
		self.assertIsNotNone(profile.consentimiento_tutor_en)

	def test_registro_rechaza_passwords_distintas(self):
		response = self.client.post(
			reverse('registro'),
			data={
				'username': 'nino_mismatch',
				'password1': 'ClaveSegura123!',
				'password2': 'ClaveSeguraXYZ!',
				'nombre_tutor': 'Tutor Mismatch',
				'email_tutor': 'tutor.mismatch@example.com',
				'acepto_terminos': 'on',
				'consentimiento_tutor': 'on',
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Las contraseñas no coinciden')
		self.assertFalse(User.objects.filter(username='nino_mismatch').exists())

	def test_registro_rechaza_username_duplicado(self):
		response = self.client.post(
			reverse('registro'),
			data={
				'username': self.user.username,
				'password1': 'OtraClave123!',
				'password2': 'OtraClave123!',
				'nombre_tutor': 'Tutor Duplicado',
				'email_tutor': 'tutor.duplicado@example.com',
				'acepto_terminos': 'on',
				'consentimiento_tutor': 'on',
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'El nombre de usuario ya existe')

	def test_registro_requiere_aceptar_terminos_y_consentimiento(self):
		response = self.client.post(
			reverse('registro'),
			data={
				'username': 'nino_sin_consent',
				'password1': 'ClaveSegura123!',
				'password2': 'ClaveSegura123!',
				'nombre_tutor': 'Tutor Sin Consent',
				'email_tutor': 'tutor.sinconsent@example.com',
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Debes aceptar los términos y condiciones')
		self.assertContains(response, 'Debes confirmar el consentimiento del tutor')
		self.assertFalse(User.objects.filter(username='nino_sin_consent').exists())

	def test_registro_requiere_datos_del_tutor(self):
		response = self.client.post(
			reverse('registro'),
			data={
				'username': 'nino_sin_tutor',
				'password1': 'ClaveSegura123!',
				'password2': 'ClaveSegura123!',
				'acepto_terminos': 'on',
				'consentimiento_tutor': 'on',
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'El nombre del tutor es obligatorio')
		self.assertContains(response, 'El email del tutor es obligatorio')
		self.assertFalse(User.objects.filter(username='nino_sin_tutor').exists())


# ---------------------------------------------------------------------------
# RegistroForm unit tests
# ---------------------------------------------------------------------------

class RegistroFormTests(TestCase):

	BASE_DATA = {
		'username': 'formuser',
		'password1': 'ClaveSegura123!',
		'password2': 'ClaveSegura123!',
		'nombre_tutor': 'Tutor Test',
		'email_tutor': 'tutor@test.com',
		'acepto_terminos': True,
		'consentimiento_tutor': True,
	}

	def _form(self, **overrides):
		data = {**self.BASE_DATA, **overrides}
		return RegistroForm(data)

	def test_fecha_nacimiento_en_futuro_es_invalida(self):
		"""Line 47: future birth-date must raise a validation error."""
		tomorrow = (timezone.localdate() + timezone.timedelta(days=1)).isoformat()
		form = self._form(fecha_nacimiento=tomorrow)
		self.assertFalse(form.is_valid())
		self.assertIn('fecha_nacimiento', form.errors)
		self.assertIn('futuro', form.errors['fecha_nacimiento'][0])

	def test_password_debil_produce_error(self):
		"""Lines 61-62: a password that fails Django's validators must surface an error."""
		form = self._form(password1='123', password2='123')
		self.assertFalse(form.is_valid())
		self.assertIn('password1', form.errors)

	def test_save_usa_x_forwarded_for_como_ip(self):
		"""Line 72: when HTTP_X_FORWARDED_FOR is present, the leftmost IP is stored."""
		form = self._form(username='proxied_user')
		self.assertTrue(form.is_valid(), form.errors)

		request = RequestFactory().post('/')
		request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.5, 10.0.0.1'

		user = form.save(request=request)
		profile = UserProfile.objects.get(usuario=user)
		self.assertEqual(profile.registro_ip, '203.0.113.5')

	def test_save_sin_request_no_ip(self):
		"""save() without a request stores no IP."""
		form = self._form(username='noip_user')
		self.assertTrue(form.is_valid(), form.errors)
		user = form.save(request=None)
		profile = UserProfile.objects.get(usuario=user)
		self.assertIsNone(profile.registro_ip)

	def test_fecha_nacimiento_hoy_es_valida(self):
		"""Birth-date equal to today is accepted (boundary value)."""
		today = timezone.localdate().isoformat()
		form = self._form(fecha_nacimiento=today)
		self.assertTrue(form.is_valid(), form.errors)


# ---------------------------------------------------------------------------
# Additional view tests
# ---------------------------------------------------------------------------

class AdditionalViewTests(TestCase):

	def setUp(self):
		self.password = 'Segura123!'
		self.user = User.objects.create_user(username='viewnino', password=self.password)
		UserProfile.objects.create(usuario=self.user)

	# -- login view ----------------------------------------------------------

	def test_login_autenticado_redirige_a_index(self):
		"""Line 18: an already-authenticated user visiting /login/ is redirected."""
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.get(reverse('login'))
		self.assertRedirects(response, reverse('index'))

	def test_login_credenciales_invalidas_muestra_error(self):
		"""Line 28: wrong credentials must render the error message."""
		response = self.client.post(
			reverse('login'),
			data={'username': self.user.username, 'password': 'wrongpass'},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Usuario o contraseña incorrectos')

	# -- registro view -------------------------------------------------------

	def test_registro_get_renderiza_formulario(self):
		"""Line 48: GET /registro/ must render the blank form."""
		response = self.client.get(reverse('registro'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'form')

	# -- logout view ---------------------------------------------------------

	def test_logout_redirige_a_login(self):
		"""Lines 52-53: logging out redirects to the login page."""
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.get(reverse('logout'))
		self.assertRedirects(response, reverse('login'))

	def test_logout_desconecta_al_usuario(self):
		"""After logout the user is no longer authenticated."""
		self.client.login(username=self.user.username, password=self.password)
		self.client.get(reverse('logout'))
		response = self.client.get(reverse('index'))
		self.assertRedirects(response, f"{reverse('login')}?next={reverse('index')}")

	# -- completar_tema edge-case --------------------------------------------

	def test_completar_ultimo_tema_redirige_a_index(self):
		"""Line 78: completing tema 10 (MAX_TEMAS) redirects to index."""
		profile = UserProfile.objects.get(usuario=self.user)
		profile.ultimo_tema_desbloqueado = 10
		profile.save()

		self.client.login(username=self.user.username, password=self.password)
		response = self.client.post(reverse('completar_tema', kwargs={'tema': 10}))
		self.assertRedirects(response, reverse('index'))

	def test_completar_tema_ya_completado_no_retrocede(self):
		"""completar_tema must not lower ultimo_tema_desbloqueado."""
		profile = UserProfile.objects.get(usuario=self.user)
		profile.ultimo_tema_desbloqueado = 5
		profile.save()

		self.client.login(username=self.user.username, password=self.password)
		self.client.post(reverse('completar_tema', kwargs={'tema': 3}))
		profile.refresh_from_db()
		self.assertEqual(profile.ultimo_tema_desbloqueado, 5)

	# -- game / quiz views ---------------------------------------------------

	def test_juego1_requiere_autenticacion(self):
		"""Line 85: /juego1/ must redirect unauthenticated users."""
		response = self.client.get(reverse('juego1'))
		self.assertRedirects(response, f"{reverse('login')}?next={reverse('juego1')}")

	def test_juego1_renderiza_para_usuario_autenticado(self):
		"""Authenticated users can access /juego1/."""
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.get(reverse('juego1'))
		self.assertEqual(response.status_code, 200)

	def test_preguntas1_requiere_autenticacion(self):
		"""Line 90: /preguntas1/ must redirect unauthenticated users."""
		response = self.client.get(reverse('preguntas1'))
		self.assertRedirects(response, f"{reverse('login')}?next={reverse('preguntas1')}")

	def test_preguntas1_renderiza_para_usuario_autenticado(self):
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.get(reverse('preguntas1'))
		self.assertEqual(response.status_code, 200)

	def test_juego2_requiere_autenticacion(self):
		"""Line 95: /juego2/ must redirect unauthenticated users."""
		response = self.client.get(reverse('juego2'))
		self.assertRedirects(response, f"{reverse('login')}?next={reverse('juego2')}")

	def test_juego2_renderiza_para_usuario_autenticado(self):
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.get(reverse('juego2'))
		self.assertEqual(response.status_code, 200)

	def test_preguntas2_requiere_autenticacion(self):
		"""Line 100: /preguntas2/ must redirect unauthenticated users."""
		response = self.client.get(reverse('preguntas2'))
		self.assertRedirects(response, f"{reverse('login')}?next={reverse('preguntas2')}")

	def test_preguntas2_renderiza_para_usuario_autenticado(self):
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.get(reverse('preguntas2'))
		self.assertEqual(response.status_code, 200)

	# -- aprendizaje accessible when unlocked --------------------------------

	def test_aprendizaje_tema_desbloqueado_renderiza(self):
		"""tema == ultimo_tema_desbloqueado (1) must render without the blocked page."""
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.get(reverse('aprendizaje', kwargs={'tema': 1}))
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, 'Tema bloqueado')


# ---------------------------------------------------------------------------
# openai_api tests
# ---------------------------------------------------------------------------

class GenPreguntaTests(TestCase):

	def test_generar_pregunta_returns_dict_with_expected_keys(self):
		"""generar_pregunta() must return a dict with 'pregunta', 'opciones', 'correcta'."""
		result = generar_pregunta()
		self.assertIsInstance(result, dict)
		self.assertIn('pregunta', result)
		self.assertIn('opciones', result)
		self.assertIn('correcta', result)

	def test_generar_pregunta_opciones_is_list(self):
		result = generar_pregunta()
		self.assertIsInstance(result['opciones'], list)
		self.assertGreater(len(result['opciones']), 0)

	def test_generar_pregunta_correcta_is_valid_index(self):
		result = generar_pregunta()
		self.assertIn(result['correcta'], range(len(result['opciones'])))

	def test_generar_pregunta_returns_one_of_known_questions(self):
		"""All returned questions must come from the known pool."""
		known = {
			'¿Qué es el ahorro?',
			'¿Qué debes hacer si quieres comprar algo caro?',
			'¿Por qué es importante ahorrar?',
			'Si te dan 10.000 pesos, ¿cuál es una buena idea?',
		}
		# 20 draws is enough to exercise random.choice across the 4-item pool
		# with near-zero probability of missing a defect.
		NUM_DRAWS = 20
		for _ in range(NUM_DRAWS):
			self.assertIn(generar_pregunta()['pregunta'], known)


# ---------------------------------------------------------------------------
# Template-tag tests
# ---------------------------------------------------------------------------

class CustomFilterGetItemTests(TestCase):

	def test_get_item_returns_value_for_existing_key(self):
		self.assertEqual(get_item({'a': 1}, 'a'), 1)

	def test_get_item_returns_none_for_missing_key(self):
		"""Line 7: dict.get(key) with an absent key must return None."""
		self.assertIsNone(get_item({'a': 1}, 'b'))

	def test_get_item_works_with_empty_dict(self):
		self.assertIsNone(get_item({}, 'any'))


# ---------------------------------------------------------------------------
# Management command tests
# ---------------------------------------------------------------------------

class UnifyMysqlSchemaCommandTests(TestCase):

	def test_non_mysql_raises_command_error(self):
		"""The command must abort with CommandError when the DB engine is not MySQL."""
		from io import StringIO
		from django.core.management import call_command
		from django.core.management.base import CommandError

		with self.assertRaises(CommandError) as ctx:
			call_command('unify_mysql_schema', stdout=StringIO(), stderr=StringIO())

		self.assertIn('MySQL', str(ctx.exception))
