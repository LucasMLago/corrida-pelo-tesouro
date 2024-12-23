import socket
import threading
from threading import Semaphore, Lock
import time

# Configurações do servidor
HOST = 'localhost'
PORT = 8080

# Variáveis globais
MAP_SIZE = 10
mapa_principal = [[0] * MAP_SIZE for _ in range(MAP_SIZE)]  # Mapa 10x10
tesouros_mapa = [(2, 3), (5, 6), (7, 8)]  # Posições iniciais dos tesouros
jogadores = {}  # {player_id: (x, y)}
tesouros_coletados = {}  # {player_id: quantidade}
fila_sala = []  # Fila para acessar a sala do tesouro

# Semáforos
sem_celulas = [[Semaphore(1) for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
sem_sala = Semaphore(1)
lock = Lock()

# Função para verificar se o jogo terminou
def verificar_fim_do_jogo():
    with lock:
        if not tesouros_mapa:
            anunciar_vencedor()
            return True
    return False

# Anunciar o vencedor e encerrar o servidor
def anunciar_vencedor():
    vencedor = max(tesouros_coletados, key=tesouros_coletados.get)
    pontos = tesouros_coletados[vencedor]
    mensagem = f"O jogo terminou! Jogador {vencedor} venceu com {pontos} tesouros!\n"
    print(mensagem)
    for conn in conexoes.values():
        conn.sendall(mensagem.encode())
    time.sleep(2)
    for conn in conexoes.values():
        conn.close()
    exit(0)

# Função para gerenciar conexões de jogadores
def handle_player(conn, addr, player_id):
    global jogadores, tesouros_coletados
    jogadores[player_id] = (0, 0)  # Posição inicial
    tesouros_coletados[player_id] = 0
    conn.sendall(f"Bem-vindo, jogador {player_id}!\n".encode())

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            print(f"Jogador {player_id}: {data}")

            if data.startswith("mover"):
                _, x, y = data.split()
                mover_jogador(player_id, int(x), int(y), conn)
            elif data == "tesouro":
                coletar_tesouro(player_id, conn)
            elif data == "sala":
                acessar_sala(player_id, conn)

            if verificar_fim_do_jogo():
                break
        except Exception as e:
            print(f"Erro com jogador {player_id}: {e}")
            break

    print(f"Jogador {player_id} desconectado")
    with lock:
        if player_id in jogadores:
            del jogadores[player_id]
    conn.close()

# Função para mover jogadores
def mover_jogador(player_id, dx, dy, conn):
    x, y = jogadores[player_id]
    nx, ny = x + dx, y + dy
    if nx < 0 or nx >= MAP_SIZE or ny < 0 or ny >= MAP_SIZE:
        conn.sendall("Movimento inválido!\n".encode())
        return

    with sem_celulas[nx][ny]:  # Protege célula destino
        with lock:
            jogadores[player_id] = (nx, ny)
        conn.sendall(f"Você se moveu para {nx}, {ny}\n".encode())

# Função para coletar tesouro
def coletar_tesouro(player_id, conn):
    pos = jogadores[player_id]
    with sem_celulas[pos[0]][pos[1]]:  # Protege célula
        if pos in tesouros_mapa:
            with lock:
                tesouros_mapa.remove(pos)
                tesouros_coletados[player_id] += 1
            conn.sendall("Tesouro coletado!\n".encode())
        else:
            conn.sendall("Nenhum tesouro aqui!\n".encode())

# Função para acessar a sala do tesouro
def acessar_sala(player_id, conn):
    global fila_sala
    with sem_sala:  # Acesso exclusivo à sala
        conn.sendall("Você entrou na sala do tesouro!\n".encode())
        tempo_restante = 10
        while tempo_restante > 0:
            conn.sendall(f"Tempo restante: {tempo_restante} segundos\n".encode())
            time.sleep(1)
            tempo_restante -= 1
        conn.sendall("Tempo na sala acabou!\n".encode())

# Inicializar servidor
def start_server():
    global conexoes
    conexoes = {}
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Servidor iniciado em {HOST}:{PORT}")

    player_id = 0
    while True:
        conn, addr = server.accept()
        conexoes[player_id] = conn
        threading.Thread(target=handle_player, args=(conn, addr, player_id)).start()
        player_id += 1

if __name__ == "__main__":
    start_server()
