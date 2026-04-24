from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction


class Command(BaseCommand):
    help = (
        "Sincroniza el esquema legado (usuarios/perfiles_usuario/temas/progreso_usuario) "
        "tomando como fuente de verdad las tablas Django (auth_user/game_*)."
    )

    def handle(self, *args, **options):
        engine = connection.settings_dict.get('ENGINE', '')
        if 'mysql' not in engine:
            raise CommandError('Este comando solo se puede ejecutar con MySQL configurado como BD por defecto.')

        with transaction.atomic():
            self._sync_usuarios()
            self._sync_perfiles()
            self._sync_temas()
            self._prune_legacy()
            self._sync_progreso()

        self._print_summary()
        self.stdout.write(self.style.SUCCESS('Unificacion completada.'))

    def _exec(self, sql):
        with connection.cursor() as cursor:
            cursor.execute(sql)

    def _sync_usuarios(self):
        self._exec(
            """
            INSERT INTO usuarios (username, password_hash, activo, fecha_creacion)
            SELECT username, password, is_active, date_joined
            FROM auth_user
            ON DUPLICATE KEY UPDATE
                password_hash = VALUES(password_hash),
                activo = VALUES(activo),
                fecha_creacion = LEAST(usuarios.fecha_creacion, VALUES(fecha_creacion));
            """
        )

    def _sync_perfiles(self):
        self._exec(
            """
            INSERT INTO perfiles_usuario (
                usuario_id,
                fecha_nacimiento,
                genero,
                nombre_tutor,
                email_tutor,
                pais,
                fecha_creacion
            )
            SELECT
                ul.id,
                gp.fecha_nacimiento,
                gp.genero,
                gp.nombre_tutor,
                gp.email_tutor,
                gp.pais,
                gp.fecha_creacion
            FROM game_userprofile gp
            INNER JOIN auth_user au ON au.id = gp.usuario_id
            INNER JOIN usuarios ul ON ul.username = au.username
            ON DUPLICATE KEY UPDATE
                fecha_nacimiento = VALUES(fecha_nacimiento),
                genero = VALUES(genero),
                nombre_tutor = VALUES(nombre_tutor),
                email_tutor = VALUES(email_tutor),
                pais = VALUES(pais),
                fecha_creacion = LEAST(perfiles_usuario.fecha_creacion, VALUES(fecha_creacion));
            """
        )

    def _sync_temas(self):
        self._exec(
            """
            INSERT INTO temas (numero_tema, titulo, descripcion, orden, es_activo)
            SELECT numero_tema, titulo, descripcion, orden, es_activo
            FROM game_tema
            ON DUPLICATE KEY UPDATE
                titulo = VALUES(titulo),
                descripcion = VALUES(descripcion),
                orden = VALUES(orden),
                es_activo = VALUES(es_activo);
            """
        )

    def _sync_progreso(self):
        # Recalcula el progreso legado desde UserProfile para evitar divergencias acumuladas.
        self._exec('DELETE FROM progreso_usuario;')
        self._exec(
            """
            INSERT INTO progreso_usuario (usuario_id, tema_id, completado, desbloqueado, fecha_completado)
            SELECT
                ul.id,
                t.id,
                CASE WHEN t.orden < gp.ultimo_tema_desbloqueado THEN 1 ELSE 0 END AS completado,
                1 AS desbloqueado,
                CASE WHEN t.orden < gp.ultimo_tema_desbloqueado THEN NOW() ELSE NULL END AS fecha_completado
            FROM game_userprofile gp
            INNER JOIN auth_user au ON au.id = gp.usuario_id
            INNER JOIN usuarios ul ON ul.username = au.username
            INNER JOIN temas t ON t.orden <= gp.ultimo_tema_desbloqueado;
            """
        )

    def _prune_legacy(self):
        # Conserva en legacy solo lo que existe en las tablas Django fuente.
        self._exec(
            """
            DELETE u
            FROM usuarios u
            LEFT JOIN auth_user au ON au.username = u.username
            WHERE au.id IS NULL;
            """
        )
        self._exec(
            """
            DELETE p
            FROM perfiles_usuario p
            LEFT JOIN usuarios ul ON ul.id = p.usuario_id
            LEFT JOIN auth_user au ON au.username = ul.username
            LEFT JOIN game_userprofile gp ON gp.usuario_id = au.id
            WHERE gp.id IS NULL;
            """
        )
        self._exec(
            """
            DELETE t
            FROM temas t
            LEFT JOIN game_tema gt ON gt.numero_tema = t.numero_tema
            WHERE gt.id IS NULL;
            """
        )

    def _print_summary(self):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM auth_user) AS auth_users,
                    (SELECT COUNT(*) FROM game_userprofile) AS django_profiles,
                    (SELECT COUNT(*) FROM game_tema) AS django_temas,
                    (SELECT COUNT(*) FROM usuarios) AS legacy_users,
                    (SELECT COUNT(*) FROM perfiles_usuario) AS legacy_profiles,
                    (SELECT COUNT(*) FROM temas) AS legacy_temas,
                    (SELECT COUNT(*) FROM progreso_usuario) AS legacy_progreso;
                """
            )
            row = cursor.fetchone()

        self.stdout.write(
            f"Django(auth_user/game_userprofile/game_tema): {row[0]}/{row[1]}/{row[2]}"
        )
        self.stdout.write(
            f"Legado(usuarios/perfiles_usuario/temas/progreso_usuario): {row[3]}/{row[4]}/{row[5]}/{row[6]}"
        )
