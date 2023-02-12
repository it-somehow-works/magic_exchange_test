import socket
import requests
import time
import threading
import json
import asyncio
import aiohttp
import numpy as np
import random
from encryption import Encryption
import util


class OrderBook:
    def __init__(self):
        self.ask_book = []
        self.bid_book = []
        self.total_eth = 1000

    async def initialize_orders(self):
        current_price = await retrieve_eth_price()
        prices = np.random.normal(current_price, current_price / 4, 30)

        bid_prices = sorted(prices)[:15]
        ask_prices = sorted(prices, reverse=True)[:15]
        for bid_price in bid_prices:
            self.add_limit_order('bid', bid_price, random.randint(10, 50))
        for ask_price in ask_prices:
            self.add_limit_order('ask', ask_price, random.randint(10, 50))

    def add_limit_order(self, order_side, price, quantity):
        if order_side == 'ask':
            self.ask_book.append({'price': price, 'quantity': quantity})
            self.ask_book = sorted(self.ask_book, key=lambda x: x['price'], reverse=True)
        elif order_side == 'bid':
            self.bid_book.append({'price': price, 'quantity': quantity})
            self.bid_book = sorted(self.bid_book, key=lambda x: x['price'])

    def add_market_order(self, order_type, quantity):
        if order_type == 'bid':
            while quantity > 0 and self.ask_book:
                price, available_quantity = self.ask_book[0]['price'], self.ask_book[0]['quantity']
                if available_quantity > quantity:
                    self.ask_book[0]['quantity'] = available_quantity - quantity
                    break
                else:
                    quantity -= available_quantity
                    self.ask_book.pop(0)
        elif order_type == 'ask':
            while quantity > 0 and self.bid_book:
                price, available_quantity = self.bid_book[0]['price'], self.bid_book[0]['quantity']
                if available_quantity > quantity:
                    self.bid_book[0]['quantity'] = available_quantity - quantity
                    break
                else:
                    quantity -= available_quantity
                    self.bid_book.pop(0)
        self.print_order_book()

    async def print_order_book(self):
        # Setup decryption
        encryption = Encryption(8, 17, 8000000000000)

        for order in self.ask_book:
            print(str(order['quantity']))
            if isinstance(order['quantity'], str) and 'c0' in order['quantity']:
                decrypted_quantity = encryption.decrypt(order['quantity'])
                order['quantity'] = decrypted_quantity

        print(f"Bid Side: {self.bid_book}")
        print(f"Ask Side: {self.ask_book}")

    async def remove_limit_order(self):
        current_price = await retrieve_eth_price()
        print(f'Current ETH price: {current_price}')
        for i in range(len(self.ask_book)-1):
            if self.ask_book and current_price >= self.ask_book[i]['price']:
                order = self.ask_book.pop(i)
                print(f'Order filled at price {order["price"]}')
        for j in range(len(self.bid_book)-1):
            if self.bid_book and current_price <= self.bid_book[j]['price']:
                order = self.bid_book.pop(j)
                print(f'Order filled at price {order["price"]}')
        print("No orders filled")


async def start_server():
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_address = ('localhost', 10000)
    print(f'Starting up server on {server_address[0]}:{server_address[1]}')
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)
    order_book = OrderBook()
    await order_book.initialize_orders()

    while True:
        print('Waiting for a connection...')
        client_socket, client_address = server_socket.accept()
        print(f'Accepted connection from {client_address[0]}:{client_address[1]}')

        # Start a new task to handle this connection
        await asyncio.ensure_future(handle_client(client_socket, client_address, order_book))

        await order_book.print_order_book()

        # Call the remove_limit_order function
        await order_book.remove_limit_order()


async def retrieve_eth_price():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD") as response:
                data = await response.json()
                return float(data['USD'])
    except:
        return -1.0


async def handle_client(client_socket, client_address, order_book):
    data = client_socket.recv(1024).decode().strip()
    print(f'Received: {data}')

    if data:
        order_type, order_side, order_details = data.split(';')
        if order_type == 'limit':
            order_details = order_details.replace('[', '').replace(']', '').split(',')
            print(order_details)
            price = float(order_details[0])
            quantity = order_details[1:]
            print(quantity)
            current_price = await retrieve_eth_price()
            if (order_side == 'ask' and price >= current_price) or (order_side == 'bid' and price <= current_price):
                order_book.add_limit_order(order_side, price, quantity)
                client_socket.sendall('Order added to book'.encode())
            else:
                client_socket.sendall('Order price not valid'.encode())
        elif order_type == 'market':
            quantity = float(order_details)
            order_book.add_market_order(order_side, quantity)
            client_socket.sendall('Order added to book'.encode())
    else:
        print(data)
        client_socket.close()


if __name__ == '__main__':
    asyncio.run(start_server())

