import socket
import threading
import tkinter as tk

# Configurações do cliente
SERVER_HOST = 'localhost'
SERVER_PORT = 8080

# Inicializa o socket do cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

# Variáveis do mapa
MAP_SIZE = 10
mapa = [[0] * MAP_SIZE for _ in range(MAP_SIZE)]  # Estado do mapa (atualizado pelo servidor)
player_id = None  # ID do jogador

# Função para enviar comandos ao servidor
def enviar_comando(comando):
    client_socket.sendall(comando.encode())

# Função para receber atualizações do servidor
def receber_atualizacoes():
    global player_id
    while True:
        try:
            mensagem = client_socket.recv(1024).decode()
            if mensagem.startswith("Bem-vindo"):
                player_id = int(mensagem.split(", jogador ")[1].strip())
                print(f"Conectado como jogador {player_id}")
            elif mensagem.startswith("MAPA:"):
                atualizar_mapa(mensagem[5:])  # Remove o prefixo "MAPA:"
            else:
                print(mensagem)
        except Exception as e:
            print(f"Erro ao receber dados: {e}")
            break

# Atualiza o mapa com base na mensagem do servidor
def atualizar_mapa(estado_mapa):
    global mapa
    linhas = estado_mapa.strip().split("\n")
    for i in range(MAP_SIZE):
        mapa[i] = list(map(int, linhas[i].split()))
    atualizar_visualizacao()

# Atualiza a interface gráfica do mapa
def atualizar_visualizacao():
    for i in range(MAP_SIZE):
        for j in range(MAP_SIZE):
            if mapa[i][j] == 0:
                grid[i][j].config(bg="white")  # Célula vazia
            elif mapa[i][j] == 1:
                grid[i][j].config(bg="gold")  # Tesouro
            elif mapa[i][j] == 2:
                grid[i][j].config(bg="blue")  # Jogador

# Função para movimentar o jogador
def mover_jogador(direcao):
    if direcao == "cima":
        enviar_comando("mover -1 0")
    elif direcao == "baixo":
        enviar_comando("mover 1 0")
    elif direcao == "esquerda":
        enviar_comando("mover 0 -1")
    elif direcao == "direita":
        enviar_comando("mover 0 1")

# Função para coletar tesouro
def coletar_tesouro():
    enviar_comando("tesouro")

# Função para acessar a sala do tesouro
def acessar_sala():
    enviar_comando("sala")

# Função para receber atualizações do servidor
def receber_atualizacoes():
    global player_id
    while True:
        try:
            mensagem = client_socket.recv(1024).decode()
            if "O jogo terminou!" in mensagem:
                print(mensagem)
                exibir_mensagem_final(mensagem)
                break
            elif mensagem.startswith("Bem-vindo"):
                player_id = int(mensagem.split(", jogador ")[1].strip())
                print(f"Conectado como jogador {player_id}")
            elif mensagem.startswith("MAPA:"):
                atualizar_mapa(mensagem[5:])
            else:
                print(mensagem)
        except Exception as e:
            print(f"Erro ao receber dados: {e}")
            break

# Exibir mensagem final na interface
def exibir_mensagem_final(mensagem):
    final_window = tk.Toplevel(janela)
    final_window.title("Fim do Jogo")
    tk.Label(final_window, text=mensagem, font=("Arial", 16)).pack(pady=20)
    tk.Button(final_window, text="Sair", command=janela.quit).pack(pady=10)


# Inicializa a interface gráfica
janela = tk.Tk()
janela.title("Cliente - Corrida pelo Tesouro")

# Cria a grade do mapa
grid = []
for i in range(MAP_SIZE):
    linha = []
    for j in range(MAP_SIZE):
        btn = tk.Label(janela, width=4, height=2, bg="white", relief="solid")
        btn.grid(row=i, column=j, padx=1, pady=1)
        linha.append(btn)
    grid.append(linha)

# Botões de controle
frame_controles = tk.Frame(janela)
frame_controles.grid(row=MAP_SIZE, column=0, columnspan=MAP_SIZE)

btn_cima = tk.Button(frame_controles, text="Cima", command=lambda: mover_jogador("cima"))
btn_cima.grid(row=0, column=1)

btn_esquerda = tk.Button(frame_controles, text="Esquerda", command=lambda: mover_jogador("esquerda"))
btn_esquerda.grid(row=1, column=0)

btn_baixo = tk.Button(frame_controles, text="Baixo", command=lambda: mover_jogador("baixo"))
btn_baixo.grid(row=1, column=1)

btn_direita = tk.Button(frame_controles, text="Direita", command=lambda: mover_jogador("direita"))
btn_direita.grid(row=1, column=2)

btn_tesouro = tk.Button(frame_controles, text="Coletar Tesouro", command=coletar_tesouro)
btn_tesouro.grid(row=2, column=0, columnspan=3)

btn_sala = tk.Button(frame_controles, text="Acessar Sala", command=acessar_sala)
btn_sala.grid(row=3, column=0, columnspan=3)

# Thread para receber atualizações do servidor
thread_receber = threading.Thread(target=receber_atualizacoes, daemon=True)
thread_receber.start()

# Inicia a interface gráfica
janela.mainloop()
