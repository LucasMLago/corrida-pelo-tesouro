# Corrida Pelo Tesouro

Corrida Pelo Tesouro é um jogo multiplayer onde os jogadores competem para coletar tesouros em um mapa. O jogo é implementado em Python usando `tkinter` para a interface gráfica e `socket` para a comunicação entre cliente e servidor.

## Estrutura do Projeto

- **Servidor**: `server/servidor.py`
- **Mapa do Servidor**: `map/mapa.py`
- **Cliente**: `client/cliente.py`

## Requisitos

- Python 3.x
- Bibliotecas padrão do Python (`tkinter`, `socket`, `threading`, `random`, `logging`)

## Como Executar

### Servidor

1. Navegue até o diretório `server`:
    ```sh
    cd corrida-pelo-tesouro/server
    ```
2. Execute o servidor:
    ```sh
    python servidor.py
    ```

### Cliente

1. Navegue até o diretório `client`:
    ```sh
    cd corrida-pelo-tesouro/client
    ```
2. Execute o cliente:
    ```sh
    python cliente.py
    ```

## Funcionalidades

- **Mapa Principal**: O mapa principal contém tesouros que os jogadores podem coletar.
- **Salas do Tesouro**: Os jogadores podem acessar salas do tesouro para coletar mais tesouros.
- **Comunicação Cliente-Servidor**: O estado do jogo é sincronizado entre os clientes através do servidor.

## Documentação

Para mais detalhes sobre o funcionamento do jogo e a implementação, consulte a [Documentação](Documentacao.md).