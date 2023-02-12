import socket
import argparse
from encryption import Encryption


def send_order(order_type, order_side, order_details):
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's address and port
    server_address = ('localhost', 10000)
    client_socket.connect(server_address)

    # Setup order detail encryption

    encryption = Encryption(8, 17, 8000000000000)
    order_price = int(order_details.split(",")[0])
    order_quantity = encryption.encrypt(int((order_details.split(","))[1]))
    order_info = [order_price, str(order_quantity).split('\n + ')]

    try:
        # Send data
        message = f'{order_type};{order_side};{order_info}'
        print(message)
        client_socket.sendall(message.encode())

        # Receive response from server
        data = client_socket.recv(1024).decode()
        print(f'Received from server: {data}')
    finally:
        client_socket.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send a cryptocurrency exchange order')
    parser.add_argument('-o', '--order_type', choices=['limit', 'market'], required=True, help='Type of order')
    parser.add_argument('-s', '--order_side', choices=['bid', 'ask'], required=True, help='Order Side')
    parser.add_argument('-d', '--order_details', required=True, help='Details of the order')
    args = parser.parse_args()

    send_order(args.order_type, args.order_side, args.order_details)
