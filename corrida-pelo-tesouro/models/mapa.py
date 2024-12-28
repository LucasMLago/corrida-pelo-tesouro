import tkinter as tk
import threading
import random

# Configurações do mapa
LINHAS = 8
COLUNAS = 8
TESOUROS_SALA = 16
TESOUROS_MAPA = 8

# Flag global para controlar as threads
encerrar_threads = False

class Mapa:
    """
    Classe que representa o mapa do jogo.
    """

    def __init__(self):
        """
        Inicializa o mapa.
        """
        self.mapa_estado = [[False for _ in range(COLUNAS)] for _ in range(LINHAS)]
        self.tesouros_restantes = TESOUROS_MAPA
        self.mutex_global = threading.Lock()
        self.semaforos_celulas = [[threading.Semaphore(1) for _ in range(COLUNAS)] for _ in range(LINHAS)]
        self.salas_tesouro = {}
        self.sala_semaforos = {}
        self.sala_estados = {}
        self.tesouros_mapa = set(random.sample([(i, j) for i in range(LINHAS) for j in range(COLUNAS)], TESOUROS_MAPA))
        for i in range(LINHAS):
            for j in range(COLUNAS):
                if (i, j) not in self.tesouros_mapa:
                    self.salas_tesouro[(i, j)] = TESOUROS_SALA
                    self.sala_semaforos[(i, j)] = threading.Semaphore(1)
                    self.sala_estados[(i, j)] = [True] * TESOUROS_SALA

    def coletar_tesouro(self, x, y):
        """
        Coleta um tesouro do mapa principal.
        """
        with self.semaforos_celulas[x][y]:
            if self.mapa_estado[x][y]:
                self.mapa_estado[x][y] = False
                self.tesouros_restantes -= 1
                print(f"Tesouros restantes no mapa principal: {self.tesouros_restantes}")
                if self.tesouros_restantes == 0:
                    print("Todos os tesouros do mapa principal foram coletados")

    def acessar_sala_do_tesouro(self, x, y):
        """
        Controla o acesso à sala do tesouro específica.
        """
        if self.sala_semaforos[(x, y)].acquire(blocking=False):
            print(f"Jogador entrou na sala do tesouro em ({x}, {y})")
            return True
        else:
            print("A sala do tesouro está ocupada. Aguarde sua vez.")
            return False

    def coletar_tesouro_sala(self, x, y, idx):
        """
        Coleta um tesouro de uma sala do tesouro específica.
        """
        if self.sala_estados[(x, y)][idx]:
            self.sala_estados[(x, y)][idx] = False
            self.salas_tesouro[(x, y)] -= 1
            print(f"Tesouros restantes na sala ({x}, {y}): {self.salas_tesouro[(x, y)]}")
            if self.salas_tesouro[(x, y)] == 0:
                print(f"Todos os tesouros da sala ({x}, {y}) foram coletados")
            return True
        return False

    def liberar_sala(self, x, y):
        """
        Libera a sala do tesouro.
        """
        self.sala_semaforos[(x, y)].release()
        print(f"Jogador saiu da sala do tesouro em ({x}, {y})")