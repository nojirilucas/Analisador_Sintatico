from enum import Enum

class TokenType(Enum):
    PALAVRA_RESERVADA = "PalavraReservada"
    IDENTIFICADOR = "Identificador"
    NUMERO = "Numero"
    REAL = "Real"
    STRING = "String"
    CARACTERE = "Caractere"
    OPERADOR = "Operador"
    SIMBOLO = "Simbolo"
    COMENTARIO = "Comentario"
    ERRO = "Erro"

class Token:
    def __init__(self, tipo, valor, linha):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha

    def __str__(self):
        return f"{self.tipo.value} -> \"{self.valor}\" (linha {self.linha})"
