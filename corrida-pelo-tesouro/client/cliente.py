import socket
import threading
import tkinter as tk
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.jogo import Jogo

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
        
        # Aguarda receber a seed antes de criar o jogo
        msg = self.sock.recv(1024).decode('utf-8')
        if msg.startswith("SEED"):
            _, seed = msg.split()
            self.map_seed = int(seed)
        else:
            self.map_seed = None
            
        self.janela = tk.Tk()
        self.jogo = Jogo(self.janela, cliente=self, seed=self.map_seed)
        threading.Thread(target=self.ouvir_servidor).start()

    def ouvir_servidor(self):
        """
        Ouve mensagens do servidor.
        """
        while True:
            try:
                msg = self.sock.recv(1024).decode('utf-8')
                if not msg:
                    break
                self.tratar_mensagem(msg)
            except socket.error:
                break

    def tratar_mensagem(self, msg):
        """
        Trata as mensagens recebidas do servidor.
        """
        if msg.startswith("COLETAR_TESOURO"):
            _, x, y = msg.split()
            x, y = int(x), int(y)
            self.jogo.coletar_tesouro(x, y, atualizar_servidor=False)
        elif msg.startswith("ENTRAR_SALA"):
            _, x, y = msg.split()
            x, y = int(x), int(y)
            self.jogo.acessar_sala_do_tesouro(x, y)
        elif msg.startswith("COLETAR_TESOURO_SALA"):
            _, x, y, idx = msg.split()
            x, y, idx = int(x), int(y), int(idx)
            self.jogo.coletar_tesouro_sala(x, y, idx)

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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    cliente = Cliente()
    cliente.janela.mainloop()
