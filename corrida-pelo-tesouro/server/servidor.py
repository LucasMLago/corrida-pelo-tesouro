import socket
import threading
import logging
import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.mapa import Mapa

class Servidor:
    """
    Classe que representa o servidor do jogo.
    """

    def __init__(self, host='localhost', port=8080):
        """
        Inicializa o servidor.
        """
        self.host = host
        self.port = port
        self.clientes = []
        self.lock = threading.Lock()
        self.map_seed = random.randint(1, 1000000)
        self.mapa = Mapa(seed=self.map_seed)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def iniciar(self):
        """
        Inicia o servidor e aguarda conexões de clientes.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        logging.info(f"Servidor iniciado em {self.host}:{self.port}")

        try:
            while True:
                client_socket, client_address = self.sock.accept()
                logging.info(f"Conexão estabelecida com {client_address}")
                with self.lock:
                    self.clientes.append(client_socket)
                threading.Thread(target=self.tratar_cliente, args=(client_socket,)).start()
        except KeyboardInterrupt:
            logging.info("Servidor interrompido pelo usuário.")
        finally:
            self.sock.close()

    def tratar_cliente(self, cliente):
        """
        Trata a comunicação com um cliente específico.
        """
        client_address = cliente.getpeername()[1]
        self.enviar_estado_inicial(cliente)
        try:
            while True:
                try:
                    msg = cliente.recv(1024).decode('utf-8')
                    if not msg:
                        break
                    self.log_acao(msg, client_address)
                    self.tratar_mensagem(msg, cliente, client_address)
                except socket.error:
                    pass
        finally:
            self.remover_cliente(cliente, client_address)

    def tratar_mensagem(self, msg, cliente, client_address):
        """
        Trata as mensagens recebidas dos clientes.
        """
        if msg.startswith("LOG"):
            self.tratar_log_cliente(msg, client_address)
        elif msg.startswith("COLETAR_TESOURO"):
            _, x, y = msg.split()
            x, y = int(x), int(y)
            self.mapa.coletar_tesouro(x, y)
            self.broadcast(msg, cliente)
            logging.info(f"Tesouro coletado por {client_address}: ({x}, {y})")
        elif msg.startswith("ACESSAR_SALA"):
            _, x, y = msg.split()
            x, y = int(x), int(y)
            if self.mapa.acessar_sala_do_tesouro(x, y):
                cliente.send(f"ENTRAR_SALA {x} {y}".encode('utf-8'))
        elif msg.startswith("COLETAR_TESOURO_SALA"):
            _, x, y, idx = msg.split()
            x, y, idx = int(x), int(y), int(idx)
            if self.mapa.coletar_tesouro_sala(x, y, idx):
                self.broadcast(msg, cliente)
        elif msg.startswith("SAIR_SALA"):
            _, x, y = msg.split()
            x, y = int(x), int(y)
            self.mapa.liberar_sala(x, y)
        elif msg == "SAIR_DO_JOGO":
            self.remover_cliente(cliente, client_address)
            logging.info(f"Jogador {client_address} saiu do jogo.")

    def tratar_log_cliente(self, msg, client_address):
        """
        Trata as mensagens de log recebidas dos clientes.
        """
        _, log_msg = msg.split(" ", 1)

    def remover_cliente(self, cliente, client_address=None):
        """
        Remove um cliente da lista de clientes conectados.
        """
        if cliente in self.clientes:
            self.clientes.remove(cliente)
        cliente.close()

    def broadcast(self, msg, cliente_atual):
        """
        Envia uma mensagem para todos os clientes conectados, exceto o remetente.
        """
        for cliente in self.clientes:
            if cliente != cliente_atual:
                try:
                    cliente.send(msg.encode('utf-8'))
                except socket.error as e:
                    logging.error(f"Erro ao enviar mensagem para {cliente.getpeername()}: {e}")
                    self.remover_cliente(cliente)

    def log_acao(self, msg, client_address):
        """
        Registra uma ação realizada por um cliente.
        """
        if "SAIR_DO_JOGO" not in msg:
            logging.info(f"Cliente {client_address}: {msg}")

    def enviar_estado_inicial(self, cliente):
        """
        Envia o estado inicial do mapa para um cliente recém-conectado.
        """
        with self.lock:
            cliente.send(f"SEED {self.map_seed}".encode('utf-8'))
            for i in range(8):
                for j in range(8):
                    if self.mapa.mapa_estado[i][j]:
                        cliente.send(f"COLETAR_TESOURO {i} {j}".encode('utf-8'))

if __name__ == "__main__":
    servidor = Servidor()
    servidor.iniciar()
