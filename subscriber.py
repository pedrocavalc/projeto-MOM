import tkinter as tk
from tkinter import messagebox
import pika, threading, os

TOPICOS_FILE = "topicos.txt"
USUARIOS_FILE = "usuarios.txt"

def ler_arquivo(arquivo):
    if not os.path.exists(arquivo): return []
    with open(arquivo, "r") as f:
        return [linha.strip() for linha in f if linha.strip()]

class SubscriberApp:
    def __init__(self, master):
        self.master = master
        master.title("Subscriber MOM")

        tk.Label(master, text="Seu nome de usuário:").pack()
        self.entry_nome = tk.Entry(master)
        self.entry_nome.pack()
        tk.Button(master, text="Entrar", command=self.logar).pack(pady=4)

        self.texto = tk.Text(master, height=15, width=55)
        self.texto.pack()
        self.texto.insert(tk.END, "Faça login para começar!\n")
        self.texto.config(state=tk.DISABLED)

        self.frame_topicos = tk.Frame(master)
        self.listbox = tk.Listbox(self.frame_topicos, selectmode=tk.MULTIPLE, width=30)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrollbar = tk.Scrollbar(self.frame_topicos)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        self.frame_topicos.pack(pady=4)

        tk.Button(master, text="Assinar tópicos selecionados", command=self.assinar_topicos).pack()
        tk.Button(master, text="Receber mensagens diretas", command=self.assinar_fila_individual).pack(pady=2)

        self.atualizar_topicos()
        tk.Button(master, text="Atualizar tópicos", command=self.atualizar_tudo).pack()

        self.frame_direct = tk.Frame(master)
        tk.Label(self.frame_direct, text="Enviar mensagem direta para:").pack(side=tk.LEFT)
        self.combo_dest = tk.StringVar(master)
        self.dropdown_users = tk.OptionMenu(self.frame_direct, self.combo_dest, '')
        self.dropdown_users.pack(side=tk.LEFT)
        self.entry_direct_msg = tk.Entry(self.frame_direct, width=20)
        self.entry_direct_msg.pack(side=tk.LEFT, padx=3)
        tk.Button(self.frame_direct, text="Enviar", command=self.enviar_mensagem_direta).pack(side=tk.LEFT)
        self.frame_direct.pack(pady=6)
        self.username = None

    def logar(self):
        self.username = self.entry_nome.get().strip()
        if not self.username:
            messagebox.showwarning("Atenção", "Digite o nome do usuário.")
            return
        usuarios = ler_arquivo(USUARIOS_FILE)
        if self.username not in usuarios:
            messagebox.showwarning("Atenção", "Usuário não existe. Peça para o admin criar!")
            return
        self.texto.config(state=tk.NORMAL)
        self.texto.insert(tk.END, f"Logado como: {self.username}\n")
        self.texto.config(state=tk.DISABLED)
        self.atualizar_usuarios()

    def atualizar_topicos(self):
        topicos = ler_arquivo(TOPICOS_FILE)
        self.listbox.delete(0, tk.END)
        for t in topicos:
            self.listbox.insert(tk.END, t)

    def atualizar_usuarios(self):
        usuarios = ler_arquivo(USUARIOS_FILE)
        menu = self.dropdown_users['menu']
        menu.delete(0, 'end')
        for u in usuarios:
            if u != self.username:
                menu.add_command(label=u, command=tk._setit(self.combo_dest, u))
        outros = [u for u in usuarios if u != self.username]
        if outros:
            self.combo_dest.set(outros[0])
        else:
            self.combo_dest.set('')

    def atualizar_tudo(self):
        self.atualizar_topicos()
        self.atualizar_usuarios()

    def assinar_topicos(self):
        indices = self.listbox.curselection()
        topicos = [self.listbox.get(i) for i in indices]
        for t in topicos:
            threading.Thread(target=self.receber_topico, args=(t,), daemon=True).start()
        self.texto.config(state=tk.NORMAL)
        self.texto.insert(tk.END, f"Assinando tópicos: {', '.join(topicos)}\n")
        self.texto.config(state=tk.DISABLED)

    def assinar_fila_individual(self):
        threading.Thread(target=self.receber_fila_individual, daemon=True).start()
        self.texto.config(state=tk.NORMAL)
        self.texto.insert(tk.END, f"Assinando fila individual: queue_{self.username}\n")
        self.texto.config(state=tk.DISABLED)

    def receber_topico(self, topico):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange=topico, exchange_type='fanout')
        result = channel.queue_declare('', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange=topico, queue=queue_name)

        def callback(ch, method, properties, body):
            self.texto.config(state=tk.NORMAL)
            self.texto.insert(tk.END, f"[{topico}] {body.decode()}\n")
            self.texto.config(state=tk.DISABLED)
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    def receber_fila_individual(self):
        fila = f"queue_{self.username}"
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=fila)
        def callback(ch, method, properties, body):
            self.texto.config(state=tk.NORMAL)
            self.texto.insert(tk.END, f"[Mensagem direta] {body.decode()}\n")
            self.texto.config(state=tk.DISABLED)
        channel.basic_consume(queue=fila, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    def enviar_mensagem_direta(self):
        destinatario = self.combo_dest.get()
        msg = self.entry_direct_msg.get().strip()
        if not destinatario or not msg:
            messagebox.showwarning("Atenção", "Selecione um usuário e digite a mensagem.")
            return
        fila = f"queue_{destinatario}"
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=fila)
        # Adiciona remetente na mensagem
        channel.basic_publish(exchange='', routing_key=fila, body=f"[De {self.username}]: {msg}")
        connection.close()
        self.texto.config(state=tk.NORMAL)
        self.texto.insert(tk.END, f"[Para {destinatario}]: {msg}\n")
        self.texto.config(state=tk.DISABLED)
        self.entry_direct_msg.delete(0, tk.END)

root = tk.Tk()
app = SubscriberApp(root)
root.mainloop()
