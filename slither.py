import pygame
import math
import random

# --- Configurações ---
LARGURA, ALTURA = 800, 600
FPS = 60

# Cores
PRETO = (15, 15, 25)
VERDE = (50, 220, 100)
VERDE_ESCURO = (30, 150, 70)
VERMELHO = (230, 60, 60)
BRANCO = (255, 255, 255)

pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Slither Clone")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont("Arial", 20, bold=True)


class Cobra:
    def __init__(self, x, y, cor=VERDE):
        self.pos = pygame.Vector2(x, y)
        self.angulo = 0                    # direção em radianos
        self.velocidade = 3
        self.tamanho_segmento = 12         # distância entre segmentos
        self.corpo = [pygame.Vector2(x, y) for _ in range(15)]  # segmentos
        self.cor = cor
        self.raio = 10
        self.viva = True
        self.pontos = 0

    def mover(self, alvo_mouse=None):
        if not self.viva:
            return

        # Vira em direção ao mouse (ou mantém direção)
        if alvo_mouse:
            dx = alvo_mouse[0] - LARGURA / 2
            dy = alvo_mouse[1] - ALTURA / 2
            if dx != 0 or dy != 0:
                angulo_alvo = math.atan2(dy, dx)
                # Rotação suave
                diferenca = (angulo_alvo - self.angulo + math.pi) % (2 * math.pi) - math.pi
                self.angulo += diferenca * 0.1

        # Move a cabeça
        self.pos.x += math.cos(self.angulo) * self.velocidade
        self.pos.y += math.sin(self.angulo) * self.velocidade

        # Atualiza o corpo (cada segmento segue o anterior)
        self.corpo.insert(0, pygame.Vector2(self.pos))
        # Remove segmentos extras mantendo o tamanho
        while len(self.corpo) > self.pontos + 15:
            self.corpo.pop()

    def desenhar(self, tela, camera):
        if not self.viva:
            return

        # Desenha do rabo pra cabeça (pra ficar bonito)
        for i in range(len(self.corpo) - 1, -1, -1):
            seg = self.corpo[i]
            tela_x = seg.x - camera.x
            tela_y = seg.y - camera.y

            # Só desenha se estiver na tela
            if -30 < tela_x < LARGURA + 30 and -30 < tela_y < ALTURA + 30:
                raio = self.raio if i == 0 else self.raio - (i * 0.05)
                raio = max(raio, 4)
                # Cor mais escura no corpo
                cor = self.cor if i == 0 else VERDE_ESCURO
                pygame.draw.circle(tela, cor, (int(tela_x), int(tela_y)), int(raio))

    def colidir_com(self, outra):
        """Verifica se a cabeça bateu no corpo de outra cobra"""
        if not self.viva or not outra.viva:
            return False
        cabeca = self.corpo[0]
        for i, seg in enumerate(outra.corpo):
            if i < 5:  # ignora os primeiros (a cabeça dela)
                continue
            if cabeca.distance_to(seg) < self.raio + outra.raio * 0.7:
                return True
        return False


class Comida:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.raio = 6
        self.cor = (random.randint(180, 255), random.randint(100, 255), random.randint(100, 255))


# --- Inicialização ---
cobra = Cobra(0, 0)
camera = pygame.Vector2(-LARGURA / 2, -ALTURA / 2)  # centraliza em (0,0)

# Gera comidas num raio ao redor
comidas = []
for _ in range(300):
    x = random.randint(-1500, 1500)
    y = random.randint(-1500, 1500)
    comidas.append(Comida(x, y))

rodando = True
while rodando:
    clock.tick(FPS)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    mouse = pygame.mouse.get_pos()
    cobra.mover(mouse)

    # Câmera centraliza na cobra
    camera.x = cobra.pos.x - LARGURA / 2
    camera.y = cobra.pos.y - ALTURA / 2

    # Colisão com comida
    cabeca = cobra.corpo[0]
    for comida in comidas[:]:
        if cabeca.distance_to(comida.pos) < cobra.raio + comida.raio:
            comidas.remove(comida)
            cobra.pontos += 2
            # Gera nova comida
            comidas.append(Comida(
                random.randint(-1500, 1500),
                random.randint(-1500, 1500)
            ))

    # --- Desenhar ---
    tela.fill(PRETO)

    # Desenha grade de fundo (referência visual)
    passo = 60
    inicio_x = -(camera.x % passo)
    inicio_y = -(camera.y % passo)
    for x in range(int(inicio_x), LARGURA, passo):
        pygame.draw.line(tela, (25, 25, 40), (x, 0), (x, ALTURA))
    for y in range(int(inicio_y), ALTURA, passo):
        pygame.draw.line(tela, (25, 25, 40), (0, y), (LARGURA, y))

    # Comidas
    for comida in comidas:
        tx = comida.pos.x - camera.x
        ty = comida.pos.y - camera.y
        if -20 < tx < LARGURA + 20 and -20 < ty < ALTURA + 20:
            pygame.draw.circle(tela, comida.cor, (int(tx), int(ty)), comida.raio)

    # Cobra
    cobra.desenhar(tela, camera)

    # HUD
    texto = fonte.render(f"Pontos: {cobra.pontos}", True, BRANCO)
    tela.blit(texto, (15, 15))

    pygame.display.flip()

pygame.quit()