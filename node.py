import json
import docker
import subprocess
client = docker.from_env()


def docker_compose(*args):
    cmd = ["docker-compose"]
    cmd.extend(list(args))
    result = subprocess.call(cmd)
    if result > 0:
        print(f'Error: {result}')
    return result


def mine_blocks(num_blocks=3):
    docker_compose(*['run', 'btcctl', 'generate', str(num_blocks)])


class Node:

    def __init__(self, container):
        self.container = container

        # set static attributes for easy lookup
        self.pub_key = self.info['identity_pubkey']
        self.ip_address = self.container.attrs['NetworkSettings']['Networks']['docker_default']['IPAddress']
        self.address = f'{self.pub_key}@{self.ip_address}'

    def _cmd(self, cmd):
        cmd = "lncli " + cmd
        result = self.container.exec_run(cmd)
        if result.exit_code == 0:
            return json.loads(result.output)
        else:
            raise Exception(f'Erorr: {result.output}')

    def create_address(self):
        result = self._cmd("newaddress np2wkh")
        self.wallet_address = result['address']

    @property
    def info(self):
        return self._cmd("getinfo")

    @property
    def peers(self):
        return self._cmd('listpeers').get('peers')

    def connect(self, node):
        return self._cmd(f'connect {node.address}')

    def open_channel(self, node, amount):
        return self._cmd(f'openchannel --node_key={node.pub_key} --local_amt={amount}')

    def pay(self, node=None, amount=None, invoice=None):
        if invoice is not None:
            self._cmd(f'sendpayment --pay_req={invoice}')
        else:
            if node is None and amount is None:
                raise ValueError('`node` and `amount` must be set if no invoice provided')
            else:
                self._cmd(f'sendpayment {node.pub_key} {amount}')

    def add_invoice(self, amount, memo=''):
        result = self._cmd(f'addinvoice {amount} --memo="{memo}"')
        return result['pay_req']

    @property
    def invoices(self):
        return self._cmd('listinvoices')['invoices']

    @property
    def wallet_balance(self):
        return self._cmd('walletbalance --witness_only=true')

    @property
    def channel_balance(self):
        return self._cmd('channelbalance')

