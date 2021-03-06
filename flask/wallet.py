from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii


class Wallet:
    """Creates, loads and holds private and public keys. Manages transaction
    signing and verification."""

    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None
        self.node_id = node_id

    def create_keys(self):
        """Create a new pair of Public and Private Key."""
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def save_keys(self):
        """Save the key to a file (default: wallet-5000.txt)."""
        if self.public_key is not None and self.private_key is not None:
            try:
                with open('wallet-{}.txt'.format(self.node_id), mode='w') as \
                        file:
                    file.write(self.public_key)
                    file.write('\n')
                    file.write(self.private_key)
                return True
            except(IOError, IndexError):
                print("Saving wallet failed!!!!")
                return False

    def load_keys(self):
        """Load the key from a file (default: wallet-5000.txt)."""
        try:
            with open('wallet-{}.txt'.format(self.node_id), mode='r') as file:
                keys = file.readlines()
                public_key = keys[0][:-1]
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
            return True
        except(IOError, IndexError):
            print("Loading wallet failed!!!")
            return False

    def generate_keys(self):
        """Generate a new pair of private and public key."""
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii.hexlify(private_key.exportKey(format='DER')).
                decode('ascii'),
                binascii.hexlify(public_key.exportKey(format='DER')).
                decode('ascii'))

    def sign_transaction(self, sender, recipient, amount):
        """Sign a transaction and return the signature.

        Arguments:
            :sender: The sender of the transaction.
            :recipient: The recipient of the transaction.
            :amount: The amount of the transaction.
        """
        # Converting back to 'binary' from string (we converted above).
        signer = PKCS1_v1_5.new(RSA.importKey(
            binascii.unhexlify(self.private_key)))
        # Converting to string and enconding.
        new_hash = SHA256.new(
            (str(sender) + str(recipient) + str(amount)).encode('utf8'))
        signature = signer.sign(new_hash)
        # Converting back to 'string'
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction(transaction):
        """Verify the signature of the transaction.

        Arguments:
            transaction: The transaction that should be verified.
        """
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        new_hash = SHA256.new(
            (str(transaction.sender) + str(transaction.recipient) +
             str(transaction.amount)).encode('utf8'))
        return (verifier.verify(new_hash, binascii.
                                unhexlify(transaction.signature)))
