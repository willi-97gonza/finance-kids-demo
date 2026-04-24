import sqlite3
from datetime import datetime

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from game.models import Tema, UserProfile


def parse_datetime(value):
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def sync():
    sqlite_conn = sqlite3.connect('db.sqlite3')
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    with transaction.atomic():
        sqlite_cur.execute('SELECT * FROM auth_user ORDER BY id')
        for row in sqlite_cur.fetchall():
            payload = dict(row)
            User.objects.update_or_create(
                id=payload['id'],
                defaults={
                    'password': payload['password'],
                    'last_login': parse_datetime(payload['last_login']),
                    'is_superuser': bool(payload['is_superuser']),
                    'username': payload['username'],
                    'first_name': payload['first_name'],
                    'last_name': payload['last_name'],
                    'email': payload['email'],
                    'is_staff': bool(payload['is_staff']),
                    'is_active': bool(payload['is_active']),
                    'date_joined': parse_datetime(payload['date_joined']),
                },
            )

        sqlite_cur.execute('SELECT * FROM game_tema ORDER BY id')
        for row in sqlite_cur.fetchall():
            payload = dict(row)
            Tema.objects.update_or_create(
                id=payload['id'],
                defaults={
                    'numero_tema': payload['numero_tema'],
                    'titulo': payload['titulo'],
                    'descripcion': payload['descripcion'],
                    'orden': payload['orden'],
                    'es_activo': bool(payload['es_activo']),
                },
            )

        sqlite_cur.execute('SELECT * FROM game_userprofile ORDER BY id')
        for row in sqlite_cur.fetchall():
            payload = dict(row)
            UserProfile.objects.update_or_create(
                id=payload['id'],
                defaults={
                    'usuario_id': payload['usuario_id'],
                    'fecha_nacimiento': payload['fecha_nacimiento'],
                    'genero': payload['genero'],
                    'nombre_tutor': payload['nombre_tutor'],
                    'email_tutor': payload['email_tutor'],
                    'pais': payload['pais'],
                    'ultimo_tema_desbloqueado': payload['ultimo_tema_desbloqueado'],
                },
            )

    sqlite_conn.close()


sync()
print('users=', User.objects.count())
print('temas=', Tema.objects.count())
print('profiles=', UserProfile.objects.count())
