# lnd-python-sdk
A Python SDK for interacting with the lnd lightning network client from lightning labs (https://github.com/lightningnetwork/lnd)

Follow the instructions here: https://github.com/lightningnetwork/lnd/tree/master/docker

Once you have a docker containers setup for alice and bob and have mined some blocks you can use the python interface provided to simplify the interactions between them.

Example

```python
# assuming your docker containers are named "alice" and "bob"
from nodes import Node, client

alice = Node(client.containers.get('alice'))
bob = Node(client.containers.get('bob'))

alice.create_address()
bob.create_address()

# connect to bob and fund a payment channel
alice.connect(bob)
alice.open_channel(bob, 500_000)

# lets get paid
invoice = bob.add_invoice(200_000, memo='pay me')
alice.pay(invoice)

print(bob.wallet_balance)
print(alice.wallet_balance)
```

