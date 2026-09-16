import os
os.environ["PATH"] += os.pathsep + r'C:\Program Files\Graphviz\bin'

import graphviz
from regex_lexer import TokenType, Token

class Node:
    def __init__(self, value: str, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

class RegexParser:
    PRECEDENCE = {
        TokenType.KLEENE: 3,
        TokenType.PLUS: 3,
        TokenType.QUESTION: 3,
        TokenType.CONCAT: 2,
        TokenType.UNION: 1
    }

    @staticmethod
    def to_postfix(tokens: list[Token]) -> list[Token]:
        output = []
        stack = []

        for token in tokens:
            if token.type == TokenType.SYMBOL:
                output.append(token)
            elif token.type == TokenType.LPAREN:
                stack.append(token)
            elif token.type == TokenType.RPAREN:
                while stack and stack[-1].type != TokenType.LPAREN:
                    output.append(stack.pop())
                if stack:
                    stack.pop()
            else:
                while (stack and stack[-1].type != TokenType.LPAREN and
                       RegexParser.PRECEDENCE.get(stack[-1].type, 0) >= RegexParser.PRECEDENCE.get(token.type, 0)):
                    output.append(stack.pop())
                stack.append(token)

        while stack:
            output.append(stack.pop())

        return output

    @staticmethod
    def build_tree(postfix_tokens: list[Token]) -> Node:
        stack = []

        for token in postfix_tokens:
            if token.type == TokenType.SYMBOL:
                stack.append(Node(token.value))
            elif token.type in {TokenType.KLEENE, TokenType.PLUS, TokenType.QUESTION}:
                child = stack.pop() if stack else None
                stack.append(Node(token.value, left=child))
            elif token.type in {TokenType.CONCAT, TokenType.UNION}:
                right = stack.pop() if stack else None
                left = stack.pop() if stack else None
                stack.append(Node(token.value, left=left, right=right))

        return stack[0] if stack else None

    @staticmethod
    def draw_tree(root: Node, filename: str = "arbol_sintactico"):
        dot = graphviz.Digraph(comment="Árbol Sintáctico", format="png")
        dot.attr(rankdir='TB')
        dot.attr('node', shape='circle', style='filled', fillcolor='#E3F2FD', fontname='Helvetica')

        counter = 0

        def add_nodes(node):
            nonlocal counter
            if not node:
                return None
            
            node_id = f"node_{counter}"
            counter += 1
            
            # Escapar barras invertidas para Graphviz
            clean_val = str(node.value).replace('\\', '\\\\')
            dot.node(node_id, clean_val)

            if node.left:
                left_id = add_nodes(node.left)
                dot.edge(node_id, left_id)
            if node.right:
                right_id = add_nodes(node.right)
                dot.edge(node_id, right_id)

            return node_id

        add_nodes(root)
        dot.render(filename, cleanup=True)