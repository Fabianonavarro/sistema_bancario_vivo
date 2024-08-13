import textwrap
from abc import ABC, abstractmethod
from datetime import datetime
from cpf_cnpj import CPF

date = datetime.now()

class Cliente:
    """Representa um cliente do banco."""
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        """Realiza uma transação em uma conta."""
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        """Adiciona uma conta à lista de contas do cliente."""
        self.contas.append(conta)


class PessoaFisica(Cliente):
    """Representa um cliente pessoa física."""
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    """Representa uma conta bancária genérica."""
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        """Cria uma nova conta para o cliente."""
        return cls(numero, cliente)

    @property
    def saldo(self):
        """Retorna o saldo da conta."""
        return self._saldo

    @property
    def numero(self):
        """Retorna o número da conta."""
        return self._numero

    @property
    def agencia(self):
        """Retorna o código da agência da conta."""
        return self._agencia

    @property
    def cliente(self):
        """Retorna o cliente da conta."""
        return self._cliente

    @property
    def historico(self):
        """Retorna o histórico de transações da conta."""
        return self._historico

    def sacar(self, valor):
        """Realiza um saque da conta."""
        saldo = self.saldo
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        if valor > saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        """Realiza um depósito na conta."""
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class ContaCorrente(Conta):
    """Representa uma conta corrente com limites e saques controlados."""
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        """Realiza um saque da conta corrente com controle de limite e saques."""
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        if valor > self._limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
            return False

        if numero_saques >= self._limite_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
            return False

        return super().sacar(valor)

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
            Limite:\t\tR$ {self._limite:.2f}
        """


class Historico:
    """Armazena o histórico de transações de uma conta."""
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        """Retorna a lista de transações."""
        return self._transacoes

    def adicionar_transacao(self, transacao):
        """Adiciona uma transação ao histórico."""
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": date.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )


class Transacao(ABC):
    """Classe base para transações."""
    @property
    @abstractmethod
    def valor(self):
        """Retorna o valor da transação."""
        pass

    @abstractmethod
    def registrar(self, conta):
        """Registra a transação na conta."""
        pass


class Saque(Transacao):
    """Representa uma transação de saque."""
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        """Retorna o valor do saque."""
        return self._valor

    def registrar(self, conta):
        """Registra o saque na conta."""
        sucesso = conta.sacar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    """Representa uma transação de depósito."""
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        """Retorna o valor do depósito."""
        return self._valor

    def registrar(self, conta):
        """Registra o depósito na conta."""
        sucesso = conta.depositar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)


def remover_mascara(cpf):
    """Remove a máscara do CPF."""
    return ''.join(filter(str.isdigit, cpf))


def validar_cpf(cpf):
    """Valida o CPF utilizando a biblioteca cpf_cnpj."""
    cpf = remover_mascara(cpf)
    return CPF(cpf).validate()


def menu():
    """Exibe o menu principal do sistema bancário."""
    menu_texto = """\n   
    Seja bem-vindo ao sistema bancário VIVO

    ================ MENU ================
    Depositar               Opção [1] 
    Sacar                   Opção [2] 
    Extrato                 Opção [3] 
    Nova conta              Opção [4]   
    Listar contas           Opção [5]
    Novo usuário            Opção [6]
    Sair                    Opção [0] 

    ---------------------------------
    => Escolha uma opção _> """
    return input(textwrap.dedent(menu_texto))


def filtrar_cliente(cpf, clientes):
    """Filtra um cliente pelo CPF."""
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def escolher_conta(cliente):
    """Permite ao cliente escolher uma conta se tiver mais de uma."""
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None

    print("\nEscolha a conta:")
    for i, conta in enumerate(cliente.contas):
        print(f"{i + 1}: {conta.numero} - Saldo: R$ {conta.saldo:.2f}")

    try:
        escolha = int(input("Digite o número da conta: "))
        if 1 <= escolha <= len(cliente.contas):
            return cliente.contas[escolha - 1]
    except ValueError:
        pass

    print("\n@@@ Escolha inválida! @@@")
    return None


def depositar(clientes):
    """Realiza um depósito em uma conta do cliente."""
    cpf = input("Informe o CPF do cliente (ex: 123.456.789-00): ").strip()
    cpf = remover_mascara(cpf)

    if not validar_cpf(cpf):
        print("\n@@@ CPF inválido! @@@")
        return

    cliente = filtrar_cliente(cpf, clientes)
    if cliente is None:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = input("Informe o valor do depósito: ")
    try:
        valor = float(valor)
    except ValueError:
        print("\n@@@ Valor inválido! @@@")
        return

    transacao = Deposito(valor)
    conta = escolher_conta(cliente)
    if conta:
        cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    """Realiza um saque em uma conta do cliente."""
    cpf = input("Informe o CPF do cliente (ex: 123.456.789-00): ").strip()
    cpf = remover_mascara(cpf)

    if not validar_cpf(cpf):
        print("\n@@@ CPF inválido! @@@")
        return

    cliente = filtrar_cliente(cpf, clientes)
    if cliente is None:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = input("Informe o valor do saque: ")
    try:
        valor = float(valor)
    except ValueError:
        print("\n@@@ Valor inválido! @@@")
        return

    transacao = Saque(valor)
    conta = escolher_conta(cliente)
    if conta:
        cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    """Exibe o extrato de uma conta do cliente."""
    cpf = input("Informe o CPF do cliente (ex: 123.456.789-00): ").strip()
    cpf = remover_mascara(cpf)

    if not validar_cpf(cpf):
        print("\n@@@ CPF inválido! @@@")
        return

    cliente = filtrar_cliente(cpf, clientes)
    if cliente is None:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = escolher_conta(cliente)
    if conta:
        print("\n================ EXTRATO ================")
        transacoes = conta.historico.transacoes

        extrato = ""
        if not transacoes:
            extrato = "Não foram realizadas movimentações."
        else:
            for transacao in transacoes:
                extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f} em {transacao['data']}"

        print(extrato)
        print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
        print("==========================================")


def criar_cliente(clientes):
    """Cria um novo cliente."""
    cpf = input("Informe o CPF do cliente (ex: 123.456.789-00): ").strip()
    cpf = remover_mascara(cpf)

    if not validar_cpf(cpf):
        print("\n@@@ CPF inválido! @@@")
        return

    if filtrar_cliente(cpf, clientes):
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ").strip()
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ").strip()
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ").strip()

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero_conta, clientes, contas):
    """Cria uma nova conta corrente para um cliente."""
    cpf = input("Informe o CPF do cliente (ex: 123.456.789-00): ").strip()
    cpf = remover_mascara(cpf)

    if not validar_cpf(cpf):
        print("\n@@@ CPF inválido! @@@")
        return

    cliente = filtrar_cliente(cpf, clientes)
    if cliente is None:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    """Lista todas as contas existentes."""
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    """Função principal para executar o sistema bancário."""
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)
        elif opcao == "2":
            sacar(clientes)
        elif opcao == "3":
            exibir_extrato(clientes)
        elif opcao == "4":
            criar_cliente(clientes)
        elif opcao == "5":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
        elif opcao == "6":
            listar_contas(contas)
        elif opcao == "0":
            break
        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")

if __name__ == "__main__":
    main()
