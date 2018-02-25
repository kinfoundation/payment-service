from collections import namedtuple
from datetime import datetime
from schematics import Model
from schematics.types import StringType, IntType, DateType


Memo = namedtuple('Memo', ['app_id', 'order_id'])
db = {}


class WalletAddress(Model):
    wallet_address = StringType()
    app_id = StringType()


class Wallet(Model):
    wallet_address = StringType()
    kin_balance = IntType()
    native_balance = IntType()


class Payment(Model):
    amount = IntType()
    app_id = StringType()
    order_id = StringType()
    wallet_address = StringType()


class Order(Model):
    id = StringType()
    app_id = StringType()
    transaction_id = StringType()
    recipient_address = StringType()
    sender_address = StringType()
    amount = IntType()
    timestamp = DateType(default=datetime.utcnow())

    @classmethod
    def from_blockchain(cls, data):
        t = Order()
        t.id = cls.parse_memo(data.memo).order_id
        t.app_id = cls.parse_memo(data.memo).app_id
        t.transaction_id = data.operations[0].id
        t.sender_address = data.operations[0].from_address
        t.recipient_address = data.operations[0].to_address
        t.amount = int(data.operations[0].amount)
        return t

    @classmethod
    def parse_memo(cls, memo):
        version, app_id, order_id = memo.split('-')
        return Memo(app_id, order_id)

    @classmethod
    def create_memo(cls, app_id, order_id):
        """serialize args to the memo string."""
        return '1-{}-{}'.format(app_id, order_id)
   
    @classmethod
    def get_by_transaction_id(cls, tx_id):
        for t in db.values():
            if t.transaction_id == tx_id:
                return Order(t)
        raise KeyError(tx_id)

    @classmethod
    def get(cls, order_id):
        return Order(db[order_id])

    def save(self):
        db[self.id] = self.to_primitive()
