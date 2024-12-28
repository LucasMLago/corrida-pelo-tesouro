import tkinter as tk
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.mapa import Mapa, LINHAS, COLUNAS, encerrar_threads

class Jogo:
    """
    Classe que representa o jogo.
    """

    def __init__(self, janela, cliente=None, servidor=None):
        """
        Inicializa o jogo.
        """
        self.cliente = cliente
        self.servidor = servidor
        self.mapa = servidor.mapa if servidor else Mapa()
        self.janela = janela
        self.buttons = []
        self.timer = None

        if self.janela:
            self.janela.title("Corrida Pelo Tesouro - Mapa")
            self.centralizar_janela(self.janela, 525, 608)
            for i in range(LINHAS):
                row = []
                for j in range(COLUNAS):
                    if (i, j) in self.mapa.tesouros_mapa:
                        botao = tk.Button(janela, width=8, height=4, bg="gold", 
                                          command=lambda x=i, y=j: self.coletar_tesouro(x, y))
                    else:
                        botao = tk.Button(janela, width=8, height=4, bg="white", 
                                          command=lambda x=i, y=j: self.opcao_sala_do_tesouro(x, y))
                    botao.grid(row=i, column=j)
                    row.append(botao)
                self.buttons.append(row)

            tk.Button(janela, text="Sair do Jogo", command=self.sair_do_jogo, bg="red", fg="white", width=74, height=2).grid(row=LINHAS, column=0, columnspan=COLUNAS)

    def sair_do_jogo(self):
        """
        Encerra todas as threads e fecha o programa com segurança.
        """
        global encerrar_threads
        encerrar_threads = True
        print("Encerrando o jogo...")
        if self.cliente:
            self.cliente.sair_do_jogo()
        self.janela.destroy()

    def coletar_tesouro(self, x, y, atualizar_servidor=True):
        """
        Coleta um tesouro do mapa principal.
        """
        if self.janela and self.buttons[x][y]["bg"] == "gold":
            with self.mapa.semaforos_celulas[x][y]:
                if self.buttons[x][y]["bg"] == "gold":
                    self.buttons[x][y]["state"] = "disabled"
                    self.buttons[x][y]["bg"] = "gray"
                    self.mapa.tesouros_restantes -= 1
                    if self.cliente and atualizar_servidor:
                        self.cliente.enviar_mensagem(f"COLETAR_TESOURO {x} {y}")
                    if self.servidor:
                        self.servidor.mapa.mapa_estado[x][y] = False
                    print(f"Tesouros restantes no mapa principal: {self.mapa.tesouros_restantes}")

                    if self.mapa.tesouros_restantes == 0:
                        print("Todos os tesouros do mapa principal foram coletados!")

    def opcao_sala_do_tesouro(self, x, y):
        """
        Abre a opção para acessar uma sala do tesouro.
        """
        def entrar_na_sala():
            self.acessar_sala_do_tesouro(x, y)

        popup = tk.Toplevel(self.janela)
        popup.title("Gostaria de Entrar?")
        self.centralizar_janela(popup, 200, 150)

        tk.Label(popup, text="Deseja entrar na sala do tesouro?").pack(pady=10)
        tk.Button(popup, text="Sim", bg="green", fg="white", command=lambda: [popup.destroy(), entrar_na_sala()], width=15, height=2).pack(pady=5)
        tk.Button(popup, text="Não", bg="red", fg="white", command=popup.destroy, width=15, height=2).pack(pady=5)

    def acessar_sala_do_tesouro(self, x, y):
        """
        Controla o acesso à sala do tesouro específica.
        """
        if self.mapa.acessar_sala_do_tesouro(x, y):
            self.abrir_sala_do_tesouro(x, y)

    def abrir_sala_do_tesouro(self, x, y):
        """
        Abre a janela da sala do tesouro com um timer de 10 segundos.
        """
        sala = tk.Toplevel(self.janela)
        sala.title(f"Sala do Tesouro ({x}, {y})")
        self.centralizar_janela(sala, 205, 265)

        sala.grab_set()

        tesouros_restantes = self.mapa.sala_estados[(x, y)]

        def coletar_tesouro(idx):
            if self.mapa.coletar_tesouro_sala(x, y, idx):
                botoes[idx]["state"] = "disabled"
                botoes[idx]["bg"] = "gray"

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
            self.mapa.liberar_sala(x, y)

        def sair_voluntariamente():
            print(f"Jogador saiu voluntariamente da sala ({x}, {y})!")
            sala.destroy()
            self.mapa.liberar_sala(x, y)
            if hasattr(self, 'timer') and self.timer.is_alive():
                self.timer.cancel()

        tk.Button(sala, text="Sair da Sala", command=sair_voluntariamente, bg="red", fg="white", width=28, height=2).grid(row=4, column=0, columnspan=4)

        self.timer = threading.Timer(10, fechar_sala)
        self.timer.start()

    @staticmethod
    def centralizar_janela(janela, largura, altura):
        """
        Centraliza a janela na tela.
        """
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        x = (largura_tela - largura) // 2
        y = (altura_tela - altura) // 2
        janela.geometry(f"{largura}x{altura}+{x}+{y}")

if __name__ == "__main__":
    janela = tk.Tk()
    cliente = None
    servidor = None
    jogo = Jogo(janela, cliente, servidor)
    janela.mainloop()

