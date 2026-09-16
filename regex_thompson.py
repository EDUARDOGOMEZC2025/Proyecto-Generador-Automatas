import os
import graphviz

class State:
    def __init__(self, id_val):
        self.id = id_val
        self.transitions = {} # símbolo -> lista de estados destino

    def add_transition(self, symbol, state):
        if symbol not in self.transitions:
            self.transitions[symbol] = []
        self.transitions[symbol].append(state)

class NFA:
    def __init__(self, start_state, accept_state):
        self.start_state = start_state
        self.accept_state = accept_state

class ThompsonBuilder:
    EPSILON = 'ε'  # Constante requerida por los parsers y constructores
    _id_counter = 0

    @classmethod
    def _new_state(cls):
        st = cls._id_counter
        cls._id_counter += 1
        return State(st)

    @classmethod
    def _get_val(cls, token):
        # Extrae el valor string de un objeto Token o lo convierte si ya es string
        return token.value if hasattr(token, 'value') else str(token)

    @classmethod
    def build_from_postfix(cls, postfix_tokens):
        cls._id_counter = 0
        stack = []

        for raw_token in postfix_tokens:
            token = cls._get_val(raw_token)
            
            if token.isalnum() or token in ['a', 'b', 'c', 'd', '0', '1']:
                s1 = cls._new_state()
                s2 = cls._new_state()
                s1.add_transition(token, s2)
                stack.append(NFA(s1, s2))
            elif token == '.':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                nfa1.accept_state.add_transition(cls.EPSILON, nfa2.start_state)
                stack.append(NFA(nfa1.start_state, nfa2.accept_state))
            elif token == '|':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                s_start = cls._new_state()
                s_accept = cls._new_state()
                s_start.add_transition(cls.EPSILON, nfa1.start_state)
                s_start.add_transition(cls.EPSILON, nfa2.start_state)
                nfa1.accept_state.add_transition(cls.EPSILON, s_accept)
                nfa2.accept_state.add_transition(cls.EPSILON, s_accept)
                stack.append(NFA(s_start, s_accept))
            elif token == '*':
                nfa = stack.pop()
                s_start = cls._new_state()
                s_accept = cls._new_state()
                s_start.add_transition(cls.EPSILON, nfa.start_state)
                s_start.add_transition(cls.EPSILON, s_accept)
                nfa.accept_state.add_transition(cls.EPSILON, nfa.start_state)
                nfa.accept_state.add_transition(cls.EPSILON, s_accept)
                stack.append(NFA(s_start, s_accept))
            elif token == '+':
                nfa = stack.pop()
                s_start = cls._new_state()
                s_accept = cls._new_state()
                s_start.add_transition(cls.EPSILON, nfa.start_state)
                nfa.accept_state.add_transition(cls.EPSILON, nfa.start_state)
                nfa.accept_state.add_transition(cls.EPSILON, s_accept)
                stack.append(NFA(s_start, s_accept))
            elif token == '?':
                nfa = stack.pop()
                s_start = cls._new_state()
                s_accept = cls._new_state()
                s_start.add_transition(cls.EPSILON, nfa.start_state)
                s_start.add_transition(cls.EPSILON, s_accept)
                nfa.accept_state.add_transition(cls.EPSILON, s_accept)
                stack.append(NFA(s_start, s_accept))

        return stack.pop() if stack else None

    @classmethod
    def build_with_steps(cls, postfix_tokens):
        cls._id_counter = 0
        stack = []
        steps = []
        
        for idx, raw_token in enumerate(postfix_tokens):
            token = cls._get_val(raw_token)
            
            if token.isalnum() or token in ['a', 'b', 'c', 'd', '0', '1']:
                s1 = cls._new_state()
                s2 = cls._new_state()
                s1.add_transition(token, s2)
                stack.append(NFA(s1, s2))
            elif token == '.':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                nfa1.accept_state.add_transition(cls.EPSILON, nfa2.start_state)
                stack.append(NFA(nfa1.start_state, nfa2.accept_state))
            elif token == '|':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                s_start = cls._new_state()
                s_accept = cls._new_state()
                s_start.add_transition(cls.EPSILON, nfa1.start_state)
                s_start.add_transition(cls.EPSILON, nfa2.start_state)
                nfa1.accept_state.add_transition(cls.EPSILON, s_accept)
                nfa2.accept_state.add_transition(cls.EPSILON, s_accept)
                stack.append(NFA(s_start, s_accept))
            elif token == '*':
                nfa = stack.pop()
                s_start = cls._new_state()
                s_accept = cls._new_state()
                s_start.add_transition(cls.EPSILON, nfa.start_state)
                s_start.add_transition(cls.EPSILON, s_accept)
                nfa.accept_state.add_transition(cls.EPSILON, nfa.start_state)
                nfa.accept_state.add_transition(cls.EPSILON, s_accept)
                stack.append(NFA(s_start, s_accept))
            
            if stack:
                fname = f"step_{idx}"
                cls.draw_nfa(stack[-1], fname)
                steps.append(f"{fname}.png")
        return steps

    @classmethod
    def draw_nfa(cls, nfa, filename="nfa"):
        if not nfa: return

        dot = graphviz.Digraph(comment="AFN Thompson", format="png")
        dot.attr(rankdir='LR')

        visited = set()
        queue = [nfa.start_state]

        while queue:
            current = queue.pop(0)
            if current.id in visited: continue
            visited.add(current.id)

            # Estilo idéntico al que usas en el DFA
            if current.id == nfa.accept_state.id and current.id == nfa.start_state.id:
                dot.node(str(current.id), shape='doublecircle', style='filled', fillcolor='#BBDEFB')
            elif current.id == nfa.accept_state.id:
                dot.node(str(current.id), shape='doublecircle', style='filled', fillcolor='#C8E6C9')
            elif current.id == nfa.start_state.id:
                dot.node(str(current.id), shape='circle', style='filled', fillcolor='#BBDEFB')
            else:
                dot.node(str(current.id), shape='circle')

            for symbol, targets in current.transitions.items():
                for target in targets:
                    dot.edge(str(current.id), str(target.id), label=str(symbol))
                    if target.id not in visited:
                        queue.append(target)

        # Flecha de inicio externa idéntica al DFA
        dot.node('', shape='none', width='0', height='0')
        dot.edge('', str(nfa.start_state.id))

        dot.render(filename, cleanup=True)