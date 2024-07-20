import pygame
import sys
import random
import math
from vampire_survivor_funciones import *
from database_utils import save_score, get_high_scores
import os

# Definir constantes de color
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
MORADO = (128, 0, 128)
NARANJA = (255, 165, 0)
GRIS = (128, 128, 128)

# Definir tamaño de pantalla
ancho = 800
alto = 600

# Inicialización
pygame.init()
pygame.mixer.init()

# Función para obtener la ruta de recursos
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Cargar sonidos con rutas correctas
sonido_disparo = pygame.mixer.Sound(resource_path("disparo.wav"))
sonido_dano = pygame.mixer.Sound(resource_path("dano.wav"))
sonido_bomba = pygame.mixer.Sound(resource_path("bomba.wav"))
sonido_powerup = pygame.mixer.Sound(resource_path("powerup.wav"))
sonido_vida = pygame.mixer.Sound(resource_path("vida.wav"))
sonido_jefe = pygame.mixer.Sound(resource_path("jefe.wav"))

# Nuevas variables para el sistema de experiencia
experiencia = 0
nivel = 1
experiencia_para_nivel = 100
estrellas_xp = []
estrellas_xp_jefe = []

def juego():
    global experiencia, nivel, experiencia_para_nivel, dano_jugador, aumento_velocidad_disparo, vida_maxima, vida_jugador
    pantalla = pygame.display.set_mode((ancho, alto))
    pygame.display.set_caption("Vampire Survivor Simplificado")

    # Dificultad
    tiempo_inicio = pygame.time.get_ticks()
    factor_dificultad = 1.0

    # Jugador
    jugador = pygame.Rect(ancho // 2, alto // 2, 20, 20)
    velocidad_jugador = 5
    vida_jugador = 10
    vida_maxima = 10
    invulnerable = False
    tiempo_invulnerable = 0
    jugador_moviendo = False
    tiempo_ultimo_movimiento = 0
    tiempo_espera_disparo = 100 
    dano_jugador = round(1, 2)

    # Velocidades
    velocidad_enemigo = 2
    velocidad_proyectil = 8

    #Bombas
    bombas = []
    tiempo_ultima_bomba = 0
    radio_explosion = 175
    duracion_bomba = 15000 
    tiempo_parpadeo = 2000
    intervalo_parpadeo_inicial = 4000 
    intervalo_parpadeo_minimo = 500  

    # Explosiones
    explosiones = []

    # Power-ups
    triangulos = []
    tiempo_ultimo_triangulo = 0

    # Orbes de vida
    orbes_vida = []
    tiempo_ultimo_orbe = 0
    intervalo_orbe = 10000
    
    # Jefes
    jefes = []
    tiempo_ultimo_jefe = 0
    intervalo_jefe = 45000
    vida_jefe = 20 * (2**(2*factor_dificultad))

    # Items de mejora de vida máxima
    items_mejora_vida = []

    # Disparo
    tiempo_ultimo_disparo = 0
    intervalo_disparo = 1000
    aumento_velocidad_disparo = 1
    numeros_dano = []

    tiempo_ultimo = 0
    ejecutando = True
    reloj = pygame.time.Clock()
    puntuacion = 0
    enemigos = []
    proyectiles = []

    while ejecutando and vida_jugador > 0:
        tiempo_actual = pygame.time.get_ticks()
        delta_tiempo = (tiempo_actual - tiempo_ultimo) / 1000.0
        tiempo_ultimo = tiempo_actual
        if sys.stdout is not None:
            sys.stdout.flush()
        factor_dificultad, velocidad_enemigo = actualizar_dificultad(tiempo_actual, tiempo_inicio)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

        # Movimiento del jugador
        teclas = pygame.key.get_pressed()
        jugador_moviendo = False
        if teclas[pygame.K_LEFT]:
            jugador.x -= velocidad_jugador
            jugador_moviendo = True
        if teclas[pygame.K_RIGHT]:
            jugador.x += velocidad_jugador
            jugador_moviendo = True
        if teclas[pygame.K_UP]:
            jugador.y -= velocidad_jugador
            jugador_moviendo = True
        if teclas[pygame.K_DOWN]:
            jugador.y += velocidad_jugador
            jugador_moviendo = True

        jugador.clamp_ip(pantalla.get_rect())

        if jugador_moviendo:
            tiempo_ultimo_movimiento = tiempo_actual

         # Generar enemigos
        generar_enemigos(enemigos, tiempo_actual, tiempo_inicio, factor_dificultad)

        # Generar jefes
        if tiempo_actual - tiempo_ultimo_jefe > intervalo_jefe:
            jefes.append({
                'rect': pygame.Rect(random.randint(0, ancho), random.randint(0, alto), 40, 40),
                'vida': vida_jefe
            })
            tiempo_ultimo_jefe = tiempo_actual
            sonido_jefe.play()

        # Generar bombas, triángulos y orbes de vida
        # Modificar la generación de bombas:
        if tiempo_actual - tiempo_ultima_bomba > 10000 / factor_dificultad:
            nueva_bomba = {
                'rect': pygame.Rect(random.randint(0, ancho), random.randint(0, alto), 15, 15),
                'tiempo_creacion': tiempo_actual,
                'visible': True
            }
            bombas.append(nueva_bomba)
            tiempo_ultima_bomba = tiempo_actual

        # Manejar bombas
        for bomba in bombas[:]:
            tiempo_actual = pygame.time.get_ticks()
            tiempo_restante = duracion_bomba - (tiempo_actual - bomba['tiempo_creacion'])
            
            if tiempo_restante <= 0:
                bombas.remove(bomba)
                continue
            
            # La bomba parpadea solo en los últimos segundos
            if tiempo_restante <= tiempo_parpadeo:
                # Calcular el intervalo de parpadeo actual
                intervalo_parpadeo = max(intervalo_parpadeo_minimo, 
                                        intervalo_parpadeo_inicial * (tiempo_restante / tiempo_parpadeo))
                
                # Actualizar visibilidad de la bomba
                if tiempo_actual % int(intervalo_parpadeo * 2) < intervalo_parpadeo:
                    bomba['visible'] = True
                else:
                    bomba['visible'] = False
            else:
                bomba['visible'] = True


        if tiempo_actual - tiempo_ultimo_triangulo > 15000:
            triangulos.append(pygame.Rect(random.randint(0, ancho), random.randint(0, alto), 15, 15))
            tiempo_ultimo_triangulo = tiempo_actual

        if tiempo_actual - tiempo_ultimo_orbe > intervalo_orbe:
            orbes_vida.append(pygame.Rect(random.randint(0, ancho), random.randint(0, alto), 10, 10))
            tiempo_ultimo_orbe = tiempo_actual

        # Mover enemigos y jefes hacia el jugador
        for enemigo in enemigos + jefes:
            dx = jugador.centerx - enemigo['rect'].centerx
            dy = jugador.centery - enemigo['rect'].centery
            dist = math.sqrt(dx*dx + dy*dy)
            if dist != 0:
                enemigo['rect'].x += (dx / dist) * velocidad_enemigo
                enemigo['rect'].y += (dy / dist) * velocidad_enemigo

           # Colisión jugador-enemigo/jefe
        if not invulnerable:
            for enemigo in enemigos:
                if jugador.colliderect(enemigo['rect']):
                    if factor_dificultad > 2:
                        vida_jugador -= 1 * factor_dificultad 
                    else:
                        vida_jugador -= 1 
                    invulnerable = True
                    tiempo_invulnerable = tiempo_actual
                    sonido_dano.play()
                    break
        
            for jefe in jefes:
                if jugador.colliderect(jefe['rect']):
                    if factor_dificultad > 2:
                        vida_jugador -= 3 * factor_dificultad 
                    else:
                        vida_jugador -= 3
                    invulnerable = True
                    tiempo_invulnerable = tiempo_actual
                    sonido_dano.play()
                    break

        aplicar_colision_enemigos(enemigos, jefes)


        # Manejar invulnerabilidad
        if invulnerable and tiempo_actual - tiempo_invulnerable > 800:
            invulnerable = False

        # Generar proyectiles solo cuando el jugador está quieto
        if not jugador_moviendo and tiempo_actual - tiempo_ultimo_movimiento > tiempo_espera_disparo:
            if tiempo_actual - tiempo_ultimo_disparo > intervalo_disparo / aumento_velocidad_disparo:
                enemigo_cercano = encontrar_enemigo_cercano(jugador, enemigos, jefes)
                if enemigo_cercano:
                    enemigo_rect = enemigo_cercano['rect'] if isinstance(enemigo_cercano, dict) else enemigo_cercano
                    dx = enemigo_rect.centerx - jugador.centerx
                    dy = enemigo_rect.centery - jugador.centery
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        dx, dy = dx/dist, dy/dist
                        proyectiles.append({
                            'rect': pygame.Rect(jugador.centerx, jugador.centery, 5, 5),
                            'dx': dx,
                            'dy': dy
                        })
                    tiempo_ultimo_disparo = tiempo_actual
                    sonido_disparo.play()
                    
        # Mover proyectiles
        for proyectil in proyectiles:
            proyectil['rect'].x += proyectil['dx'] * velocidad_proyectil
            proyectil['rect'].y += proyectil['dy'] * velocidad_proyectil

        # Manejar colisiones proyectil-enemigo y proyectil-jefe
        puntuacion = manejar_colisiones_proyectil_enemigo(proyectiles, enemigos, jefes, puntuacion, dano_jugador, numeros_dano, tiempo_actual, estrellas_xp, items_mejora_vida)

        # Actualizar y eliminar números de daño
        for numero in numeros_dano[:]:
            if tiempo_actual - numero['tiempo'] > 500:  # El número desaparece después de 500ms
                numeros_dano.remove(numero)

         # Colisiones jugador-bomba y explosión
        for bomba in bombas[:]:
            if jugador.colliderect(bomba['rect']) and bomba['visible']:
                bombas.remove(bomba)
                explosiones.append({'centro': bomba['rect'].center, 'radio': 0, 'max_radio': radio_explosion})
                enemigos_afectados = [e for e in enemigos if distancia(bomba['rect'], e['rect']) <= radio_explosion]
                for e in enemigos_afectados:
                    e['vida'] -= 10  # Las bombas hacen 10 de daño
                    if e['vida'] <= 0:
                        if e in enemigos:
                            enemigos.remove(e)
                            puntuacion += 1
                jefes_afectados = [j for j in jefes if distancia(bomba['rect'], j['rect']) <= radio_explosion]
                for j in jefes_afectados:
                    j['vida'] -= 10  # Las bombas hacen 10 de daño a los jefes también
                    if j['vida'] <= 0:
                        if j in jefes:
                            jefes.remove(j)
                            puntuacion += 50
                sonido_bomba.play()

        # Actualizar explosiones
        for explosion in explosiones[:]:
            explosion['radio'] += 5
            if explosion['radio'] >= explosion['max_radio']:
                explosiones.remove(explosion)

        # Colisiones jugador-triángulo (power-up de velocidad de disparo)
        for triangulo in triangulos[:]:
            if jugador.colliderect(triangulo):
                triangulos.remove(triangulo)
                aumento_velocidad_disparo += 0.2
                sonido_powerup.play()

        # Colisiones jugador-orbe de vida
        for orbe in orbes_vida[:]:
            if jugador.colliderect(orbe):
                orbes_vida.remove(orbe)
                vida_jugador = min(vida_jugador + 2, vida_maxima)
                sonido_vida.play()

        # Colisiones jugador-item de mejora de vida máxima
        for item in items_mejora_vida[:]:
            if jugador.colliderect(item):
                items_mejora_vida.remove(item)
                vida_maxima += 5
                vida_jugador = vida_maxima
                sonido_powerup.play()

        # Mover y recoger estrellas de experiencia
        mover_estrellas(jugador, estrellas_xp, delta_tiempo)
        for estrella in estrellas_xp[:]:
            if jugador.collidepoint(estrella['x'], estrella['y']):
                estrellas_xp.remove(estrella)
                experiencia += 10
                if experiencia >= experiencia_para_nivel:
                    nivel += 1
                    experiencia -= experiencia_para_nivel
                    experiencia_para_nivel = int(experiencia_para_nivel * 1.2)

                    mejora_seleccionada = mostrar_opciones_mejora(pantalla, fuente)
                    if mejora_seleccionada == "Daño":
                        dano_jugador += 0.8
                    elif mejora_seleccionada == "Velocidad de Ataque":
                        aumento_velocidad_disparo += 1
                    elif mejora_seleccionada == "VidaMax":
                        vida_maxima += 5
                        vida_jugador = min(vida_jugador + 5, vida_maxima)
                    sonido_powerup.play()

        mover_estrellas_jefe(jugador, estrellas_xp_jefe, delta_tiempo)
        for estrella in estrellas_xp[:]:
            if jugador.collidepoint(estrella['x'], estrella['y']):
                estrellas_xp.remove(estrella)
                experiencia += 100
                if experiencia >= experiencia_para_nivel:
                    nivel += 1
                    experiencia -= experiencia_para_nivel
                    experiencia_para_nivel = int(experiencia_para_nivel * 1.2)

                    mejora_seleccionada = mostrar_opciones_mejora(pantalla, fuente)
                    if mejora_seleccionada == "Daño":
                        dano_jugador += 0.8
                    elif mejora_seleccionada == "Velocidad de Ataque":
                        aumento_velocidad_disparo += 1
                    elif mejora_seleccionada == "VidaMax":
                        vida_maxima += 20
                        vida_jugador = min(vida_jugador + 5, vida_maxima)
                    sonido_powerup.play()
                    

        # Eliminar proyectiles fuera de pantalla
        proyectiles = [p for p in proyectiles if pantalla.get_rect().colliderect(p['rect'])]




        # Dibujar todo
        pantalla.fill(NEGRO)
        
        # Dibujar barra de vida del jugador
        pygame.draw.rect(pantalla, ROJO, (10, 10, 200, 20))
        pygame.draw.rect(pantalla, VERDE, (10, 10, 200 * (vida_jugador / vida_maxima), 20))

        if invulnerable:
            pygame.draw.rect(pantalla, AMARILLO, jugador)
        else:
            pygame.draw.rect(pantalla, BLANCO, jugador)
        
        # Dibujar enemigos con barra de vida
        for enemigo in enemigos:
            pygame.draw.rect(pantalla, ROJO, enemigo['rect'])
            # Dibujar barra de vida del enemigo
            vida_maxima_enemigo = int(2 * factor_dificultad)
            pygame.draw.rect(pantalla, ROJO, (enemigo['rect'].x, enemigo['rect'].y - 5, 20, 3))
            pygame.draw.rect(pantalla, VERDE, (enemigo['rect'].x, enemigo['rect'].y - 5, 20 * (enemigo['vida'] / vida_maxima_enemigo), 3))

        for jefe in jefes:
            pygame.draw.rect(pantalla, MORADO, jefe['rect'])
            # Dibujar barra de vida del jefe
            pygame.draw.rect(pantalla, ROJO, (jefe['rect'].x, jefe['rect'].y - 10, 40, 5))
            pygame.draw.rect(pantalla, VERDE, (jefe['rect'].x, jefe['rect'].y - 10, 40 * (jefe['vida'] / vida_jefe), 5))
        for proyectil in proyectiles:
            pygame.draw.rect(pantalla, BLANCO, proyectil['rect'])
        for bomba in bombas:
            if bomba['visible']:
                pygame.draw.rect(pantalla, AMARILLO, bomba['rect'])
        for triangulo in triangulos:
            dibujar_triangulo(pantalla, VERDE, triangulo)
        for orbe in orbes_vida:
            pygame.draw.rect(pantalla, AZUL, orbe)
        for item in items_mejora_vida:
            pygame.draw.rect(pantalla, NARANJA, item)

         # Dibujar números de daño
        fuente_dano = pygame.font.Font(None, 24)
        for numero in numeros_dano:
            texto_dano = fuente_dano.render(numero['numero'], True, numero['color'])
            pantalla.blit(texto_dano, (numero['pos'][0] - texto_dano.get_width() // 2, 
                                    numero['pos'][1] - texto_dano.get_height() // 2))
        
        # Dibujar explosiones
        for explosion in explosiones:
            pygame.draw.circle(pantalla, NARANJA, explosion['centro'], explosion['radio'], 2)

        # Mostrar puntuación, nivel de dificultad, vida máxima y daño del jugador
        fuente = pygame.font.Font(None, 36)
        texto_puntuacion = fuente.render(f"Puntuación: {puntuacion}", True, BLANCO)
        texto_dificultad = fuente.render(f"Dificultad: x{factor_dificultad:.1f}", True, BLANCO)
        texto_vida_maxima = fuente.render(f"Vida Máxima: {vida_maxima}", True, BLANCO)
        texto_dano_jugador = fuente.render(f"Daño: {dano_jugador}", True, BLANCO)
        pantalla.blit(texto_puntuacion, (10, 40))
        pantalla.blit(texto_dificultad, (10, 70))
        pantalla.blit(texto_vida_maxima, (10, 100))
        pantalla.blit(texto_dano_jugador, (10, 130))

        # Dibujar estrellas de experiencia
        for estrella in estrellas_xp:
            pygame.draw.circle(pantalla, AMARILLO, (int(estrella['x']), int(estrella['y'])), 3)

        # Dibujar barra de experiencia
        pygame.draw.rect(pantalla, AZUL, (10, alto - 30, 200, 20))
        pygame.draw.rect(pantalla, VERDE, (10, alto - 30, 200 * (experiencia / experiencia_para_nivel), 20))

        # Mostrar nivel
        texto_nivel = fuente.render(f"Nivel: {nivel}", True, BLANCO)
        pantalla.blit(texto_nivel, (220, alto - 30))

        if vida_jugador == 0:
            # Mostrar pantalla de Game Over
            pantalla.fill(NEGRO)
            fuente_grande = pygame.font.Font(None, 72)
            texto_game_over = fuente_grande.render("GAME OVER", True, ROJO)
            texto_puntuacion = fuente.render(f"Puntuación final: {puntuacion}", True, BLANCO)
            pantalla.blit(texto_game_over, (ancho//2 - texto_game_over.get_width()//2, alto//2 - 50))
            pantalla.blit(texto_puntuacion, (ancho//2 - texto_puntuacion.get_width()//2, alto//2 + 50))
            pygame.display.flip()

            # Wait for a moment before proceeding
            pygame.time.wait(2000)

            # Get player name
            player_name = get_text_input(pantalla, "Enter your name:")

            # Save score to database
            save_score(player_name, puntuacion, tiempo_actual - tiempo_inicio, factor_dificultad)

            # Display high scores
            high_scores = get_high_scores()
            display_high_scores(pantalla, high_scores)

            ejecutando = False
            

        pygame.display.flip()  # Update the screen
        reloj.tick(60)  # Maintain 60 FPS

        

    # Esperar a que el jugador cierre la ventana
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                esperando = False

    pygame.quit()

if __name__ == "__main__":
    juego()