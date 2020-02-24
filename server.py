# -*- coding: utf-8 -*-
import select
import socket

SERVER_ADDRESS = ('localhost', 50007)

# Говорит о том, сколько дескрипторов единовременно могут быть открыты
MAX_CONNECTIONS = 100

# Откуда и куда записывать информацию
INPUTS = list()
OUTPUTS = list()


def get_non_blocking_server_socket():

    # Создаем сокет, который работает без блокирования основного потока
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)

    # Биндим сервер на нужный адрес и порт
    server.bind(SERVER_ADDRESS)

    # Установка максимального количество подключений
    server.listen(MAX_CONNECTIONS)

    return server


def handle_readables(readables, server):
    """
    Обработка появления событий на входах
    """
    for resource in readables:

        # Если событие исходит от серверного сокета, то мы получаем новое подключение
        if resource is server:
            connection, client_address = resource.accept()
            connection.setblocking(0)
            INPUTS.append(connection)
            print("new connection from {address}".format(address=client_address))

        # Если событие исходит не от серверного сокета, но сработало прерывание на наполнение входного буффера
        else:
            clear_resource(resource)


def clear_resource(resource):
    """
    Метод очистки ресурсов использования сокета
    """
    if resource in OUTPUTS:
        OUTPUTS.remove(resource)
    if resource in INPUTS:
        INPUTS.remove(resource)
    resource.close()

    print('closing connection ' + str(resource))


# Создаем серверный сокет без блокирования основного потока в ожидании подключения
server_socket = get_non_blocking_server_socket()
INPUTS.append(server_socket)

print("server is running, please, press ctrl+c to stop")
try:
    while INPUTS:
        readables, writables, exceptional = select.select(INPUTS, OUTPUTS, INPUTS)
        handle_readables(readables, server_socket)

except KeyboardInterrupt:
    clear_resource(server_socket)
    print("Server stopped! Thank you for using!")

