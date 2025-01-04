import socket
import threading
import time
import random
from threading import Semaphore
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.mapa import Mapa
from models.colors import colors

class Servidor:
    """
    Classe Servidor para gerenciar o jogo Corrida Pelo Tesouro.
    
    Atributos:
        host (str): Endereço do servidor.
        port (int): Porta do servidor.
        linhas_mapa_principal (int): Número de linhas do mapa principal.
        colunas_mapa_principal (int): Número de colunas do mapa principal.
        max_tesouros_mapa (int): Número máximo de tesouros no mapa principal.
        linhas_sala_tesouro (int): Número de linhas da sala do tesouro.
        colunas_sala_tesouro (int): Número de colunas da sala do tesouro.
        max_tesouros_sala (int): Número máximo de tesouros na sala do tesouro.
        mapa_principal (Mapa): Instância do mapa principal.
        jogadores (dict): Dicionário de jogadores conectados.
        lock_mapa (Semaphore): Semáforo para controle de acesso ao mapa principal.
        sala_tesouro (Mapa): Instância da sala do tesouro.
        sala_tesouro_lock (Semaphore): Semáforo para controle de acesso à sala do tesouro.
        server_socket (socket.socket): Socket do servidor.
        cores_jogadores (list): Lista de cores para os jogadores.
        salas_tesouro (dict): Dicionário para armazenar o estado de cada sala do tesouro.
        salas_tesouro_locks (dict): Dicionário para armazenar os semáforos de cada sala do tesouro.
        estado_salas_tesouro (dict): Dicionário para armazenar o estado de coleta de cada sala do tesouro.
    """
    def __init__(self, host="localhost", port=8080, tamanho_mapa=(8, 8), max_tesouros_mapa=10, tamanho_sala_tesouro=(4, 4), max_tesouros_sala=16):
        """
        Inicializa a classe Servidor com os parâmetros do jogo.
        
        Args:
            host (str): Endereço do servidor. Padrão é "localhost".
            port (int): Porta do servidor. Padrão é 8080.
            tamanho_mapa (tuple): Tamanho do mapa principal (linhas, colunas). Padrão é (8, 8).
            max_tesouros_mapa (int): Número máximo de tesouros no mapa principal. Padrão é 10.
            tamanho_sala_tesouro (tuple): Tamanho da sala do tesouro (linhas, colunas). Padrão é (4, 4).
            max_tesouros_sala (int): Número máximo de tesouros na sala do tesouro. Padrão é 16.
        """
        self.host = host
        self.port = port
        self.linhas_mapa_principal, self.colunas_mapa_principal = tamanho_mapa
        self.max_tesouros_mapa = max_tesouros_mapa
        self.linhas_sala_tesouro, self.colunas_sala_tesouro = tamanho_sala_tesouro
        self.max_tesouros_sala = max_tesouros_sala
        self.mapa_principal = Mapa(self.linhas_mapa_principal, self.colunas_mapa_principal)  # Mapa principal
        self.mapa_principal.inicializar_tesouros(quantidade=max_tesouros_mapa)  # Inicializa o mapa principal com tesouros
        self.jogadores = {}
        self.lock_mapa = Semaphore()  # Semáforo para acesso ao mapa principal
        self.sala_tesouro = None  # Sala do tesouro
        self.sala_tesouro_lock = Semaphore(1)  # Controle de exclusão mútua
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.cores_jogadores = [colors.OKGREEN, colors.OKBLUE, colors.OKPURPLE, colors.ORANGE, colors.GOLD]
        self.salas_tesouro = {}  # Dicionário para armazenar o estado de cada sala do tesouro
        self.salas_tesouro_locks = {}  # Dicionário para armazenar os semáforos de cada sala do tesouro
        self.estado_salas_tesouro = {}  # Dicionário para armazenar o estado de coleta de cada sala do tesouro
        self.inicializar_salas_tesouro()

    def inicializar_salas_tesouro(self):
        """
        Inicializa o estado das salas do tesouro no mapa principal.
        """
        for i in range(self.linhas_mapa_principal):
            for j in range(self.colunas_mapa_principal):
                if self.mapa_principal.eh_sala_tesouro((i, j)):
                    self.estado_salas_tesouro[(i, j)] = False # Inicializa o estado da sala do tesouro como não coletada
                    self.salas_tesouro_locks[(i, j)] = Semaphore(1) # Inicializa os semáforos das salas do tesouro
                    

    def iniciar(self):
        """
        Inicia o servidor e aguarda conexões de jogadores.
        """
        print("Aguardando jogadores...")
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Conexão estabelecida com {addr}")
            threading.Thread(target=self.gerenciar_jogador, args=(client_socket,)).start()

    def exibir_instrucoes(self):
        """
        Exibe as instruções do jogo para o jogador.
        
        Returns:
            str: Instruções do jogo.
        """
        instrucoes = "########################## Instruções ##########################\n" \
                     "'w' - move o jogador para cima\n" \
                     "'a' - move o jogador para esquerda\n" \
                     "'s' - move o jogador para baixo\n" \
                     "'d' - move o jogador para direita\n" \
                     "'entrar' - para entrar na sala do tesouro.\n" \
                     "'sair' - para desconectar do jogo.\n" \
                     "###############################################################\n\n"
        return instrucoes

    def gerenciar_jogador(self, client_socket):
        """
        Gerencia a conexão e as ações de um jogador.
        
        Args:
            client_socket (socket.socket): Socket do jogador.
        """
        jogador_id = len(self.jogadores) + 1
        pos_inicial = self.mapa_principal.posicao_aleatoria()
        self.jogadores[jogador_id] = {"socket": client_socket, "pos": pos_inicial, "pontos": 0}
        
        client_socket.send(f"\nBem-vindo ao jogo! Você é o jogador {jogador_id}\n\n".encode())
        client_socket.send(self.exibir_instrucoes().encode())
        client_socket.send(self.mapa_principal.exibir_mapa(self.jogadores).encode())  # Envia o mapa ao jogador

        while True:
            try:
                comando = client_socket.recv(1024).decode().strip().lower()
                self.processar_comando(client_socket, jogador_id, comando)
            except ConnectionResetError:
                print(f"Jogador {jogador_id} desconectado abruptamente.")
                del self.jogadores[jogador_id]
                client_socket.close()
                break
            except OSError:
                break

    def log_acao_jogador(self, jogador_id, acao, detalhe=""):
        """
        Registra a ação de um jogador no console.
        
        Args:
            jogador_id (int): ID do jogador.
            acao (str): Ação realizada pelo jogador.
            detalhe (str): Detalhes adicionais da ação.
        """
        cor = self.cores_jogadores[(jogador_id - 1) % len(self.cores_jogadores)]
        print(f"{cor}Jogador {jogador_id}: {acao} {detalhe}{colors.ENDC}")

    def processar_comando(self, client_socket, jogador_id, comando):
        """
        Processa o comando recebido de um jogador.
        
        Args:
            client_socket (socket.socket): Socket do jogador.
            jogador_id (int): ID do jogador.
            comando (str): Comando recebido do jogador.
        """
        movimentos = {"w": (-1, 0), "a": (0, -1), "s": (1, 0), "d": (0, 1)}
        jogador_pos = self.jogadores[jogador_id]["pos"]

        if comando in movimentos:
            nova_pos = (jogador_pos[0] + movimentos[comando][0], jogador_pos[1] + movimentos[comando][1])
            if self.mapa_principal.valida_posicao(nova_pos):
                with self.lock_mapa:
                    self.jogadores[jogador_id]["pos"] = nova_pos
                    self.jogadores[jogador_id]["pos_anterior"] = nova_pos  # atualiza a posição anterior do jogador
                    self.log_acao_jogador(jogador_id, "moveu-se para", nova_pos)
                    if self.mapa_principal.coletar_tesouro(nova_pos):
                        self.jogadores[jogador_id]["pontos"] += 1  # Pontos do jogador
                        client_socket.send(f"\n{colors.OKGREEN}>>> Tesouro coletado <<<{colors.ENDC}\n".encode())
                        self.log_acao_jogador(jogador_id, "coletou um tesouro em", nova_pos)
                        if self.todos_tesouros_coletados():
                            self.exibir_ranking()
            self.atualizar_mapas_para_todos_jogadores()

        elif comando == "entrar":
            if self.mapa_principal.eh_sala_tesouro(jogador_pos):
                if jogador_pos not in self.salas_tesouro:
                    self.salas_tesouro[jogador_pos] = Mapa(self.linhas_sala_tesouro, self.colunas_sala_tesouro)  # Criando um novo mapa da sala do tesouro
                    self.salas_tesouro[jogador_pos].inicializar_tesouros(quantidade=self.max_tesouros_sala, sala_tesouro=True)  # Inicializa a sala com tesouros
                if not self.estado_salas_tesouro.get(jogador_pos, False):  # Verifica se todos os tesouros da sala do tesouro já foram coletados
                    if self.salas_tesouro_locks[jogador_pos].acquire(blocking=False):
                        self.sala_tesouro = self.salas_tesouro[jogador_pos]
                        self.log_acao_jogador(jogador_id, "entrou na sala do tesouro")
                        self.jogadores[jogador_id]["na_sala_tesouro"] = True  # Jogador dentro da sala do tesouro
                        self.jogadores[jogador_id]["pos_anterior"] = self.jogadores[jogador_id]["pos"]  # Salva a última posição do jogador
                        self.sala_do_tesouro(client_socket, jogador_id, jogador_pos)
                        self.jogadores[jogador_id]["na_sala_tesouro"] = False  # Jogador fora da sala do tesouro
                        self.salas_tesouro_locks[jogador_pos].release()
                    else:
                        client_socket.send(f"\n{colors.RED}>>> A sala do tesouro está ocupada por outro jogador <<<{colors.RED}\n".encode())
                else:
                    client_socket.send(f"{colors.RED}Você não pode entrar em um Tesouro que já foi coletado{colors.ENDC}\n".encode())
            else:
                client_socket.send(f"{colors.RED}Você não está em uma sala do tesouro{colors.ENDC}\n".encode())
            self.atualizar_mapas_para_todos_jogadores()

        elif comando == "sair":
            print(f"Jogador {jogador_id} desconectado.")
            self.log_acao_jogador(jogador_id, "desconectou-se do jogo")
            del self.jogadores[jogador_id]
            try:
                client_socket.send("Saindo do jogo...\n".encode())
            except ConnectionResetError:
                pass
            client_socket.close()

        else:
            client_socket.send(f"{colors.RED}Movimento inválido, tente um comando válido{colors.ENDC}\n".encode())
            client_socket.send(self.mapa_principal.exibir_mapa(self.jogadores).encode())  # Envia o mapa ao jogador

    def sala_do_tesouro(self, client_socket, jogador_id, posicao_anterior):
        """
        Gerencia a entrada e ações do jogador na sala do tesouro.
        
        Args:
            client_socket (socket.socket): Socket do jogador.
            jogador_id (int): ID do jogador.
            posicao_anterior (tuple): Posição anterior do jogador no mapa principal.
        """
        x, y = posicao_anterior
        client_socket.send(f"\n>>> Você entrou na sala do tesouro ({x, y}) <<<".encode())
        client_socket.send(f"\n{colors.RED}>>> Você tem 10 segundos para coletar os Tesouros dessa sala <<<{colors.ENDC}\n\n".encode())
        jogador_pos = (random.randint(0, self.linhas_sala_tesouro - 1), random.randint(0, self.colunas_sala_tesouro - 1))
        self.jogadores[jogador_id]["pos"] = jogador_pos
        client_socket.send(self.sala_tesouro.exibir_mapa({jogador_id: {"pos": jogador_pos}}).encode())  # Envia o mapa da sala do tesouro

        tempo_restante = 10
        start_time = time.time()
        while tempo_restante > 0:
            try:
                comando = client_socket.recv(1024).decode().strip().lower()
                movimentos = {"w": (-1, 0), "a": (0, -1), "s": (1, 0), "d": (0, 1)}
                if comando in movimentos:
                    nova_pos = (jogador_pos[0] + movimentos[comando][0], jogador_pos[1] + movimentos[comando][1])
                    if self.sala_tesouro.valida_posicao(nova_pos):
                        jogador_pos = nova_pos
                        self.jogadores[jogador_id]["pos"] = jogador_pos
                        self.log_acao_jogador(jogador_id, "moveu-se para", nova_pos)
                        if self.sala_tesouro.coletar_tesouro(nova_pos):
                            self.jogadores[jogador_id]["pontos"] += 1  # Pontos do jogador
                            client_socket.send(f"\n{colors.OKGREEN}>>> Tesouro coletado <<<{colors.ENDC}\n".encode())
                            self.log_acao_jogador(jogador_id, "coletou um tesouro em", nova_pos)
                        if self.sala_tesouro.todos_tesouros_coletados():
                            self.estado_salas_tesouro[posicao_anterior] = True
                            x, y = posicao_anterior
                            self.mapa_principal.celulas[x][y] = f"{colors.RED}x{colors.ENDC}"
                            client_socket.send(f"\n{colors.OKGREEN}>>> Todos os tesouros desta sala foram coletados <<<{colors.ENDC}\n".encode())
                            print(f"Todos os tesouros da sala {(x, y)} foram coletados")
                elif comando == "sair":
                    self.log_acao_jogador(jogador_id, "saiu da sala do tesouro")
                    client_socket.send("Você saiu da sala do tesouro.\n".encode())
                    break
                else:
                    client_socket.send(f"{colors.RED}\n>>> Movimento inválido, tente um comando válido <<<{colors.ENDC}\n".encode())
                client_socket.send(self.sala_tesouro.exibir_mapa({jogador_id: {"pos": jogador_pos}}).encode())  # Envia o mapa atualizado ao jogador
            except BlockingIOError:
                pass
            except ConnectionResetError:
                break

            tempo_restante = 10 - int(time.time() - start_time)
            time.sleep(0.1)

        if tempo_restante <= 0:
            client_socket.send(f"\n{colors.RED}>>> Tempo esgotado :( <<<{colors.ENDC}\n".encode())

        self.jogadores[jogador_id]["pos"] = posicao_anterior  # Retorna o jogador à posição anterior no mapa principal
        self.jogadores[jogador_id]["pos_anterior"] = posicao_anterior  # Garante que a posição anterior seja atualizada
        self.sala_tesouro = None
        for jogador in self.jogadores.values():
            if not jogador.get("na_sala_tesouro", False):
                jogador["socket"].send(self.mapa_principal.exibir_mapa(self.jogadores).encode())  # Envia o mapa atualizado a todos os jogadores
        
        if self.todos_tesouros_coletados():
            self.exibir_ranking()

    def todos_tesouros_salas_tesouro_coletados(self):
        """
        Verifica se todos os tesouros das salas do tesouro foram coletados.
        
        Returns:
            bool: True se todos os tesouros foram coletados, False caso contrário.
        """
        for sala, estado in self.estado_salas_tesouro.items():
            if not estado:
                return False
        return True
    
    def todos_tesouros_coletados(self):
        """
        Verifica se todos os tesouros do mapa principal e das salas do tesouro foram coletados.
        
        Returns:
            bool: True se todos os tesouros foram coletados, False caso contrário.
        """
        return self.mapa_principal.todos_tesouros_coletados() and self.todos_tesouros_salas_tesouro_coletados()
    
    def exibir_ranking(self):
        """
        Exibe o ranking dos jogadores com base nos pontos acumulados.
        """
        ranking = sorted(self.jogadores.items(), key=lambda item: item[1]["pontos"], reverse=True)
        ranking_str = f"\n{colors.OKPURPLE}>>> Ranking dos Jogadores <<<{colors.ENDC}\n"
        for pos, (jogador_id, info) in enumerate(ranking, start=1):
            ranking_str += f"{colors.OKPURPLE}{pos}º Lugar: Jogador {jogador_id} ------> {info['pontos']} pontos{colors.ENDC}\n"
            try:
                info["socket"].send(f"\n{colors.OKGREEN}>>> Você ficou na {pos}ª posição com {info['pontos']} pontos <<<{colors.ENDC}\n".encode())
            except:
                pass
        print(ranking_str)
        for jogador_id, info in self.jogadores.items():
            try:
                info["socket"].send(ranking_str.encode())
            except:
                pass

    def atualizar_mapas_para_todos_jogadores(self):
        """
        Atualiza o mapa para todos os jogadores conectados.
        """
        mapa_atualizado = self.mapa_principal.exibir_mapa(self.jogadores, posicao_do_jogador="pos_anterior").encode()
        for _, jogador in self.jogadores.items():
            if not jogador.get("na_sala_tesouro", False):
                try:
                    jogador["socket"].send(mapa_atualizado)
                except:
                    pass

if __name__ == "__main__":
    servidor = Servidor(tamanho_mapa=(8, 8), max_tesouros_mapa=10, tamanho_sala_tesouro=(4, 4), max_tesouros_sala=16)
    servidor.iniciar()
