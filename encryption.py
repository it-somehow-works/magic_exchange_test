from bfv.batch_encoder import BatchEncoder
from bfv.bfv_decryptor import BFVDecryptor
from bfv.bfv_encryptor import BFVEncryptor
from bfv.bfv_evaluator import BFVEvaluator
from bfv.bfv_key_generator import BFVKeyGenerator
from bfv.bfv_parameters import BFVParameters


class Encryption:
    def __init__(self, degree, plain_modulus, ciph_modulus):
        self.degree = degree
        self.plain_modulus = plain_modulus
        self.ciph_modulus = ciph_modulus
        self.params = BFVParameters(poly_degree=degree,
                                plain_modulus=plain_modulus,
                                ciph_modulus=ciph_modulus)
        self.key_generator = BFVKeyGenerator(self.params)
        self.public_key = self.key_generator.public_key
        self.secret_key = self.key_generator.secret_key
        self.encoder = BatchEncoder(self.params)
        self.encryptor = BFVEncryptor(self.params, self.public_key)
        self.decryptor = BFVDecryptor(self.params, self.secret_key)

    def encrypt(self, number):
        plain1 = self.encoder.encode(self.number_to_hex(number, 8))
        cipher1 = self.encryptor.encrypt(plain1)
        return cipher1

    def decrypt(self, product):
        decrypted_prod = self.decryptor.decrypt(product)
        decoded_prod = self.encoder.decode(decrypted_prod)
        return decoded_prod

    def evaluate(self, ciph1, ciph2):
        evaluator = BFVEvaluator(self.params)
        cipher_prod = evaluator.add(ciph1, ciph2)
        return cipher_prod

    def number_to_hex(self, number, degree):
        hex_list = []
        hex_str = hex(number)[2:]
        hex_list = [int(x, 16) for x in hex_str]
        hex_list = hex_list + [0] * (degree - len(hex_list))
        return hex_list

    def from_hex_to_dec(self, hex_array):
        hex_string = ''
        for digit in hex_array:
            hex_string += str(digit)
        dec_value = int(hex_string, 16)
        return dec_value
