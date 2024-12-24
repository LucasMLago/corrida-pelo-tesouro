import socket
import threading
import logging
from datetime import datetime

class Servidor:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.clientes = []
        self.lock = threading.Lock()
        self.mapa_estado = [[False] * 8 for _ in range(8)]  # Estado inicial do mapa
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
                    self.tratar_mensagem(msg, cliente)
                except socket.error as e:
                    logging.error(f"Erro de socket ao receber mensagem: {e}")
                    break
        finally:
            if cliente in self.clientes:
                self.clientes.remove(cliente)
            cliente.close()

    def tratar_mensagem(self, msg, cliente):
        """
        Lida com mensagens recebidas dos clientes.

        Formatos de mensagem esperados:
        - "COLETAR_TESOURO": Indica uma solicitação para coletar um tesouro
        - "SAIR_DO_JOGO": Indica uma solicitação para sair do jogo

        Args:
            msg (str): A mensagem recebida do cliente.
            cliente (socket.socket): O socket do cliente que enviou a mensagem.
        """
        if msg.startswith("COLETAR_TESOURO"):
            _, x, y = msg.split()
            x, y = int(x), int(y)
            with self.lock:
                self.mapa_estado[x][y] = True
            self.broadcast(msg, cliente)
        elif msg.startswith("SAIR_DO_JOGO"):
            self.remover_cliente(cliente)
        # aqui podemos fazer outros tratamentos de mensagens caso necessário

    def remover_cliente(self, cliente):
        if cliente in self.clientes:
            self.clientes.remove(cliente)
        cliente.close()

    def broadcast(self, msg, cliente_atual):
        for cliente in self.clientes:
            if cliente != cliente_atual:
                try:
                    cliente.send(msg.encode('utf-8'))
                except socket.error as e:
                    print(f"Erro ao enviar mensagem para {cliente.getpeername()}: {e}")
                    self.remover_cliente(cliente)

    def log_acao(self, msg, client_address):
        print(f"O jogador {client_address}: {msg}")

    def enviar_estado_inicial(self, cliente):
        for i in range(8):
            for j in range(8):
                if self.mapa_estado[i][j]:
                    cliente.send(f"COLETAR_TESOURO {i} {j}".encode('utf-8'))

if __name__ == "__main__":
    servidor = Servidor()
    servidor.iniciar()
