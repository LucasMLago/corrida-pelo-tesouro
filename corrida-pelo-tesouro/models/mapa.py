import random
from models.colors import colors

class Mapa:
    """
    Classe Mapa para representar o mapa do jogo Corrida Pelo Tesouro.
    
    Atributos:
        linhas (int): Número de linhas do mapa.
        colunas (int): Número de colunas do mapa.
        celulas (list): Matriz que representa as células do mapa.
        tesouros (list): Lista de posições dos tesouros no mapa.
    """
    def __init__(self, linhas, colunas):
        """
        Inicializa a classe Mapa com o número de linhas e colunas.
        
        Args:
            linhas (int): Número de linhas do mapa.
            colunas (int): Número de colunas do mapa.
        """
        self.linhas = linhas
        self.colunas = colunas
        self.celulas = [["." for _ in range(colunas)] for _ in range(linhas)]
        self.tesouros = []
        self.inicializar_tesouros()

    def inicializar_tesouros(self, quantidade=None, sala_tesouro=False):
        """
        Inicializa os tesouros no mapa.
        
        Args:
            quantidade (int): Número de tesouros a serem inicializados. Se None, um valor aleatório é escolhido.
            sala_tesouro (bool): Indica se os tesouros estão sendo inicializados em uma sala do tesouro.
        """
        if sala_tesouro:
            for i in range(self.linhas):
                for j in range(self.colunas):
                    self.celulas[i][j] = f"{colors.GOLD}T{colors.ENDC}"
                    self.tesouros.append((i, j))
        else:
            if quantidade is None:
                quantidade = random.randint(5, 10)
            for _ in range(quantidade):
                x, y = self.posicao_aleatoria()
                self.celulas[x][y] = f"{colors.GOLD}T{colors.ENDC}"
                self.tesouros.append((x, y))

    def valida_posicao(self, pos):
        """
        Verifica se uma posição é válida no mapa.
        
        Args:
            pos (tuple): Posição a ser verificada (linha, coluna).
        
        Returns:
            bool: True se a posição é válida, False caso contrário.
        """
        x, y = pos
        return 0 <= x < self.linhas and 0 <= y < self.colunas

    def coletar_tesouro(self, pos):
        """
        Coleta um tesouro na posição especificada.
        
        Args:
            pos (tuple): Posição do tesouro a ser coletado (linha, coluna).
        
        Returns:
            bool: True se o tesouro foi coletado, False caso contrário.
        """
        if pos in self.tesouros:
            self.tesouros.remove(pos)
            x, y = pos
            self.celulas[x][y] = f"{colors.RED}x{colors.ENDC}"
            return True
        return False

    def todos_tesouros_coletados(self):
        """
        Verifica se todos os tesouros foram coletados.
        
        Returns:
            bool: True se todos os tesouros foram coletados, False caso contrário.
        """
        return len(self.tesouros) == 0

    def eh_sala_tesouro(self, pos):
        """
        Verifica se uma posição é uma sala do tesouro.
        
        Args:
            pos (tuple): Posição a ser verificada (linha, coluna).
        
        Returns:
            bool: True se a posição é uma sala do tesouro, False caso contrário.
        """
        x, y = pos
        return self.celulas[x][y] == "."

    def posicao_aleatoria(self):
        """
        Retorna uma posição aleatória válida no mapa.
        
        Returns:
            tuple: Posição aleatória (linha, coluna).
        """
        while True:
            x, y = random.randint(0, self.linhas - 1), random.randint(0, self.colunas - 1)
            if self.celulas[x][y] == ".":
                return (x, y)

    def exibir_mapa(self, jogadores=None, posicao_do_jogador="pos"):
        """
        Exibe o mapa com a posição dos jogadores.
        
        Args:
            jogadores (dict): Dicionário de jogadores com suas posições.
            posicao_do_jogador (str): Chave para acessar a posição do jogador no dicionário de jogadores.
        
        Returns:
            str: Representação do mapa com a posição dos jogadores.
        """
        mapa_str = "    " + " ".join(str(i) for i in range(self.colunas)) + "\n"
        mapa_str += "  " + "-" * (self.colunas * 2 + 3) + "\n"
        for i in range(self.linhas):
            linha = []
            for j in range(self.colunas):
                jogador_na_posicao = False
                if jogadores:
                    for jogador_id, jogador_info in jogadores.items():
                        if (i, j) == jogador_info.get(posicao_do_jogador, jogador_info["pos"]) and (i, j):
                            linha.append(f"{colors.OKBLUE}{jogador_id}{colors.ENDC}")
                            jogador_na_posicao = True
                            break
                if not jogador_na_posicao:
                    linha.append(self.celulas[i][j])
            mapa_str += str(i) + " | " + " ".join(linha) + " |\n"
        mapa_str += "  " + "-" * (self.colunas * 2 + 3) + "\n"
        return mapa_str
