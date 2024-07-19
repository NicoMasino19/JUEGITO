import pygame
import sys
import random
import math
import time 
import os

# Definir tamaño de pantalla
ancho = 800
alto = 600

# Inicialización
pygame.init()
pygame.mixer.init()
ancho, alto = 800, 600

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
MORADO = (128, 0, 128)
NARANJA = (255, 165, 0)
GRIS = (128, 128, 128)

# Get the base path for resources
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

# Cargar sonidos con rutas correctas
sonido_disparo = pygame.mixer.Sound(os.path.join(base_path, "disparo.wav"))
sonido_dano = pygame.mixer.Sound(os.path.join(base_path, "dano.wav"))
sonido_bomba = pygame.mixer.Sound(os.path.join(base_path, "bomba.wav"))
sonido_powerup = pygame.mixer.Sound(os.path.join(base_path, "powerup.wav"))
sonido_vida = pygame.mixer.Sound(os.path.join(base_path, "vida.wav"))
sonido_jefe = pygame.mixer.Sound(os.path.join(base_path, "jefe.wav"))

def distancia(rect1, rect2):
    # Asumimos que rect2 puede ser un diccionario o un Rect
    if isinstance(rect2, dict):
        rect2 = rect2['rect']
    return math.sqrt((rect1.centerx - rect2.centerx)**2 + (rect1.centery - rect2.centery)**2)

def encontrar_enemigo_cercano(jugador, enemigos, jefes):
    todos_enemigos = enemigos + jefes
    if not todos_enemigos:
        return None
    return min(todos_enemigos, key=lambda enemigo: distancia(jugador, enemigo['rect'] if isinstance(enemigo, dict) else enemigo))


def dibujar_triangulo(superficie, color, rect):
    pygame.draw.polygon(superficie, color, [
        (rect.left + rect.width // 2, rect.top),
        (rect.left, rect.bottom),
        (rect.right, rect.bottom)
    ])

def actualizar_dificultad(tiempo_actual, tiempo_inicio):
    minutos_transcurridos = (tiempo_actual - tiempo_inicio) / 60000
    factor_dificultad = 1 + (minutos_transcurridos * 0.5)
    velocidad_enemigo = 1 + (factor_dificultad / 3)
    return factor_dificultad, velocidad_enemigo

def aplicar_colision_enemigos(enemigos, jefes):
    todos_enemigos = enemigos + jefes
    for i, enemigo1 in enumerate(todos_enemigos):
        for enemigo2 in todos_enemigos[i+1:]:
            if enemigo1['rect'].colliderect(enemigo2['rect']):
                # Calcular vector de separación
                dx = enemigo1['rect'].centerx - enemigo2['rect'].centerx
                dy = enemigo1['rect'].centery - enemigo2['rect'].centery
                distancia = max(1, math.sqrt(dx*dx + dy*dy))  # Evitar división por cero
                
                # Normalizar el vector
                dx /= distancia
                dy /= distancia
                
                # Aplicar separación
                fuerza_separacion = 1.0  # Ajusta este valor para cambiar la fuerza de separación
                enemigo1['rect'].x += dx * fuerza_separacion
                enemigo1['rect'].y += dy * fuerza_separacion
                enemigo2['rect'].x -= dx * fuerza_separacion
                enemigo2['rect'].y -= dy * fuerza_separacion

import math

def mover_estrellas(jugador, estrellas, delta_tiempo):
    for estrella in estrellas:
        dx = jugador.centerx - estrella['x']
        dy = jugador.centery - estrella['y']
        distancia = math.sqrt(dx**2 + dy**2)
        
        if distancia < 5:  # Si está muy cerca, moverla directamente al jugador
            estrella['x'] = jugador.centerx
            estrella['y'] = jugador.centery
        else:
            velocidad = min(7000 / (distancia), 500000)  # Velocidad aumenta al acercarse pero está limitada
            factor_movimiento = velocidad * delta_tiempo
            estrella['x'] += (dx / distancia) * factor_movimiento
            estrella['y'] += (dy / distancia) * factor_movimiento

def mover_estrellas_jefe(jugador, estrellas, delta_tiempo):
    for estrella in estrellas:
        dx = jugador.centerx - estrella['x']
        dy = jugador.centery - estrella['y']
        distancia = math.sqrt(dx**2 + dy**2)
        
        if distancia < 5:  # Si está muy cerca, moverla directamente al jugador
            estrella['x'] = jugador.centerx
            estrella['y'] = jugador.centery
        else:
            velocidad = min(7000 / (distancia), 500000)  # Velocidad aumenta al acercarse pero está limitada
            factor_movimiento = velocidad * delta_tiempo
            estrella['x'] += (dx / distancia) * factor_movimiento
            estrella['y'] += (dy / distancia) * factor_movimiento


# Modificar la función de generación de enemigos
def generar_enemigos(enemigos, tiempo_actual, tiempo_inicio, factor_dificultad):
    base_enemy_spawn_rate = 50 * factor_dificultad 
    max_enemies = 50
    enemy_spawn_rate = max(2, int(base_enemy_spawn_rate / factor_dificultad))
    num_enemies_to_spawn = random.randint(1, max(1, int(factor_dificultad)))

    if len(enemigos) < max_enemies and random.randint(1, enemy_spawn_rate) == 1:
        for _ in range(num_enemies_to_spawn):
            lado = random.choice(['arriba', 'abajo', 'izquierda', 'derecha'])
            if lado == 'arriba':
                enemigo = {'rect': pygame.Rect(random.randint(0, ancho), -20, 20, 20), 'vida': int(2 * factor_dificultad)}
            elif lado == 'abajo':
                enemigo = {'rect': pygame.Rect(random.randint(0, ancho), alto + 20, 20, 20), 'vida': int(2 * factor_dificultad)}
            elif lado == 'izquierda':
                enemigo = {'rect': pygame.Rect(-20, random.randint(0, alto), 20, 20), 'vida': int(2 * factor_dificultad)}
            else:
                enemigo = {'rect': pygame.Rect(ancho + 20, random.randint(0, alto), 20, 20), 'vida': int(2 * factor_dificultad)}
            enemigos.append(enemigo)

# Modificar la función de colisiones proyectil-enemigo
def manejar_colisiones_proyectil_enemigo(proyectiles, enemigos, jefes, puntuacion, dano_jugador, numeros_dano, tiempo_actual, estrellas_xp, estrellas_xp_jefe):
    for proyectil in proyectiles[:]:
        for enemigo in enemigos[:]:
            if proyectil['rect'].colliderect(enemigo['rect']):
                if proyectil in proyectiles:
                    proyectiles.remove(proyectil)
                
                # Calcular daño con posibilidad de crítico
                es_critico = random.random() < 0.15  # 10% de probabilidad de crítico
                dano_actual = dano_jugador * 2 if es_critico else dano_jugador
                
                enemigo['vida'] -= dano_actual
                if enemigo['vida'] <= 0:
                    enemigos.remove(enemigo)
                    # Soltar estrella de experiencia
                    estrellas_xp.append({'x': enemigo['rect'].centerx, 'y': enemigo['rect'].centery})
                    puntuacion += 1
                
                # Agregar número de daño
                numeros_dano.append({
                    'numero': str(int(dano_actual)),
                    'pos': enemigo['rect'].center,
                    'tiempo': tiempo_actual,
                    'color': AMARILLO if es_critico else BLANCO
                })
                break
        
        for jefe in jefes[:]:
            if proyectil['rect'].colliderect(jefe['rect']):
                if proyectil in proyectiles:
                    proyectiles.remove(proyectil)
                
                # Calcular daño con posibilidad de crítico
                es_critico = random.random() < 0.1  # 10% de probabilidad de crítico
                dano_actual = dano_jugador * 2 if es_critico else dano_jugador
                
                jefe['vida'] -= dano_actual
                # Agregar número de daño
                numeros_dano.append({
                    'numero': str(int(dano_actual)),
                    'pos': proyectil['rect'].center,
                    'tiempo': tiempo_actual,
                    'color': AMARILLO if es_critico else BLANCO
                })
                if jefe['vida'] <= 0:
                    jefes.remove(jefe)
                    puntuacion += 50
                    # Soltar item de mejora de vida máxima
                    estrellas_xp_jefe.append(pygame.Rect(jefe['rect'].centerx, jefe['rect'].centery, 15, 15))
                break
    
    return puntuacion

def mostrar_opciones_mejora(pantalla, fuente):
    opciones = ["Daño", "Velocidad de Ataque", "VidaMax"]
    ancho_boton = 250
    alto_boton = 50
    espaciado = 20
    total_alto = (alto_boton + espaciado) * len(opciones) - espaciado

    # Oscurecer el fondo
    s = pygame.Surface((pantalla.get_width(), pantalla.get_height()))
    s.set_alpha(128)
    s.fill(NEGRO)
    pantalla.blit(s, (0, 0))

    seleccion = None
    while seleccion is None:
        y_start = (pantalla.get_height() - total_alto) // 2
        for i, opcion in enumerate(opciones):
            rect = pygame.Rect((pantalla.get_width() - ancho_boton) // 2, 
                               y_start + i * (alto_boton + espaciado), 
                               ancho_boton, alto_boton)
            color = GRIS
            if rect.collidepoint(pygame.mouse.get_pos()):
                color = BLANCO
                if pygame.mouse.get_pressed()[0]:
                    seleccion = opcion

            pygame.draw.rect(pantalla, color, rect)
            texto = fuente.render(opcion, True, NEGRO)
            texto_rect = texto.get_rect(center=rect.center)
            pantalla.blit(texto, texto_rect)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return None

        pygame.display.flip()
    time.sleep(1/2)
    return seleccion