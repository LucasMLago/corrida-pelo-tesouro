import socket
import threading
import tkinter as tk
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from map.mapa import Mapa

class Cliente:
    """
    Classe que representa o cliente do jogo.
    """

    def __init__(self, host='localhost', port=8080):
        """
        Inicializa o cliente.
        """
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.mapa = None
        threading.Thread(target=self.receber_mensagens).start()

    def enviar_mensagem(self, msg):
        """
        Envia uma mensagem para o servidor.
        """
        self.sock.send(msg.encode('utf-8'))

    def sair_do_jogo(self):
        """
        Envia uma mensagem de saída para o servidor e fecha a conexão.
        """
        self.enviar_mensagem("SAIR_DO_JOGO")
        self.sock.close()

    def receber_mensagens(self):
        """
        Recebe mensagens do servidor.
        """
        while True:
            try:
                msg = self.sock.recv(1024).decode('utf-8')
                if msg:
                    print(f"Mensagem recebida: {msg}")
                    self.tratar_mensagem(msg)
            except:
                print("Conexão com o servidor perdida.")
                self.sock.close()
                break

    def tratar_mensagem(self, msg):
        """
        Trata as mensagens recebidas do servidor.
        """
        if msg.startswith("COLETAR_TESOURO"):
            _, x, y = msg.split()
            x, y = int(x), int(y)
            if self.mapa:
                self.mapa.coletar_tesouro(x, y, atualizar_servidor=False)

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
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    cliente = Cliente()
    janela = tk.Tk()
    mapa = Mapa(janela, cliente)
    cliente.mapa = mapa
    janela.protocol("WM_DELETE_WINDOW", cliente.sair_do_jogo)
    janela.mainloop()
