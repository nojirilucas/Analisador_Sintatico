from tokens import Token, TokenType

palavras_reservadas = {"int", "real", "char", "return"}

def analisar_linha(linha, num_linha):
    tokens = []
    i = 0
    while i < len(linha):
        c = linha[i]

        if c.isspace():
            i += 1
            continue

        # Identificadores e palavras reservadas
        if c.isalpha():
            lexema = ""
            while i < len(linha) and (linha[i].isalnum() or linha[i] == '_'):
                lexema += linha[i]
                i += 1
            tipo = TokenType.PALAVRA_RESERVADA if lexema in palavras_reservadas else TokenType.IDENTIFICADOR
            tokens.append(Token(tipo, lexema, num_linha))

        # Números inteiros ou reais
        elif c.isdigit():
            num = ""
            ponto = False
            while i < len(linha) and (linha[i].isdigit() or linha[i] == '.'):
                if linha[i] == '.':
                    if ponto:
                        break
                    ponto = True
                num += linha[i]
                i += 1
            tokens.append(Token(TokenType.REAL if ponto else TokenType.NUMERO, num, num_linha))

        # Strings
        elif c == '"':
            i += 1
            str_val = ""
            while i < len(linha) and linha[i] != '"':
                str_val += linha[i]
                i += 1
            i += 1
            tokens.append(Token(TokenType.STRING, str_val, num_linha))

        # Caracteres
        elif c == "'":
            if i + 2 < len(linha) and linha[i+2] == "'":
                tokens.append(Token(TokenType.CARACTERE, linha[i+1], num_linha))
                i += 3
            else:
                tokens.append(Token(TokenType.ERRO, linha[i:], num_linha))
                break

        # Comentários de linha
        elif c == '\\' and i+1 < len(linha) and linha[i+1] == '\\':
            tokens.append(Token(TokenType.COMENTARIO, linha[i:], num_linha))
            break

        # Símbolos
        elif c in "();{}=+":
            tokens.append(Token(TokenType.SIMBOLO, c, num_linha))
            i += 1

        else:
            tokens.append(Token(TokenType.ERRO, c, num_linha))
            i += 1

    return tokens

def analisar_arquivo(nome_arquivo):
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    todos_tokens = []
    for num, linha in enumerate(linhas, start=1):
        tokens = analisar_linha(linha, num)
        todos_tokens.extend(tokens)

    return todos_tokens

if __name__ == "__main__":
    tokens = analisar_arquivo("teste.txt")
    for t in tokens:
        print(t)
