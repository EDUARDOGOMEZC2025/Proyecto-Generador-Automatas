import os
os.environ["PATH"] += os.pathsep + r'C:\Program Files\Graphviz\bin'

import graphviz
from collections import deque
from regex_thompson import NFA, State, ThompsonBuilder


class DFAState:
    _id_counter = 0

    def __init__(self, nfa_states: set):
        self.id = DFAState._id_counter
        DFAState._id_counter += 1
        self.nfa_states = nfa_states  # Conjunto de estados AFN que representa
        self.transitions = {}         # símbolo -> DFAState
        self.is_accept = False

    @classmethod
    def reset_counter(cls):
        cls._id_counter = 0


class DFA:
    def __init__(self, start_state: DFAState, states: list[DFAState], alphabet: set):
        self.start_state = start_state
        self.states = states
        self.alphabet = alphabet


class DFABuilder:

    @staticmethod
    def get_epsilon_closure(states: set) -> set:
        """Calcula la ε-cerradura para un conjunto de estados del AFN."""
        closure = set(states)
        stack = list(states)

        while stack:
            state = stack.pop()
            if ThompsonBuilder.EPSILON in state.transitions:
                for next_state in state.transitions[ThompsonBuilder.EPSILON]:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)

        return closure

    @staticmethod
    def get_move(states: set, symbol: str) -> set:
        """Calcula el conjunto de estados alcanzables moviéndose con un símbolo."""
        reachable = set()
        for state in states:
            if symbol in state.transitions:
                for next_state in state.transitions[symbol]:
                    reachable.add(next_state)
        return reachable

    @staticmethod
    def build_from_nfa(nfa: NFA) -> DFA:
        """Convierte un AFN a AFD utilizando la Construcción de Subconjuntos."""
        DFAState.reset_counter()

        # 1. Obtener el alfabeto (excluyendo ε)
        alphabet = set()
        visited_nfa = set()

        def extract_alphabet(state: State):
            if state in visited_nfa:
                return
            visited_nfa.add(state)
            for symbol, next_states in state.transitions.items():
                if symbol != ThompsonBuilder.EPSILON:
                    alphabet.add(symbol)
                for next_state in next_states:
                    extract_alphabet(next_state)

        extract_alphabet(nfa.start_state)

        # 2. Estado inicial del AFD = ε-cerradura(estado_inicial_AFN)
        initial_closure = DFABuilder.get_epsilon_closure({nfa.start_state})
        start_dfa_state = DFAState(initial_closure)
        if nfa.accept_state in initial_closure:
            start_dfa_state.is_accept = True

        dfa_states = [start_dfa_state]
        unmarked_states = deque([start_dfa_state])

        state_mapping = {frozenset(initial_closure): start_dfa_state}

        # 3. Algoritmo de Subconjuntos
        while unmarked_states:
            current_dfa_state = unmarked_states.popleft()

            for symbol in sorted(alphabet):
                move_result = DFABuilder.get_move(current_dfa_state.nfa_states, symbol)
                closure_result = DFABuilder.get_epsilon_closure(move_result)

                if not closure_result:
                    continue

                frozen_closure = frozenset(closure_result)

                if frozen_closure not in state_mapping:
                    new_dfa_state = DFAState(closure_result)
                    if nfa.accept_state in closure_result:
                        new_dfa_state.is_accept = True

                    state_mapping[frozen_closure] = new_dfa_state
                    dfa_states.append(new_dfa_state)
                    unmarked_states.append(new_dfa_state)

                current_dfa_state.transitions[symbol] = state_mapping[frozen_closure]

        return DFA(start_dfa_state, dfa_states, alphabet)

    @staticmethod
    def draw_dfa(dfa: DFA, filename: str = "afd_output"):
        """Genera el gráfico del AFD usando Graphviz y lo guarda como PNG."""
        dot = graphviz.Digraph(comment="AFD Subconjuntos", format="png")
        dot.attr(rankdir='LR')

        for state in dfa.states:
            if state.is_accept:
                dot.node(str(state.id), shape='doublecircle', style='filled', fillcolor='#C8E6C9')
            elif state == dfa.start_state:
                dot.node(str(state.id), shape='circle', style='filled', fillcolor='#BBDEFB')
            else:
                dot.node(str(state.id), shape='circle')

            for symbol, next_state in state.transitions.items():
                dot.edge(str(state.id), str(next_state.id), label=str(symbol))

        dot.node('', shape='none', width='0', height='0')
        dot.edge('', str(dfa.start_state.id))

        dot.render(filename, cleanup=True)