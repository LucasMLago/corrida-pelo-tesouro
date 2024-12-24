import socket
import threading
import logging
from datetime import datetime
from mapa import Mapa  # Importe a classe Mapa

class Servidor:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.clientes = []
        self.lock = threading.Lock()
        self.mapa = Mapa(None, servidor=self)  # Crie uma instância do Mapa sem janela
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def iniciar(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        logging.info(f"Servidor iniciado em {self.host}:{self.port}")

        try:
            while True:
                cliente, client_address = self.sock.accept()
                logging.info(f"Conexão estabelecida com {client_address}")
                with self.lock:
                    self.clientes.append(cliente)
                threading.Thread(target=self.tratar_cliente, args=(cliente,)).start()
        except KeyboardInterrupt:
            logging.info("Servidor interrompido pelo usuário.")
        finally:
            self.sock.close()

    def tratar_cliente(self, cliente):
        client_address = cliente.getpeername()
        self.enviar_estado_inicial(cliente)
        try:
            while True: 
                try:
                    msg = cliente.recv(1024).decode('utf-8')
                    if not msg:
                        break
                    self.log_acao(msg, client_address)
                    self.tratar_mensagem(msg, cliente, client_address)
                except socket.error as e:
                    pass
        finally:
            self.remover_cliente(cliente, client_address)

    def tratar_mensagem(self, msg, cliente, client_address):
        if msg.startswith("COLETAR_TESOURO"):
            _, x, y = msg.split()
            x, y = int(x), int(y)
            with self.mapa.semaforos_celulas[x][y]:  # Protege a célula específica
                if self.mapa.mapa_estado[x][y]:  # Verifica se o tesouro ainda está disponível
                    self.mapa.mapa_estado[x][y] = False
                    self.broadcast(msg, cliente)
                    logging.info(f"O Jogador {client_address} coletou um tesouro: {msg}")
        elif msg == "SAIR_DO_JOGO":
            self.remover_cliente(cliente, client_address)
            logging.info(f"O Jogador {client_address} saiu do jogo.")

    def remover_cliente(self, cliente, client_address=None):
        if cliente in self.clientes:
            self.clientes.remove(cliente)
        cliente.close()

    def broadcast(self, msg, cliente_atual):
        for cliente in self.clientes:
            if cliente != cliente_atual:
                try:
                    cliente.send(msg.encode('utf-8'))
                except socket.error as e:
                    logging.error(f"Erro ao enviar mensagem para {cliente.getpeername()}: {e}")
                    self.remover_cliente(cliente)

    def log_acao(self, msg, client_address):
        logging.info(f"O jogador {client_address}: {msg}")

    def enviar_estado_inicial(self, cliente):
        with self.lock:  # Protege o acesso ao estado do mapa
            for i in range(8):
                for j in range(8):
                    if self.mapa.mapa_estado[i][j]:
                        cliente.send(f"COLETAR_TESOURO {i} {j}".encode('utf-8'))

if __name__ == "__main__":
    servidor = Servidor()
    servidor.iniciar()
