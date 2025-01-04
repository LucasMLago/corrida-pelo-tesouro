import socket
import threading
import time

class Cliente:
    """
    Classe Cliente para conectar ao servidor do jogo Corrida Pelo Tesouro.
    
    Atributos:
        host (str): Endereço do servidor.
        port (int): Porta do servidor.
        socket (socket.socket): Socket para comunicação com o servidor.
        in_treasure_room (bool): Indica se o jogador está na sala do tesouro.
    """
    def __init__(self, host="localhost", port=8080):
        """
        Inicializa a classe Cliente com o endereço e porta do servidor.
        
        Args:
            host (str): Endereço do servidor. Padrão é "localhost".
            port (int): Porta do servidor. Padrão é 8080.
        """
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.in_treasure_room = False

    def conectar(self):
        """
        Conecta ao servidor e inicia as threads para receber mensagens e enviar comandos.
        """
        try:
            self.socket.connect((self.host, self.port))
            time.sleep(0.1)
            threading.Thread(target=self.receber_mensagens).start()
            self.enviar_comandos()
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")

    def receber_mensagens(self):
        """
        Recebe mensagens do servidor e as exibe no console.
        """
        while True:
            try:
                mensagem = self.socket.recv(1024).decode()
                print(mensagem)
                if "Saindo do jogo..." in mensagem:
                    self.socket.close()  # Fecha o socket do cliente
                    break
                elif "Você saiu da sala do tesouro." in mensagem:
                    self.in_treasure_room = False
            except:
                print("Conexão com o servidor foi perdida.")
                break

    def enviar_comandos(self):
        """
        Envia comandos do jogador para o servidor.
        """
        while True:
            time.sleep(0.1)
            if self.in_treasure_room:
                comando = input("Digite um comando (w, a, s, d, sair): ")
            else:
                comando = input("Digite um comando (w, a, s, d, entrar, sair): ")
            self.socket.send(comando.encode())
            if comando == "sair" and not self.in_treasure_room:
                break
            elif comando == "entrar":
                self.in_treasure_room = True

if __name__ == "__main__":
    cliente = Cliente()
    cliente.conectar()
