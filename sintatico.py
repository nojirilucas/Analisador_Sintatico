from tokens import TokenType

class SyntaxError(Exception):
    """Exceção customizada para erros de sintaxe."""
    def __init__(self, message, linha=None):
        super().__init__(message)
        self.linha = linha

    def __str__(self):
        if self.linha:
            return f"Syntax Error at line {self.linha}: {super().__str__()}"
        return f"Syntax Error: {super().__str__()}"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        # Define current_token se houver tokens, senão None
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _advance(self):
        """Avança para o próximo token."""
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _consume(self, expected_type, expected_value=None):
        """
        Consome o token atual se ele corresponder ao tipo e valor esperados.
        Avança para o próximo token. Caso contrário, levanta SyntaxError.
        """
        token = self.current_token
        
        if token is None:
            expected_descr = f"'{expected_value}' ({expected_type.value})" if expected_value else expected_type.value
            raise SyntaxError(f"Unexpected end of input. Expected {expected_descr}.")

        linha_atual = token.linha

        if token.tipo != expected_type:
            raise SyntaxError(f"Expected token type {expected_type.value}, got {token.tipo.value} ('{token.valor}')", linha_atual)

        if expected_value is not None and token.valor != expected_value:
            raise SyntaxError(f"Expected token value '{expected_value}', got '{token.valor}' for type {token.tipo.value}", linha_atual)
        
        self._advance()
        return token

    def parse_programa(self):
        self.parse_declaracao_funcao()
        if self.current_token is not None:
            raise SyntaxError(f"Unexpected token '{self.current_token.valor}' after program completion.", self.current_token.linha)

    def parse_declaracao_funcao(self):
        self.parse_tipo()
        self._consume(TokenType.IDENTIFICADOR)
        self._consume(TokenType.SIMBOLO, '(')
        self._consume(TokenType.SIMBOLO, ')')
        self._consume(TokenType.SIMBOLO, '{') 
        self.parse_lista_comandos()
        self._consume(TokenType.SIMBOLO, '}')

    def parse_tipo(self):
        token = self.current_token
        if token and token.tipo == TokenType.PALAVRA_RESERVADA and token.valor in {"int", "real", "char"}:
            self._consume(TokenType.PALAVRA_RESERVADA, token.valor)
        else:
            linha = token.linha if token else "EOF"
            valor = token.valor if token else "None"
            raise SyntaxError(f"Expected type (int, real, char), got '{valor}'", linha)

    def parse_lista_comandos(self):
        while self.current_token and not (self.current_token.tipo == TokenType.SIMBOLO and self.current_token.valor == '}'):
            self.parse_comando()

    def parse_comando(self):
        
        token = self.current_token
        if not token:
             raise SyntaxError("Unexpected end of input expecting a command.")

        if token.tipo == TokenType.PALAVRA_RESERVADA:
            if token.valor == "return":
                self.parse_comando_retorno()
            elif token.valor in {"int", "real", "char"}:
                self.parse_declaracao_variavel()
            else:
                raise SyntaxError(f"Unexpected reserved word '{token.valor}' at start of a command.", token.linha)
        elif token.tipo == TokenType.IDENTIFICADOR:
            if self.pos + 1 < len(self.tokens):
                next_token = self.tokens[self.pos+1]
                if next_token.tipo == TokenType.SIMBOLO and next_token.valor == '=':
                    self.parse_atribuicao()
                elif next_token.tipo == TokenType.SIMBOLO and next_token.valor == '(':
                    self.parse_chamada_funcao_stmt()
                else:
                    raise SyntaxError(f"After identifier '{token.valor}', expected '=' or '(' but got '{next_token.valor}'", next_token.linha)
            else:
                raise SyntaxError(f"Unexpected end of input after identifier '{token.valor}'. Expected assignment or function call.", token.linha)
        else:
            raise SyntaxError(f"Unexpected token '{token.valor}' to start a command.", token.linha)

    def parse_declaracao_variavel(self):
        self.parse_tipo()
        self._consume(TokenType.IDENTIFICADOR)
        if self.current_token and self.current_token.tipo == TokenType.SIMBOLO and self.current_token.valor == '=':
            self._consume(TokenType.SIMBOLO, '=')
            self.parse_expressao()
        self._consume(TokenType.SIMBOLO, ';')

    def parse_atribuicao(self):
        self._consume(TokenType.IDENTIFICADOR)
        self._consume(TokenType.SIMBOLO, '=')
        self.parse_expressao()
        self._consume(TokenType.SIMBOLO, ';')

    def parse_chamada_funcao_stmt(self):
        # <chamada_funcao_stmt> ::= IDENTIFICADOR LPAREN <lista_argumentos_opcional> RPAREN SEMI
        self._consume(TokenType.IDENTIFICADOR) # Nome da função
        self._consume(TokenType.SIMBOLO, '(')    # LPAREN
        self.parse_lista_argumentos_opcional()
        self._consume(TokenType.SIMBOLO, ')')    # RPAREN
        self._consume(TokenType.SIMBOLO, ';')    # SEMI
        
    def parse_lista_argumentos_opcional(self):
        if self.current_token and not (self.current_token.tipo == TokenType.SIMBOLO and self.current_token.valor == ')'):
            self.parse_lista_argumentos()

    def parse_lista_argumentos(self):
        self.parse_expressao() 

    def parse_comando_retorno(self):
        self._consume(TokenType.PALAVRA_RESERVADA, "return")
        self.parse_expressao()
        self._consume(TokenType.SIMBOLO, ';')

    def parse_expressao(self):
        self.parse_termo()
        while self.current_token and self.current_token.tipo == TokenType.SIMBOLO and self.current_token.valor == '+':
            self._consume(TokenType.SIMBOLO, '+')
            self.parse_termo()

    def parse_termo(self):
        token = self.current_token
        if not token:
            raise SyntaxError("Unexpected end of input expecting a term.")

        if token.tipo == TokenType.IDENTIFICADOR:
            self._consume(TokenType.IDENTIFICADOR)
        elif token.tipo == TokenType.NUMERO:
            self._consume(TokenType.NUMERO)
        elif token.tipo == TokenType.REAL:
            self._consume(TokenType.REAL)
        elif token.tipo == TokenType.STRING:
            self._consume(TokenType.STRING)
        elif token.tipo == TokenType.CARACTERE:
            self._consume(TokenType.CARACTERE)
        else:
            raise SyntaxError(f"Expected identifier, number, real, string, or character, got '{token.valor}'", token.linha)

# Bloco para testar o parser
if __name__ == "__main__":
    try:
        from analisador import analisar_arquivo 
    except ImportError:
        print("Erro: Não foi possível encontrar 'analisador.py'. Certifique-se de que está no diretório correto.")
        exit(1)

    nome_arquivo_teste = "teste_limpo.txt"
    
    print(f"Analisando arquivo: {nome_arquivo_teste}")
    try:
        with open(nome_arquivo_teste, "w", encoding="utf-8") as f_example:
             f_example.write("int main() {\n")
             f_example.write("    int valor = 10 + 20;\n")
             f_example.write("    real saldo = 150.75;\n")
             f_example.write("    char inicial = 'J';\n")
             f_example.write("    printf(\"Teste\");\n")
             f_example.write("    valor = valor + 5;\n")
             f_example.write("    return 0;\n")
             f_example.write("}\n")
        print(f"Arquivo de exemplo '{nome_arquivo_teste}' criado/sobrescrito para teste.")

        raw_tokens = analisar_arquivo(nome_arquivo_teste)
    except FileNotFoundError:
        print(f"Erro: Arquivo de teste '{nome_arquivo_teste}' não encontrado.")
        exit(1)
    except Exception as e:
        print(f"Erro durante a análise léxica: {e}")
        exit(1)

    tokens_para_parser = []
    tem_erros_lexicos = False
    for t in raw_tokens:
        if t.tipo == TokenType.ERRO:
            print(f"Erro Léxico (do analisador.py): \"{t.valor}\" (linha {t.linha}). Análise sintática abortada.")
            tem_erros_lexicos = True
            break
        if t.tipo != TokenType.COMENTARIO:
            tokens_para_parser.append(t)

    if not tem_erros_lexicos and tokens_para_parser:
        print(f"\nTokens para o parser (total: {len(tokens_para_parser)}):")
        
        print("\nIniciando análise sintática...")
        parser = Parser(tokens_para_parser)
        try:
            parser.parse_programa()
            print("\nAnálise sintática concluída com sucesso!")
        except SyntaxError as e:
            print(f"\n{e}")
        except Exception as e:
            print(f"\nErro inesperado durante o parsing: {e}")

    elif not tokens_para_parser and not tem_erros_lexicos:
        print("Nenhum token para analisar (arquivo vazio ou apenas comentários).")
    else:
        print("Não foi possível prosseguir para a análise sintática devido a erros léxicos ou ausência de tokens.")
