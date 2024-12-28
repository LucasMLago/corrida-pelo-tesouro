# Documentação

## Funcionamento da Exclusão Mútua (Semáforos)

No código, a exclusão mútua é implementada usando semáforos (`threading.Semaphore`). Semáforos são usados para controlar o acesso a recursos compartilhados, garantindo que apenas um thread possa acessar um recurso específico por vez.

No contexto do jogo, semáforos são usados para proteger o acesso a células do mapa e salas do tesouro:

- **Semáforos de Células (`self.semaforos_celulas`)**: Cada célula do mapa tem um semáforo associado. Quando um jogador tenta coletar um tesouro em uma célula, o semáforo dessa célula é adquirido. Isso garante que apenas um jogador possa coletar o tesouro em uma célula específica por vez.
- **Semáforos de Salas (`self.sala_semaforos`)**: Cada sala do tesouro tem um semáforo associado. Quando um jogador tenta acessar uma sala do tesouro, o semáforo dessa sala é adquirido. Isso garante que apenas um jogador possa acessar uma sala do tesouro por vez.

## Lógica do Servidor para Gerenciar Estados do Jogo

O servidor gerencia o estado do jogo através de várias funções e mecanismos:

1. **Inicialização do Servidor**: O servidor é inicializado com um endereço e porta específicos. Ele cria um socket para ouvir conexões de clientes e inicia um loop para aceitar conexões.

2. **Tratamento de Clientes**: Quando um cliente se conecta, o servidor cria um novo thread para tratar a comunicação com esse cliente. Isso permite que o servidor trate múltiplos clientes simultaneamente.

3. **Envio do Estado Inicial**: Quando um cliente se conecta, o servidor envia o estado inicial do mapa para o cliente. Isso inclui a posição dos tesouros no mapa.

4. **Tratamento de Mensagens**: O servidor recebe mensagens dos clientes e as trata de acordo com o tipo de mensagem. Por exemplo, se um cliente coleta um tesouro, o servidor atualiza o estado do mapa e envia uma mensagem para todos os outros clientes informando sobre a coleta do tesouro.

5. **Broadcast**: O servidor envia mensagens para todos os clientes conectados, exceto o remetente. Isso é usado para informar todos os jogadores sobre ações importantes, como a coleta de um tesouro.

6. **Logs**: Existem dois tipos de logs no sistema:

    - **Logs do Servidor**: O servidor registra ações importantes, como conexões de clientes, coleta de tesouros e saída de jogadores. Esses logs ajudam a monitorar o estado do jogo e a diagnosticar problemas no servidor.

    ```
    2024-12-27 22:27:38,058 - INFO - Servidor iniciado em localhost:8080
    2024-12-27 22:27:46,239 - INFO - Conexão estabelecida com ('127.0.0.1', 51151)
    2024-12-27 22:27:48,580 - INFO - O Jogador 51151: COLETAR_TESOURO 0 0
    2024-12-27 22:28:09,556 - INFO - O Jogador 51151: COLETAR_TESOURO 6 3
    2024-12-27 22:28:11,343 - INFO - O Jogador 51151 saiu do jogo.
    ```
    
    - **Logs do Cliente**: Cada cliente também pode registrar suas próprias ações, como tentativas de coleta de tesouros e movimentações no mapa. Esses logs são úteis para os jogadores acompanharem suas atividades e para a resolução de problemas específicos do cliente.

    ```
    Tesouros restantes no mapa principal: 7
    Jogador entrou na sala do tesouro em (2, 2)!
    Tesouros restantes na sala (2, 2): 15
    Tesouros restantes na sala (2, 2): 14
    Jogador saiu voluntariamente da sala (2, 2)!
    Jogador entrou na sala do tesouro em (3, 5)!
    Tesouros restantes na sala (3, 5): 15
    Tesouros restantes na sala (3, 5): 14
    Tempo esgotado na sala (3, 5)!
    Jogador saiu da sala do tesouro em (3, 5)!
    Tesouros restantes no mapa principal: 6
    Encerrando o jogo...
    Conexão com o servidor perdida.
    ```