# Corrida Pelo Tesouro

## Descrição

Corrida Pelo Tesouro é um jogo multiplayer onde os jogadores competem para coletar tesouros espalhados em um mapa. O jogo inclui um mapa principal e várias salas do tesouro, onde os jogadores podem entrar para coletar mais tesouros. O objetivo é coletar o máximo de tesouros possível e alcançar a maior pontuação.

## Objetivos

- **Competição**: Jogadores competem entre si para coletar tesouros e alcançar a maior pontuação.
- **Exploração**: Jogadores exploram o mapa principal e as salas do tesouro em busca de tesouros.
- **Multiplayer**: Suporte para múltiplos jogadores conectados ao mesmo tempo.

## Funcionalidades

- **Movimentação**: Jogadores podem se mover pelo mapa usando comandos de teclado.
- **Coleta de Tesouros**: Jogadores podem coletar tesouros espalhados pelo mapa.
- **Salas do Tesouro**: Jogadores podem entrar em salas do tesouro para coletar mais tesouros.
- **Ranking**: Exibição de um ranking dos jogadores com base na pontuação acumulada.

## Requisitos

- **Python 3**
- **Bibliotecas padrão do Python**:
  - `socket`: Utilizada para comunicação entre cliente e servidor.
  - `threading`: Utilizada para gerenciar múltiplas conexões de clientes simultaneamente.
  - `socket`: Utilizado para gerenciar as salas do tesouro com Semáforos e criação da interação Cliente-Servidor
  - `time`: Utilizada para gerenciar temporizações no jogo.
  - `random`: Utilizada para gerar posições aleatórias no mapa.
  - `os`: Utilizada para interações com o sistema operacional, como manipulação de arquivos e diretórios.
  - `sys`: Utilizada para manipular parâmetros e funções do sistema.
- **Sistema Operacional**: O código deve funcionar em qualquer sistema operacional que suporte Python 3.x, incluindo Windows, macOS e Linux.

## Configuração

1. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis de ambiente preenchidas como exemplo:

    ```plaintext
    IP_PRIVADO=localhost
    IP_PUBLICO=localhost
    PORTA=8080
    ```

## Como Rodar o Código

### Servidor

1. Execute o servidor:

    ```bash
    python corrida-pelo-tesouro/server/servidor.py
    ```

### Cliente

2. Execute um cliente:

    ```bash
    python corrida-pelo-tesouro/client/cliente.py
    ```

3. Repita o passo 2 para cada cliente/jogador adicional que deseja conectar ao servidor.

## Comandos do Jogo

- `'w'`: Move o jogador para cima.
- `'a'`: Move o jogador para a esquerda.
- `'s'`: Move o jogador para baixo.
- `'d'`: Move o jogador para a direita.
- `'entrar'`: Entra na sala do tesouro (se o jogador estiver em uma posição de entrada).
- `'sair'`: Desconecta do jogo ou sai da sala do tesouro.

- **client/cliente.py**: Código do cliente que conecta ao servidor e permite que o jogador envie comandos e receba atualizações.
- **models/colors.py**: Definições de cores para exibição no console.
- **models/mapa.py**: Implementação da classe Mapa que representa o mapa do jogo.
- **server/servidor.py**: Código do servidor que gerencia o jogo, incluindo a lógica de movimentação, coleta de tesouros e salas do tesouro.

## Documentação

Veja o arquivo [Documentação](DOC.md) para mais detalhes.