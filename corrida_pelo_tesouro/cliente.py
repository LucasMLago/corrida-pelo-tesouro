import socket
import threading
import tkinter as tk
from mapa import Mapa

class Cliente:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        threading.Thread(target=self.receber_mensagens).start()

    def enviar_mensagem(self, msg):
        self.sock.send(msg.encode('utf-8'))

    def receber_mensagens(self):
        while True:
            try:
                msg = self.sock.recv(1024).decode('utf-8')
                if msg:
                    print(f"Mensagem recebida: {msg}")
            except:
                print("Conexão com o servidor perdida.")
                self.sock.close()
                break

class InterfaceCliente:
    def __init__(self, cliente):
        self.cliente = cliente
        self.janela = tk.Tk()
        self.janela.title("Cliente Corrida Pelo Tesouro")
        self.centralizar_janela(self.janela, 300, 200)

        self.entrada = tk.Entry(self.janela, width=50)
        self.entrada.pack(pady=10)

        self.botao_enviar = tk.Button(self.janela, text="Enviar", command=self.enviar_mensagem)
        self.botao_enviar.pack(pady=10)

        self.janela.mainloop()

    def enviar_mensagem(self):
        msg = self.entrada.get()
        self.cliente.enviar_mensagem(msg)
        self.entrada.delete(0, tk.END)

    @staticmethod
    def centralizar_janela(janela, largura, altura):
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        x = (largura_tela - largura) // 2
        y = (altura_tela - altura) // 2
        janela.geometry(f"{largura}x{altura}+{x}+{y}")

if __name__ == "__main__":
    cliente = Cliente()
    janela = tk.Tk()
    mapa = Mapa(janela, cliente)
    janela.mainloop()
