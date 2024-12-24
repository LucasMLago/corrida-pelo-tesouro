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

6. **Logs**: O servidor registra ações importantes, como conexões de clientes, coleta de tesouros e saída de jogadores. Isso ajuda a monitorar o estado do jogo e a diagnosticar problemas.

## Logs de Execução Demonstrando Jogadores Acessando a Sala do Tesouro

Aqui estão alguns exemplos de logs de execução que demonstram jogadores acessando a sala do tesouro:

```
2023-10-10 12:00:00 - INFO - Servidor iniciado em localhost:8080
2023-10-10 12:01:00 - INFO - Conexão estabelecida com ('127.0.0.1', 50000)
2023-10-10 12:01:05 - INFO - O jogador ('127.0.0.1', 50000): COLETAR_TESOURO 2 3
2023-10-10 12:01:05 - INFO - O Jogador ('127.0.0.1', 50000) coletou um tesouro: COLETAR_TESOURO 2 3
2023-10-10 12:02:00 - INFO - O jogador ('127.0.0.1', 50000): ENTRAR_SALA_TESOURO 4 5
2023-10-10 12:02:00 - INFO - Jogador entrou na sala do tesouro em (4, 5)!
2023-10-10 12:02:10 - INFO - Tempo esgotado na sala (4, 5)!
2023-10-10 12:02:10 - INFO - Jogador saiu da sala do tesouro em (4, 5)!
2023-10-10 12:03:00 - INFO - O Jogador ('127.0.0.1', 50000) saiu do jogo.
```

Esses logs mostram o servidor iniciando, um cliente se conectando, coletando um tesouro, entrando em uma sala do tesouro, e finalmente saindo do jogo. Os logs ajudam a monitorar o estado do jogo e a entender as ações dos jogadores.