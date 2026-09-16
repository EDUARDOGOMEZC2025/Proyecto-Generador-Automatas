from regex_dfa import DFAState

class DFASimulator:
    @staticmethod
    def evaluate(start_state: DFAState, input_string: str) -> bool:
        """ Evalúa si una cadena es aceptada por el AFD. """
        current_state = start_state

        for char in input_string:
            if char in current_state.transitions:
                current_state = current_state.transitions[char]
            else:
                # Transición no existente = Estado de rechazo (Pozo)
                return False

        return current_state.is_accept