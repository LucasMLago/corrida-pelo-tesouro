# Documentação Detalhada do Projeto Corrida Pelo Tesouro

## Funcionamento da Exclusão Mútua (Semáforos)

No jogo Corrida Pelo Tesouro, a exclusão mútua é utilizada para garantir que múltiplos jogadores não acessem simultaneamente recursos críticos, como o mapa principal e as salas do tesouro. Para isso, utilizamos semáforos (`Semaphore`) da biblioteca `threading` do Python.

### Semáforo para o Mapa Principal

O semáforo `lock_mapa` é utilizado para controlar o acesso ao mapa principal. Sempre que um jogador se move ou coleta um tesouro no mapa principal, o semáforo é adquirido para garantir que nenhuma outra operação ocorra simultaneamente no mapa.

```python
self.lock_mapa = Semaphore()
```

### Semáforo para as Salas do Tesouro

Cada sala do tesouro possui seu próprio semáforo, armazenado no dicionário `salas_tesouro_locks`. Isso garante que apenas um jogador possa acessar uma sala do tesouro por vez.

```python
self.salas_tesouro_locks[jogador_pos] = Semaphore(1)
```

## Lógica do Servidor para Gerenciar Estados do Jogo

O servidor gerencia os estados do jogo, incluindo a movimentação dos jogadores, a coleta de tesouros e o acesso às salas do tesouro. A seguir, detalhamos a lógica do servidor para essas operações.

### Movimentação dos Jogadores

Quando um jogador envia um comando de movimentação (`w`, `a`, `s`, `d`), o servidor verifica se a nova posição é válida e, em caso afirmativo, atualiza a posição do jogador. Se o jogador coleta um tesouro, sua pontuação é incrementada.

```python
if comando in movimentos:
    nova_pos = (jogador_pos[0] + movimentos[comando][0], jogador_pos[1] + movimentos[comando][1])
    if self.mapa_principal.valida_posicao(nova_pos):
        with self.lock_mapa:
            self.jogadores[jogador_id]["pos"] = nova_pos
            self.jogadores[jogador_id]["pos_anterior"] = nova_pos
            if self.mapa_principal.coletar_tesouro(nova_pos):
                self.jogadores[jogador_id]["pontos"] += 1
```

### Acesso às Salas do Tesouro

Quando um jogador tenta entrar em uma sala do tesouro, o servidor verifica se a sala está disponível e, em caso afirmativo, permite o acesso. O jogador tem 10 segundos para coletar os tesouros na sala.

```python
if comando == "entrar":
    if self.mapa_principal.eh_sala_tesouro(jogador_pos):
        if jogador_pos not in self.salas_tesouro:
            self.salas_tesouro[jogador_pos] = Mapa(self.linhas_sala_tesouro, self.colunas_sala_tesouro)
            self.salas_tesouro[jogador_pos].inicializar_tesouros(quantidade=self.max_tesouros_sala, sala_tesouro=True)
            self.salas_tesouro_locks[jogador_pos] = Semaphore(1)
            self.estado_salas_tesouro[jogador_pos] = False
        if not self.estado_salas_tesouro.get(jogador_pos, False):
            if self.salas_tesouro_locks[jogador_pos].acquire(blocking=False):
                self.sala_tesouro = self.salas_tesouro[jogador_pos]
                self.jogadores[jogador_id]["na_sala_tesouro"] = True
                self.jogadores[jogador_id]["pos_anterior"] = self.jogadores[jogador_id]["pos"]
                self.sala_do_tesouro(client_socket, jogador_id, jogador_pos)
                self.jogadores[jogador_id]["na_sala_tesouro"] = False
                self.salas_tesouro_locks[jogador_pos].release()
```

## Logs de Execução

A seguir, apresentamos logs de execução demonstrando jogadores acessando a sala do tesouro.

### Jogador 1 Entra na Sala do Tesouro

```
Aguardando jogadores...
Conexão estabelecida com ('127.0.0.1', 54321)
Jogador 1: entrou na sala do tesouro
>>> Você entrou na sala do tesouro (3, 4) <<<
>>> Você tem 10 segundos para coletar os Tesouros dessa sala <<<
Jogador 1: moveu-se para (0, 1)
Jogador 1: coletou um tesouro em (0, 1)
>>> Tesouro coletado <<<
Jogador 1: moveu-se para (0, 2)
Jogador 1: coletou um tesouro em (0, 2)
>>> Tesouro coletado <<<
Jogador 1: saiu da sala do tesouro
Você saiu da sala do tesouro.
```

### Jogador 2 Tenta Entrar na Sala do Tesouro Ocupada

```
Aguardando jogadores...
Conexão estabelecida com ('127.0.0.1', 54322)
Jogador 2: tentou entrar na sala do tesouro
>>> A sala do tesouro está ocupada por outro jogador <<<
```

### Jogador 1 Sai da Sala do Tesouro e Jogador 2 Entra

```
Jogador 1: saiu da sala do tesouro
Você saiu da sala do tesouro.
Jogador 2: entrou na sala do tesouro
>>> Você entrou na sala do tesouro (3, 4) <<<
>>> Você tem 10 segundos para coletar os Tesouros dessa sala <<<
Jogador 2: moveu-se para (0, 1)
Jogador 2: coletou um tesouro em (0, 1)
>>> Tesouro coletado <<<
Jogador 2: moveu-se para (0, 2)
Jogador 2: coletou um tesouro em (0, 2)
>>> Tesouro coletado <<<
Jogador 2: saiu da sala do tesouro
Você saiu da sala do tesouro.
```
