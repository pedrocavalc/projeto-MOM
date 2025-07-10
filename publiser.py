# publisher.py
import tkinter as tk
from tkinter import messagebox
import pika, os

TOPICOS_FILE = "topicos.txt"
USUARIOS_FILE = "usuarios.txt"

def ler_arquivo(arquivo):
    if not os.path.exists(arquivo): return []
    with open(arquivo, "r") as f:
        return [linha.strip() for linha in f if linha.strip()]

def atualizar_listas():
    topicos = ler_arquivo(TOPICOS_FILE)
    menu_topico['menu'].delete(0, 'end')
    for t in topicos:
        menu_topico['menu'].add_command(label=t, command=tk._setit(var_topico, t))
    if topicos:
        var_topico.set(topicos[0])
    usuarios = ler_arquivo(USUARIOS_FILE)
    menu_user['menu'].delete(0, 'end')
    for u in usuarios:
        menu_user['menu'].add_command(label=u, command=tk._setit(var_user, u))
    if usuarios:
        var_user.set(usuarios[0])

def enviar_topico():
    topico = var_topico.get()
    msg = entry_msg.get()
    if topico and msg:
        channel.exchange_declare(exchange=topico, exchange_type='fanout')
        channel.basic_publish(exchange=topico, routing_key='', body=msg)
        messagebox.showinfo("Enviado", f"Enviado para tópico '{topico}'.")
        entry_msg.delete(0, tk.END)

def enviar_usuario():
    usuario = var_user.get()
    msg = entry_msg2.get()
    if usuario and msg:
        fila = "queue_" + usuario
        channel.queue_declare(queue=fila)
        channel.basic_publish(exchange='', routing_key=fila, body=msg)
        messagebox.showinfo("Enviado", f"Enviado para usuário '{usuario}'.")
        entry_msg2.delete(0, tk.END)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

root = tk.Tk()
root.title("Publisher MOM")

tk.Label(root, text="Enviar para Tópico:").pack()
var_topico = tk.StringVar(root)
menu_topico = tk.OptionMenu(root, var_topico, '')
menu_topico.pack()
entry_msg = tk.Entry(root, width=40)
entry_msg.pack()
tk.Button(root, text="Enviar para Tópico", command=enviar_topico).pack(pady=4)

tk.Label(root, text="Enviar mensagem direta para usuário:").pack(pady=(10,0))
var_user = tk.StringVar(root)
menu_user = tk.OptionMenu(root, var_user, '')
menu_user.pack()
entry_msg2 = tk.Entry(root, width=40)
entry_msg2.pack()
tk.Button(root, text="Enviar para Usuário", command=enviar_usuario).pack(pady=4)

tk.Button(root, text="Atualizar listas", command=atualizar_listas).pack(pady=8)
atualizar_listas()
root.mainloop()
