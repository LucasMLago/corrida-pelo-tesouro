import tkinter as tk
import threading
import time
import random

# Configurações do mapa
LINHAS = 8
COLUNAS = 8
TESOUROS_SALA = 16  # Tesouros nas salas do tesouro
TESOUROS_MAPA = 8  # Número de tesouros no mapa principal

# Flag global para controlar as threads
encerrar_threads = False

class Mapa:
    # Adicione um parâmetro opcional servidor
    def __init__(self, janela, cliente=None, servidor=None):
        self.cliente = cliente
        self.servidor = servidor  # Armazene a referência ao servidor
        self.janela = janela
        if not hasattr(self, 'mapa_estado'):
            self.mapa_estado = [[False for _ in range(COLUNAS)] for _ in range(LINHAS)]
        self.tesouros_restantes = TESOUROS_MAPA
        self.mutex_global = threading.Lock()  # Protege o mapa inteiro
        self.semaforos_celulas = [[threading.Semaphore(1) for _ in range(COLUNAS)] for _ in range(LINHAS)]  # Semáforos para cada célula
        self.salas_tesouro = {}
        self.sala_semaforos = {}  # Semáforos para salas
        self.sala_estados = {}  # Armazena o estado dos tesouros em cada sala
        self.buttons = []
        self.tesouros_mapa = set(random.sample([(i, j) for i in range(LINHAS) for j in range(COLUNAS)], TESOUROS_MAPA))
        self.timer = None
        
        if self.janela:
            self.janela.title("Corrida Pelo Tesouro - Mapa")
            self.centralizar_janela(self.janela, 525, 608)
            for i in range(LINHAS):
                row = []
                for j in range(COLUNAS):
                    if (i, j) in self.tesouros_mapa:  # Coordenadas de tesouros no mapa principal
                        botao = tk.Button(janela, width=8, height=4, bg="gold", 
                                          command=lambda x=i, y=j: self.coletar_tesouro(x, y))
                    else:
                        botao = tk.Button(janela, width=8, height=4, bg="white", 
                                          command=lambda x=i, y=j: self.opcao_sala_do_tesouro(x, y))
                        self.salas_tesouro[(i, j)] = TESOUROS_SALA
                        self.sala_semaforos[(i, j)] = threading.Semaphore(1)
                        self.sala_estados[(i, j)] = [True] * TESOUROS_SALA
                    botao.grid(row=i, column=j)
                    row.append(botao)
                self.buttons.append(row)

            tk.Button(janela, text="Sair do Jogo", command=self.sair_do_jogo, bg="red", fg="white", width=74, height=2).grid(row=LINHAS, column=0, columnspan=COLUNAS)

    def sair_do_jogo(self):
        """Encerra todas as threads e fecha o programa com segurança"""
        global encerrar_threads
        encerrar_threads = True
        print("Encerrando o jogo...")
        if self.cliente:
            self.cliente.sair_do_jogo()
        self.janela.destroy()

    def coletar_tesouro(self, x, y, atualizar_servidor=True):
        """Coleta um tesouro do mapa principal"""
        if self.janela and self.buttons[x][y]["bg"] == "gold":
            with self.semaforos_celulas[x][y]:  # Protege a célula específica
                if self.buttons[x][y]["bg"] == "gold":  # Verifica novamente dentro da região crítica
                    self.buttons[x][y]["state"] = "disabled"
                    self.buttons[x][y]["bg"] = "gray"
                    self.tesouros_restantes -= 1
                    if self.cliente and atualizar_servidor:
                        self.cliente.enviar_mensagem(f"COLETAR_TESOURO {x} {y}")
                    if self.servidor:
                        self.servidor.mapa_estado[x][y] = False
                    print(f"Tesouros restantes no mapa principal: {self.tesouros_restantes}")

                    if self.tesouros_restantes == 0:
                        print("Todos os tesouros do mapa principal foram coletados!")

    def opcao_sala_do_tesouro(self, x, y):
        """Abre a opção para acessar uma sala do tesouro"""
        def entrar_na_sala():
            self.acessar_sala_do_tesouro(x, y)

        popup = tk.Toplevel(self.janela)
        popup.title("Gostaria de Entrar?")
        self.centralizar_janela(popup, 200, 150)

        tk.Label(popup, text="Deseja entrar na sala do tesouro?").pack(pady=10)
        tk.Button(popup, text="Sim", bg="green", fg="white", command=lambda: [popup.destroy(), entrar_na_sala()], width=15, height=2).pack(pady=5)
        tk.Button(popup, text="Não", bg="red", fg="white", command=popup.destroy, width=15, height=2).pack(pady=5)

    def acessar_sala_do_tesouro(self, x, y):
        """Controla o acesso à sala do tesouro específica"""
        if self.sala_semaforos[(x, y)].acquire(blocking=False):
            print(f"Jogador entrou na sala do tesouro em ({x}, {y})!")
            self.abrir_sala_do_tesouro(x, y)
        else:
            print("A sala do tesouro está ocupada. Aguarde sua vez.")

    def abrir_sala_do_tesouro(self, x, y):
        """Abre a janela da sala do tesouro com um timer de 10 segundos"""
        sala = tk.Toplevel(self.janela)
        sala.title(f"Sala do Tesouro ({x}, {y})")
        self.centralizar_janela(sala, 205, 265)

        # Captura todos os eventos de entrada para a janela da sala do tesouro
        sala.grab_set()

        tesouros_restantes = self.sala_estados[(x, y)]

        def coletar_tesouro(idx):
            if tesouros_restantes[idx]:
                tesouros_restantes[idx] = False
                botoes[idx]["state"] = "disabled"
                botoes[idx]["bg"] = "gray"
                self.salas_tesouro[(x, y)] -= 1
                print(f"Tesouros restantes na sala ({x}, {y}): {self.salas_tesouro[(x, y)]}")
                if self.salas_tesouro[(x, y)] == 0:
                    print(f"Todos os tesouros da sala ({x}, {y}) foram coletados!")

        botoes = []
        for i in range(4):
            for j in range(4):
                idx = i * 4 + j
                if idx < len(tesouros_restantes) and tesouros_restantes[idx]:
                    botao = tk.Button(sala, width=6, height=3, bg="gold", 
                                      command=lambda idx=idx: coletar_tesouro(idx))
                else:
                    botao = tk.Button(sala, width=6, height=3, bg="gray", state="disabled")
                botao.grid(row=i, column=j)
                botoes.append(botao)

        def fechar_sala():
            if not sala.winfo_exists():
                return
            print(f"Tempo esgotado na sala ({x}, {y})!")
            sala.destroy()
            self.sala_semaforos[(x, y)].release()
            print(f"Jogador saiu da sala do tesouro em ({x}, {y})!")

        def sair_voluntariamente():
            print(f"Jogador saiu voluntariamente da sala ({x}, {y})!")
            sala.destroy()
            self.sala_semaforos[(x, y)].release()
            if hasattr(self, 'timer') and self.timer.is_alive():
                self.timer.cancel()

        # Botão para sair voluntariamente
        tk.Button(sala, text="Sair da Sala", command=sair_voluntariamente, bg="red", fg="white", width=28, height=2).grid(row=4, column=0, columnspan=4)

        # Inicia o timer de 10 segundos
        self.timer = threading.Timer(10, fechar_sala)
        self.timer.start()

    @staticmethod
    def centralizar_janela(janela, largura, altura):
        """Centraliza a janela na tela"""
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        x = (largura_tela - largura) // 2
        y = (altura_tela - altura) // 2
        janela.geometry(f"{largura}x{altura}+{x}+{y}")


if __name__ == "__main__":
    janela = tk.Tk()
    cliente = None  # Substitua pelo cliente real
    mapa = Mapa(janela, cliente)
    janela.mainloop()
