# Projeto MOM - Sistema de Mensageria Distribuída em Python (RabbitMQ/Tkinter)

Este projeto é uma implementação didática de um Message-Oriented Middleware (MOM) usando RabbitMQ para mensageria e Tkinter para interfaces gráficas. Você pode criar tópicos, usuários, enviar e receber mensagens em tempo real!

##  Tecnologias Utilizadas
- 🐍 Python 3
- 🐇 RabbitMQ (mensageria)
- 🎨 Tkinter (GUI)
- 📬 Pika (cliente RabbitMQ em Python)

# Visão Geral
- Admin: Gerencia usuários e tópicos do sistema (criar, remover, listar).
- Publisher: Envia mensagens para tópicos ou diretamente para usuários.
- Subscriber: Recebe mensagens dos tópicos assinados e mensagens diretas.

## 🚦 Como Funciona
- O admin cadastra tópicos e usuários.
- O publisher envia mensagens para tópicos ou usuários.
- O subscriber faz login, assina tópicos e recebe mensagens em tempo real!

## 🚀 Como Rodar
### 1. Clone o repositório

```
git clone https://github.com/seu-usuario/projeto-mom-python.git
cd projeto-mom-python
```
### 2. Requisitos
- Python 3.7+
- RabbitMQ rodando localmente (localhost)
- Instale as dependências:
```
pip install pika
```
### 3. Rode o RabbitMQ
No Windows, pode iniciar pelo menu ou pelo terminal:
```
rabbitmq-server
```
### 4. Execute os modulos

```
python admin.py
```

```
python publisher.py
```
```
python subscriber.py
```
