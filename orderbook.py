from bfv.batch_encoder import BatchEncoder
from bfv.bfv_decryptor import BFVDecryptor
from bfv.bfv_encryptor import BFVEncryptor
from bfv.bfv_evaluator import BFVEvaluator
from bfv.bfv_key_generator import BFVKeyGenerator
from bfv.bfv_parameters import BFVParameters

degree = 8
plain_modulus = 17
ciph_modulus = 8000000000000
params = BFVParameters(poly_degree=degree,
                            plain_modulus=plain_modulus,
                            ciph_modulus=ciph_modulus)
key_generator = BFVKeyGenerator(params)
public_key = key_generator.public_key
secret_key = key_generator.secret_key
encoder = BatchEncoder(params)
encryptor = BFVEncryptor(params, public_key)
decryptor = BFVDecryptor(params, secret_key)


def encrypt(number):
    # self.encoder = BatchEncoder(self.params)
    plain1 = encoder.encode([number, 0, 0, 0, 0, 0, 0, 0])
    ciph1 = encryptor.encrypt(plain1)
    check = decrypt(ciph1)
    # print([number,0,0,0,0,0,0,0], check)
    return ciph1


def decrypt(product):
    # self.encoder = BatchEncoder(self.params)
    decrypted_prod = decryptor.decrypt(product)
    decoded_prod = encoder.decode(decrypted_prod)
    return decoded_prod


def evaluate(ciph1, ciph2):
    evaluator = BFVEvaluator(params)
    ciph_prod = evaluator.add(ciph1, ciph2)
    return ciph_prod


class Order:
    def __init__(self, order_id, order_type, price, amount):
        self.order_id = order_id
        self.order_type = order_type
        self.price = price
        self.amount = amount


class OrderBook:
    def __init__(self):
        self.bids = []
        self.asks = []
        self.order_id = 0

    def add_order(self, order_type, price, amount):
        self.order_id += 1
        print(str(amount))
        new_order = [self.order_id, order_type, price, amount]
        if order_type == "bid":
            self.bids.append(new_order)
            print("here2")
        elif order_type == "ask":
            self.asks.append(new_order)

    def execute_trade(self, trade_type, price, amount):
        if trade_type == "bid":
            for i in range(len(self.asks)):
                self.asks[i][3] = evaluate(self.asks[i][3], amount)
                return True
            return False
        elif trade_type == "ask":
            for i, bid in enumerate(self.bids):
                if bid.price >= price and bid.amount >= amount:
                    bid.amount -= amount
                    if bid.amount == 0:
                        del self.bids[i]
                    return True
            return False

    def display_book(self):
        print('\n')
        print("Bids:")
        for i in range(len(self.bids)):
            print("Price:", self.bids[i][2], "Amount:", decrypt(self.bids[i][3])[0])
        print("Asks:")
        for i in range(len(self.asks)):
            print("Price:", self.asks[i][2], "Amount:", decrypt(self.asks[i][3])[0])



def main():
    # Example usage
    order_book = OrderBook()

    # Adding 5 bids
    order_book.add_order("bid", 95, encrypt(5))
    order_book.add_order("bid", 90, encrypt(3))
    order_book.add_order("bid", 95, encrypt(4))
    order_book.add_order("bid", 85, encrypt(6))
    order_book.add_order("bid", 80, encrypt(2))

    # Adding 5 asks
    order_book.add_order("ask", 100, encrypt(3))
    order_book.add_order("ask", 110, encrypt(2))
    order_book.add_order("ask", 115, encrypt(5))
    order_book.add_order("ask", 120, encrypt(4))
    order_book.add_order("ask", 125, encrypt(6))

    # Displaying the order book
    order_book.display_book()

    # Executing a trade with trade type "bid", price 100 and amount 2
    result = order_book.execute_trade("bid", 100, encrypt(-3))
    print("here")
    if result:
        print("Trade executed successfully.")
    else:
        print("Not enough liquidity.")

    # Displaying the order book after trade execution
    order_book.display_book()


if __name__ == '__main__':
    main()

