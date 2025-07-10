# admin.py
import tkinter as tk
from tkinter import simpledialog, messagebox
import pika, os

TOPICOS_FILE = "topicos.txt"
USUARIOS_FILE = "usuarios.txt"

def salvar_em_arquivo(arquivo, nome):
    with open(arquivo, "a") as f:
        f.write(nome + "\n")

def ler_arquivo(arquivo):
    if not os.path.exists(arquivo): return []
    with open(arquivo, "r") as f:
        return [linha.strip() for linha in f if linha.strip()]

def remover_de_arquivo(arquivo, nome):
    linhas = ler_arquivo(arquivo)
    with open(arquivo, "w") as f:
        for linha in linhas:
            if linha != nome:
                f.write(linha + "\n")

def criar_topico():
    nome = simpledialog.askstring("Criar Tópico", "Nome do tópico:")
    if nome and nome not in ler_arquivo(TOPICOS_FILE):
        channel.exchange_declare(exchange=nome, exchange_type='fanout')
        salvar_em_arquivo(TOPICOS_FILE, nome)
        messagebox.showinfo("Sucesso", f"Tópico '{nome}' criado!")
    else:
        messagebox.showwarning("Atenção", "Tópico já existe ou nome inválido.")

def remover_topico():
    nome = simpledialog.askstring("Remover Tópico", "Nome do tópico:")
    if nome in ler_arquivo(TOPICOS_FILE):
        channel.exchange_delete(exchange=nome)
        remover_de_arquivo(TOPICOS_FILE, nome)
        messagebox.showinfo("Sucesso", f"Tópico '{nome}' removido!")
    else:
        messagebox.showwarning("Atenção", "Tópico não encontrado.")

def listar_topicos():
    topicos = ler_arquivo(TOPICOS_FILE)
    messagebox.showinfo("Tópicos", "\n".join(topicos) if topicos else "Nenhum tópico.")

def criar_usuario():
    nome = simpledialog.askstring("Criar Usuário", "Nome do usuário:")
    if nome and nome not in ler_arquivo(USUARIOS_FILE):
        salvar_em_arquivo(USUARIOS_FILE, nome)
        fila = "queue_" + nome
        channel.queue_declare(queue=fila)
        messagebox.showinfo("Sucesso", f"Usuário '{nome}' criado! Fila '{fila}' criada.")
    else:
        messagebox.showwarning("Atenção", "Usuário já existe ou nome inválido.")

def remover_usuario():
    nome = simpledialog.askstring("Remover Usuário", "Nome do usuário:")
    if nome in ler_arquivo(USUARIOS_FILE):
        fila = "queue_" + nome
        channel.queue_delete(queue=fila)
        remover_de_arquivo(USUARIOS_FILE, nome)
        messagebox.showinfo("Sucesso", f"Usuário '{nome}' removido!")
    else:
        messagebox.showwarning("Atenção", "Usuário não encontrado.")

def listar_usuarios():
    usuarios = ler_arquivo(USUARIOS_FILE)
    messagebox.showinfo("Usuários", "\n".join(usuarios) if usuarios else "Nenhum usuário.")

def listar_filas():
    usuarios = ler_arquivo(USUARIOS_FILE)
    filas = [f"queue_{u}" for u in usuarios]
    messagebox.showinfo("Filas", "\n".join(filas) if filas else "Nenhuma fila.")

def remover_fila():
    usuarios = ler_arquivo(USUARIOS_FILE)
    fila = simpledialog.askstring("Remover Fila", "Nome exato da fila:")
    if fila in [f"queue_{u}" for u in usuarios]:
        channel.queue_delete(queue=fila)
        messagebox.showinfo("Sucesso", f"Fila '{fila}' removida!")
    else:
        messagebox.showwarning("Atenção", "Fila não encontrada.")

def qtd_msg_fila():
    usuarios = ler_arquivo(USUARIOS_FILE)
    filas = [f"queue_{u}" for u in usuarios]
    msg = ""
    for f in filas:
        q = channel.queue_declare(queue=f, passive=True)
        msg += f"{f}: {q.method.message_count} mensagens\n"
    messagebox.showinfo("Mensagens nas filas", msg if msg else "Nenhuma fila encontrada.")

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

root = tk.Tk()
root.title("Administração MOM")

botoes = [
    ("Criar Tópico", criar_topico),
    ("Remover Tópico", remover_topico),
    ("Listar Tópicos", listar_topicos),
    ("Criar Usuário", criar_usuario),
    ("Remover Usuário", remover_usuario),
    ("Listar Usuários", listar_usuarios),
    ("Listar Filas", listar_filas),
    ("Remover Fila", remover_fila),
    ("Qtd. mensagens por fila", qtd_msg_fila)
]

for txt, cmd in botoes:
    tk.Button(root, text=txt, command=cmd, width=30).pack(pady=2)

root.mainloop()
