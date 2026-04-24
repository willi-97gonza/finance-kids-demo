DROP DATABASE IF EXISTS financekids;
CREATE DATABASE financekids
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE financekids;

CREATE TABLE usuarios (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE perfiles_usuario (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id BIGINT UNSIGNED NOT NULL UNIQUE,
    fecha_nacimiento DATE NULL,
    genero ENUM('M', 'F') NULL,
    nombre_tutor VARCHAR(100) NULL,
    email_tutor VARCHAR(254) NULL,
    pais VARCHAR(50) NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_perfiles_usuario_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE
);

CREATE TABLE temas (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    numero_tema INT NOT NULL UNIQUE,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    orden INT NOT NULL,
    es_activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE preguntas (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tema_id BIGINT UNSIGNED NOT NULL,
    enunciado TEXT NOT NULL,
    orden INT NOT NULL,
    tipo ENUM('seleccion_unica', 'binaria') NOT NULL DEFAULT 'seleccion_unica',
    activa TINYINT(1) NOT NULL DEFAULT 1,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_preguntas_tema
        FOREIGN KEY (tema_id) REFERENCES temas(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_pregunta_por_tema_orden
        UNIQUE (tema_id, orden)
);

CREATE TABLE opciones_respuesta (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    pregunta_id BIGINT UNSIGNED NOT NULL,
    texto VARCHAR(255) NOT NULL,
    es_correcta TINYINT(1) NOT NULL DEFAULT 0,
    orden INT NOT NULL,
    CONSTRAINT fk_opciones_pregunta
        FOREIGN KEY (pregunta_id) REFERENCES preguntas(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_opcion_por_pregunta_orden
        UNIQUE (pregunta_id, orden)
);

CREATE TABLE progreso_usuario (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id BIGINT UNSIGNED NOT NULL,
    tema_id BIGINT UNSIGNED NOT NULL,
    completado TINYINT(1) NOT NULL DEFAULT 0,
    desbloqueado TINYINT(1) NOT NULL DEFAULT 0,
    fecha_completado DATETIME NULL,
    CONSTRAINT fk_progreso_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_progreso_tema
        FOREIGN KEY (tema_id) REFERENCES temas(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_progreso_usuario_tema
        UNIQUE (usuario_id, tema_id)
);

CREATE TABLE respuestas_usuario (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id BIGINT UNSIGNED NOT NULL,
    pregunta_id BIGINT UNSIGNED NOT NULL,
    opcion_id BIGINT UNSIGNED NOT NULL,
    es_correcta TINYINT(1) NOT NULL,
    respondida_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_respuesta_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_respuesta_pregunta
        FOREIGN KEY (pregunta_id) REFERENCES preguntas(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_respuesta_opcion
        FOREIGN KEY (opcion_id) REFERENCES opciones_respuesta(id)
        ON DELETE CASCADE
);

CREATE TABLE auditoria_usuarios (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id BIGINT UNSIGNED NOT NULL,
    accion VARCHAR(50) NOT NULL,
    detalle VARCHAR(255) NOT NULL,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_auditoria_usuarios_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE
);

CREATE TABLE auditoria_respuestas (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id BIGINT UNSIGNED NOT NULL,
    pregunta_id BIGINT UNSIGNED NOT NULL,
    opcion_id BIGINT UNSIGNED NOT NULL,
    accion VARCHAR(50) NOT NULL,
    detalle VARCHAR(255) NOT NULL,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_auditoria_respuestas_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_auditoria_respuestas_pregunta
        FOREIGN KEY (pregunta_id) REFERENCES preguntas(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_auditoria_respuestas_opcion
        FOREIGN KEY (opcion_id) REFERENCES opciones_respuesta(id)
        ON DELETE CASCADE
);

CREATE TABLE auditoria_progreso (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id BIGINT UNSIGNED NOT NULL,
    tema_id BIGINT UNSIGNED NOT NULL,
    accion VARCHAR(50) NOT NULL,
    detalle VARCHAR(255) NOT NULL,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_auditoria_progreso_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_auditoria_progreso_tema
        FOREIGN KEY (tema_id) REFERENCES temas(id)
        ON DELETE CASCADE
);

INSERT INTO temas (numero_tema, titulo, descripcion, orden, es_activo) VALUES
(1, '¿Qué es el dinero?', 'El dinero se usa para comprar cosas que necesitamos o queremos. También se puede guardar para el futuro: a eso se le llama ahorrar.', 1, 1),
(2, 'Presupuesto', 'Un presupuesto es una herramienta que ayuda a saber cuánto dinero tienes, cuánto gastas y cuánto puedes ahorrar.', 2, 1),
(3, 'Tema 3 en construcción', 'Próximamente estará disponible este nuevo tema.', 3, 0);

INSERT INTO preguntas (tema_id, enunciado, orden, tipo)
SELECT id, '¿Para qué sirve el dinero?', 1, 'binaria'
FROM temas WHERE numero_tema = 1;

INSERT INTO preguntas (tema_id, enunciado, orden, tipo)
SELECT id, '¿Qué significa ahorrar?', 2, 'binaria'
FROM temas WHERE numero_tema = 1;

INSERT INTO preguntas (tema_id, enunciado, orden, tipo)
SELECT id, '¿Cuál de estos no se compra con dinero?', 3, 'binaria'
FROM temas WHERE numero_tema = 1;

INSERT INTO preguntas (tema_id, enunciado, orden, tipo)
SELECT id, '¿Qué es un presupuesto?', 1, 'seleccion_unica'
FROM temas WHERE numero_tema = 2;

INSERT INTO preguntas (tema_id, enunciado, orden, tipo)
SELECT id, '¿Por qué es importante tener un presupuesto?', 2, 'seleccion_unica'
FROM temas WHERE numero_tema = 2;

INSERT INTO opciones_respuesta (pregunta_id, texto, es_correcta, orden)
SELECT p.id, 'Comprar cosas', 1, 1
FROM preguntas p
INNER JOIN temas t ON t.id = p.tema_id
WHERE t.numero_tema = 1 AND p.orden = 1;

INSERT INTO opciones_respuesta (pregunta_id, texto, es_correcta, orden)
SELECT p.id, 'Hacer magia', 0, 2
FROM preguntas p
INNER JOIN temas t ON t.id = p.tema_id
WHERE t.numero_tema = 1 AND p.orden = 1;

INSERT INTO opciones_respuesta (pregunta_id, texto, es_correcta, orden)
SELECT p.id, 'Guardar dinero para el futuro', 1, 1
FROM preguntas p
INNER JOIN temas t ON t.id = p.tema_id
WHERE t.numero_tema = 1 AND p.orden = 2;

INSERT INTO opciones_respuesta (pregunta_id, texto, es_correcta, orden)
SELECT p.id, 'Gastar todo ya', 0, 2
FROM preguntas p
INNER JOIN temas t ON t.id = p.tema_id
WHERE t.numero_tema = 1 AND p.orden = 2;

INSERT INTO opciones_respuesta (pregunta_id, texto, es_correcta, orden)
SELECT p.id, 'Un juguete', 0, 1
FROM preguntas p
INNER JOIN temas t ON t.id = p.tema_id
WHERE t.numero_tema = 1 AND p.orden = 3;

INSERT INTO opciones_respuesta (pregunta_id, texto, es_correcta, orden)
SELECT p.id, 'El amor', 1, 2
FROM preguntas p
INNER JOIN temas t ON t.id = p.tema_id
WHERE t.numero_tema = 1 AND p.orden = 3;

INSERT INTO opciones_respuesta (pregunta_id, texto, es_correcta, orden)
SELECT p.id, 'Es una herramienta para planificar gastos y ahorros.', 1, 1
FROM preguntas p
INNER JOIN temas t ON t.id = p.tema_id
WHERE t.numero_tema = 2 AND p.orden = 1;

INSERT INTO opciones_respuesta (pregunta_id, texto, es_correcta, orden)
SELECT p.id, 'Una forma de gastar sin control.', 0, 2
FROM preguntas p
INNER JOIN temas t ON t.id = p.tema_id
WHERE t.numero_tema = 2 AND p.orden = 1;

INSERT INTO opciones_respuesta (pregunta_id, texto, es_correcta, orden)
SELECT p.id, 'Un tipo de ahorro secreto.', 0, 3
FROM preguntas p
INNER JOIN temas t ON t.id = p.tema_id
WHERE t.numero_tema = 2 AND p.orden = 1;

INSERT INTO opciones_respuesta (pregunta_id, texto, es_correcta, orden)
SELECT p.id, 'Porque ayuda a organizar el dinero y cumplir metas.', 1, 1
FROM preguntas p
INNER JOIN temas t ON t.id = p.tema_id
WHERE t.numero_tema = 2 AND p.orden = 2;

INSERT INTO opciones_respuesta (pregunta_id, texto, es_correcta, orden)
SELECT p.id, 'Porque permite gastar más.', 0, 2
FROM preguntas p
INNER JOIN temas t ON t.id = p.tema_id
WHERE t.numero_tema = 2 AND p.orden = 2;

INSERT INTO opciones_respuesta (pregunta_id, texto, es_correcta, orden)
SELECT p.id, 'Porque es obligatorio por ley.', 0, 3
FROM preguntas p
INNER JOIN temas t ON t.id = p.tema_id
WHERE t.numero_tema = 2 AND p.orden = 2;

DELIMITER $$

CREATE TRIGGER tr_usuarios_ai
AFTER INSERT ON usuarios
FOR EACH ROW
BEGIN
    INSERT INTO auditoria_usuarios (usuario_id, accion, detalle)
    VALUES (NEW.id, 'usuario_creado', CONCAT('Se registró el usuario ', NEW.username));

    INSERT INTO progreso_usuario (usuario_id, tema_id, completado, desbloqueado, fecha_completado)
    SELECT NEW.id, t.id, 0, 1, NULL
    FROM temas t
    WHERE t.orden = 1
    LIMIT 1;

    INSERT INTO auditoria_progreso (usuario_id, tema_id, accion, detalle)
    SELECT NEW.id, t.id, 'progreso_inicial', 'Se habilitó automáticamente el tema 1 para el nuevo usuario'
    FROM temas t
    WHERE t.orden = 1
    LIMIT 1;
END$$

CREATE TRIGGER tr_respuestas_ai
AFTER INSERT ON respuestas_usuario
FOR EACH ROW
BEGIN
    DECLARE v_tema_id BIGINT UNSIGNED;
    DECLARE v_total_preguntas INT DEFAULT 0;
    DECLARE v_correctas_usuario INT DEFAULT 0;
    DECLARE v_orden_actual INT DEFAULT 0;
    DECLARE v_siguiente_tema_id BIGINT UNSIGNED DEFAULT NULL;
    DECLARE v_ya_completado TINYINT DEFAULT 0;

    SELECT p.tema_id
      INTO v_tema_id
    FROM preguntas p
    WHERE p.id = NEW.pregunta_id
    LIMIT 1;

    INSERT INTO auditoria_respuestas (usuario_id, pregunta_id, opcion_id, accion, detalle)
    VALUES (
        NEW.usuario_id,
        NEW.pregunta_id,
        NEW.opcion_id,
        'respuesta_registrada',
        CONCAT('Respuesta guardada. Correcta = ', NEW.es_correcta)
    );

    IF v_tema_id IS NOT NULL THEN
        SELECT COUNT(*)
          INTO v_total_preguntas
        FROM preguntas
        WHERE tema_id = v_tema_id
          AND activa = 1;

        SELECT COUNT(DISTINCT ru.pregunta_id)
          INTO v_correctas_usuario
        FROM respuestas_usuario ru
        INNER JOIN preguntas p ON p.id = ru.pregunta_id
        WHERE ru.usuario_id = NEW.usuario_id
          AND p.tema_id = v_tema_id
          AND ru.es_correcta = 1;

        SELECT COALESCE(completado, 0)
          INTO v_ya_completado
        FROM progreso_usuario
        WHERE usuario_id = NEW.usuario_id
          AND tema_id = v_tema_id
        LIMIT 1;

        IF v_total_preguntas > 0 AND v_correctas_usuario >= v_total_preguntas AND v_ya_completado = 0 THEN
            INSERT INTO progreso_usuario (usuario_id, tema_id, completado, desbloqueado, fecha_completado)
            VALUES (NEW.usuario_id, v_tema_id, 1, 1, NOW())
            ON DUPLICATE KEY UPDATE
                completado = 1,
                desbloqueado = 1,
                fecha_completado = IFNULL(fecha_completado, NOW());

            INSERT INTO auditoria_progreso (usuario_id, tema_id, accion, detalle)
            VALUES (
                NEW.usuario_id,
                v_tema_id,
                'tema_completado',
                'El tema fue completado por responder correctamente todas sus preguntas activas'
            );

            SELECT orden
              INTO v_orden_actual
            FROM temas
            WHERE id = v_tema_id
            LIMIT 1;

            SELECT id
              INTO v_siguiente_tema_id
            FROM temas
            WHERE orden = v_orden_actual + 1
            LIMIT 1;

            IF v_siguiente_tema_id IS NOT NULL THEN
                INSERT INTO progreso_usuario (usuario_id, tema_id, completado, desbloqueado, fecha_completado)
                VALUES (NEW.usuario_id, v_siguiente_tema_id, 0, 1, NULL)
                ON DUPLICATE KEY UPDATE
                    desbloqueado = 1;

                INSERT INTO auditoria_progreso (usuario_id, tema_id, accion, detalle)
                VALUES (
                    NEW.usuario_id,
                    v_siguiente_tema_id,
                    'tema_desbloqueado',
                    'El siguiente tema quedó habilitado por avance automático'
                );
            END IF;
        END IF;
    END IF;
END$$

DELIMITER ;

INSERT INTO usuarios (username, password_hash, activo)
VALUES ('demo_financekids', 'cambiar_por_hash_real', 1);

INSERT INTO perfiles_usuario (
    usuario_id, fecha_nacimiento, genero, nombre_tutor, email_tutor, pais
)
SELECT id, '2015-05-10', 'M', 'Tutor Demo', 'tutor@example.com', 'Colombia'
FROM usuarios
WHERE username = 'demo_financekids';

-- ==========================================
-- CONSULTAS DE PRUEBA PARA DBeaver
-- Ejecuta estas sentencias después del script
-- ==========================================

-- 1. Ver el desbloqueo automático del tema 1 tras crear usuario
-- INSERT INTO usuarios (username, password_hash, activo)
-- VALUES ('ana_demo', 'hash_demo', 1);
--
-- SELECT * FROM progreso_usuario WHERE usuario_id = (SELECT id FROM usuarios WHERE username = 'ana_demo');
-- SELECT * FROM auditoria_usuarios ORDER BY id DESC;
-- SELECT * FROM auditoria_progreso ORDER BY id DESC;

-- 2. Responder correctamente el tema 1 y revisar el desbloqueo del tema 2
-- INSERT INTO respuestas_usuario (usuario_id, pregunta_id, opcion_id, es_correcta)
-- SELECT u.id, p.id, o.id, o.es_correcta
-- FROM usuarios u
-- JOIN preguntas p ON p.orden = 1
-- JOIN temas t ON t.id = p.tema_id AND t.numero_tema = 1
-- JOIN opciones_respuesta o ON o.pregunta_id = p.id AND o.es_correcta = 1
-- WHERE u.username = 'ana_demo';
--
-- INSERT INTO respuestas_usuario (usuario_id, pregunta_id, opcion_id, es_correcta)
-- SELECT u.id, p.id, o.id, o.es_correcta
-- FROM usuarios u
-- JOIN preguntas p ON p.orden = 2
-- JOIN temas t ON t.id = p.tema_id AND t.numero_tema = 1
-- JOIN opciones_respuesta o ON o.pregunta_id = p.id AND o.es_correcta = 1
-- WHERE u.username = 'ana_demo';
--
-- INSERT INTO respuestas_usuario (usuario_id, pregunta_id, opcion_id, es_correcta)
-- SELECT u.id, p.id, o.id, o.es_correcta
-- FROM usuarios u
-- JOIN preguntas p ON p.orden = 3
-- JOIN temas t ON t.id = p.tema_id AND t.numero_tema = 1
-- JOIN opciones_respuesta o ON o.pregunta_id = p.id AND o.es_correcta = 1
-- WHERE u.username = 'ana_demo';
--
-- SELECT * FROM respuestas_usuario WHERE usuario_id = (SELECT id FROM usuarios WHERE username = 'ana_demo');
-- SELECT * FROM auditoria_respuestas ORDER BY id DESC;
-- SELECT * FROM progreso_usuario WHERE usuario_id = (SELECT id FROM usuarios WHERE username = 'ana_demo') ORDER BY tema_id;
-- SELECT * FROM auditoria_progreso ORDER BY id DESC;
