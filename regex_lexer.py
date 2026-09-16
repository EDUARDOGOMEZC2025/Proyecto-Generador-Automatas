from enum import Enum, auto

class TokenType(Enum):
    SYMBOL = auto()      # Cualquier símbolo del alfabeto
    UNION = auto()       # '|'
    CONCAT = auto()      # '.'
    KLEENE = auto()      # '*'
    PLUS = auto()        # '+'
    QUESTION = auto()    # '?'
    LPAREN = auto()      # '('
    RPAREN = auto()      # ')'

class Token:
    def __init__(self, type_: TokenType, value: str):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}')"

class RegexLexer:
    OPERATORS = {
        '|': TokenType.UNION,
        '.': TokenType.CONCAT,
        '*': TokenType.KLEENE,
        '+': TokenType.PLUS,
        '?': TokenType.QUESTION,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN
    }

    @staticmethod
    def tokenize(expression: str) -> list[Token]:
        tokens = []
        for char in expression:
            if char.isspace():
                continue
            elif char in RegexLexer.OPERATORS:
                tokens.append(Token(RegexLexer.OPERATORS[char], char))
            else:
                tokens.append(Token(TokenType.SYMBOL, char))
        return tokens

    @staticmethod
    def insert_explicit_concatenation(tokens: list[Token]) -> list[Token]:
        if not tokens:
            return []

        result = []
        for i in range(len(tokens) - 1):
            curr_token = tokens[i]
            next_token = tokens[i + 1]

            result.append(curr_token)

            can_end = curr_token.type in {
                TokenType.SYMBOL, TokenType.RPAREN, 
                TokenType.KLEENE, TokenType.PLUS, TokenType.QUESTION
            }

            can_start = next_token.type in {TokenType.SYMBOL, TokenType.LPAREN}

            if can_end and can_start and next_token.type != TokenType.CONCAT:
                result.append(Token(TokenType.CONCAT, '.'))

        result.append(tokens[-1])
        return result

    @staticmethod
    def validate(tokens: list[Token]) -> tuple[bool, str]:
        if not tokens:
            return False, "La expresión está completamente vacía."

        balance = 0
        for i, token in enumerate(tokens):
            if token.type == TokenType.LPAREN:
                balance += 1
            elif token.type == TokenType.RPAREN:
                balance -= 1
                if balance < 0:
                    return False, "Error sintáctico: Paréntesis de cierre ')' sin apertura previa."

            if token.type == TokenType.UNION:
                if i == 0 or i == len(tokens) - 1:
                    return False, "Error sintáctico: Operador '|' no puede estar al inicio o al final."
                if tokens[i - 1].type in {TokenType.UNION, TokenType.LPAREN, TokenType.CONCAT}:
                    return False, "Error sintáctico: Operador '|' carece de expresión válida a la izquierda."
                if tokens[i + 1].type in {TokenType.UNION, TokenType.RPAREN, TokenType.KLEENE, TokenType.PLUS, TokenType.QUESTION, TokenType.CONCAT}:
                    return False, "Error sintáctico: Operador '|' carece de expresión válida a la derecha."

            if token.type == TokenType.CONCAT:
                if i == 0 or i == len(tokens) - 1:
                    return False, "Error sintáctico: Operador '.' no puede estar al inicio o al final."
                if tokens[i - 1].type in {TokenType.UNION, TokenType.LPAREN, TokenType.CONCAT}:
                    return False, "Error sintáctico: Operador '.' carece de operando a la izquierda."
                if tokens[i + 1].type in {TokenType.UNION, TokenType.RPAREN, TokenType.KLEENE, TokenType.PLUS, TokenType.QUESTION, TokenType.CONCAT}:
                    return False, "Error sintáctico: Operador '.' carece de operando a la derecha."

            if token.type in {TokenType.KLEENE, TokenType.PLUS, TokenType.QUESTION}:
                if i == 0:
                    return False, f"Error sintáctico: El operador '{token.value}' requiere una expresión previa."
                if tokens[i - 1].type in {TokenType.LPAREN, TokenType.UNION, TokenType.CONCAT}:
                    return False, f"Error sintáctico: El operador '{token.value}' no tiene una expresión válida a la izquierda."

        if balance > 0:
            return False, f"Error sintáctico: Falta cerrar {balance} paréntesis '('."

        return True, "Expresión válida."