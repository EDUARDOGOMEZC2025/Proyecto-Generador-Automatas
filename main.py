import os
import datetime
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

from regex_lexer import RegexLexer
from regex_parser import RegexParser
from regex_thompson import ThompsonBuilder, NFA, State
from regex_dfa import DFABuilder

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AutoLangIDE(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AutoLang IDE - Proyecto Generador Automatas (Grupo 1)")
        self.after(0, lambda: self.wm_state('zoomed'))
        self.configure(fg_color="#0b1329")

        # Cargar el ícono de la ventana si existe logo.png
        try:
            icon_img = Image.open("logo.png")
            self.iconphoto(False, ImageTk.PhotoImage(icon_img))
        except Exception:
            pass

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.current_nfa = None
        self.current_dfa = None
        self.thompson_steps = []
        self.current_step_idx = 0
        self.animating = False
        self.current_char_idx = 0

        self.create_header()
        self.create_sidebar()
        self.create_main_dashboard()
        self.create_footer()

    def create_header(self):
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#0b1a30", height=60)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        
        # Cargar el logotipo en el encabezado
        try:
            pil_logo = Image.open("logo.png")
            self.logo_img = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(42, 42))
            lbl_logo = ctk.CTkLabel(header, image=self.logo_img, text="")
            lbl_logo.pack(side="left", padx=(15, 5), pady=8)
        except Exception:
            pass

        lbl_title = ctk.CTkLabel(header, text="AutoLang IDE - Proyecto Generador Automatas (Grupo 1)", font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        lbl_title.pack(side="left", padx=10)

        user_info = ctk.CTkLabel(header, text="Ingeniería en Sistemas UMG", font=ctk.CTkFont(size=14, weight="bold"), text_color="#cbd5e1", justify="right")
        user_info.pack(side="right", padx=20)

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#070d1e")
        sidebar.grid(row=1, column=0, sticky="nsew")

        opts = [
            ("🏠   Inicio / Visión General", lambda: self.tabview.set("🌐 Visión General")),
            ("⚙️   Paso 1: ER y AFN (q)", lambda: self.tabview.set("🔵 Diagrama AFN (Thompson)")),
            ("🔀   Paso 2: AFN ➔ AFD (S)", lambda: self.tabview.set("🟢 Diagrama AFD y Subconjuntos")),
            ("🧪   Paso 3: Probar Cadenas", lambda: self.tabview.set("🧪 Probar Cadenas")),
        ]
        for text, cmd in opts:
            btn = ctk.CTkButton(sidebar, text=text, anchor="w", fg_color="transparent", hover_color="#1e293b", command=cmd, font=ctk.CTkFont(size=13, weight="bold"))
            btn.pack(fill="x", padx=10, pady=6)

    def create_main_dashboard(self):
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="#0f172a")
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=15, pady=10)

        top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(top_bar, text="PROYECTO: GENERADOR DE AUTOMATAS FINITOS", font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(side="left")
        
        # PANEL DE CONTROL (PASO 1)
        p1 = ctk.CTkFrame(self.main_frame, fg_color="#0f2b5c", corner_radius=8)
        p1.pack(fill="x", pady=5)
        
        p1_head = ctk.CTkFrame(p1, fg_color="#0284c7", corner_radius=0, height=35)
        p1_head.pack(fill="x")
        ctk.CTkLabel(p1_head, text="PASO 1: EXPRESION REGULAR Y CONTROLES", font=ctk.CTkFont(size=13, weight="bold"), text_color="white").pack(side="left", padx=15, pady=5)

        p1_body = ctk.CTkFrame(p1, fg_color="#0f172a", corner_radius=0)
        p1_body.pack(fill="x", padx=12, pady=12)
        p1_body.columnconfigure(0, weight=1)
        p1_body.columnconfigure(1, weight=1)

        left_ctrl_box = ctk.CTkFrame(p1_body, fg_color="transparent")
        left_ctrl_box.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(left_ctrl_box, text="Ingresa la Expresión Regular:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 4))

        box_input = ctk.CTkFrame(left_ctrl_box, fg_color="transparent")
        box_input.pack(fill="x", pady=5)

        self.entry_regex = ctk.CTkEntry(box_input, width=300, height=40, font=ctk.CTkFont(size=16))
        self.entry_regex.insert(0, "(a|b)*abb")
        self.entry_regex.pack(side="left", padx=(0, 8))

        ctk.CTkButton(box_input, text="► Generar", fg_color="#15803d", hover_color="#166534", width=95, height=40, font=ctk.CTkFont(size=13, weight="bold"), command=self.process_automatas).pack(side="left", padx=3)
        ctk.CTkButton(box_input, text="🗑 Limpiar", fg_color="#1d4ed8", width=85, height=40, font=ctk.CTkFont(size=13, weight="bold"), command=self.limpiar_todo).pack(side="left", padx=3)

        ctk.CTkLabel(left_ctrl_box, text="Ejemplos rápidos:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(8, 4))
        box_ex = ctk.CTkFrame(left_ctrl_box, fg_color="transparent")
        box_ex.pack(fill="x")

        examples = ["(a|b)*", "a+b*", "1(01)*0", "(a|b)*abb", "a(b|c)*d"]
        for ex in examples:
            btn_ex = ctk.CTkButton(box_ex, text=ex, width=65, height=28, fg_color="#1e293b", hover_color="#334155", font=ctk.CTkFont(size=11, weight="bold"),
                                   command=lambda val=ex: self.set_example(val))
            btn_ex.pack(side="left", padx=3)

        right_tupla_box = ctk.CTkFrame(p1_body, fg_color="#101622", corner_radius=8, border_width=1, border_color="#1d283a")
        right_tupla_box.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(right_tupla_box, text="✨ 5-Tupla Formal del AFD M = (Q, Σ, δ, q0, F)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38bdf8").pack(anchor="w", padx=12, pady=(8, 4))
        self.lbl_tupla = ctk.CTkLabel(right_tupla_box, text="Genera una expresión...", font=ctk.CTkFont(size=12), text_color="#c8d3e6", justify="left")
        self.lbl_tupla.pack(anchor="w", padx=12, pady=(0, 8))

        # TABVIEW PRINCIPAL
        self.tabview = ctk.CTkTabview(self.main_frame, fg_color="#0f2b5c", corner_radius=8, height=640)
        self.tabview.pack(fill="both", expand=True, pady=12)

        self.tab_all = self.tabview.add("🌐 Visión General")
        self.tab_afn = self.tabview.add("🔵 Diagrama AFN (Thompson)")
        self.tab_afd = self.tabview.add("🟢 Diagrama AFD y Subconjuntos")
        self.tab_test = self.tabview.add("🧪 Probar Cadenas")

        # 1. PESTAÑA VISIÓN GENERAL
        self.tab_all.columnconfigure((0, 1, 2), weight=1)
        self.tab_all.rowconfigure(0, weight=1)
        
        self.fig_all_afn, self.ax_all_afn = plt.subplots(figsize=(3.5, 3.5), facecolor='#0f172a')
        self.canvas_all_afn = FigureCanvasTkAgg(self.fig_all_afn, master=self.tab_all)
        self.canvas_all_afn.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.fig_all_afd, self.ax_all_afd = plt.subplots(figsize=(3.5, 3.5), facecolor='#0f172a')
        self.canvas_all_afd = FigureCanvasTkAgg(self.fig_all_afd, master=self.tab_all)
        self.canvas_all_afd.get_tk_widget().grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.fig_all_tree, self.ax_all_tree = plt.subplots(figsize=(3.5, 3.5), facecolor='#0f172a')
        self.canvas_all_tree = FigureCanvasTkAgg(self.fig_all_tree, master=self.tab_all)
        self.canvas_all_tree.get_tk_widget().grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        # 2. PESTAÑA AFN
        self.tab_afn.columnconfigure(0, weight=1)
        self.tab_afn.columnconfigure(1, weight=1)
        self.tab_afn.rowconfigure(0, weight=1)

        frame_afn_left = ctk.CTkFrame(self.tab_afn, fg_color="#0f172a")
        frame_afn_left.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(frame_afn_left, text="AFN (Estados q - Thompson)", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=6)
        
        self.fig_afn, self.ax_afn = plt.subplots(figsize=(5, 4.5), facecolor='#0f172a')
        self.canvas_afn = FigureCanvasTkAgg(self.fig_afn, master=frame_afn_left)
        self.canvas_afn.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        frame_afn_right = ctk.CTkFrame(self.tab_afn, fg_color="#1e293b")
        frame_afn_right.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(frame_afn_right, text="Construcción Paso a Paso de Thompson", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=6)
        
        self.fig_step, self.ax_step = plt.subplots(figsize=(5, 4.5), facecolor='#1e293b')
        self.canvas_step = FigureCanvasTkAgg(self.fig_step, master=frame_afn_right)
        self.canvas_step.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        th_nav = ctk.CTkFrame(frame_afn_right, fg_color="transparent")
        th_nav.pack(side="bottom", fill="x", pady=10, padx=10)
        ctk.CTkButton(th_nav, text="< Anterior", width=90, height=32, font=ctk.CTkFont(size=12, weight="bold"), command=self.prev_thompson_step).pack(side="left", padx=5)
        self.lbl_step_info = ctk.CTkLabel(th_nav, text="Paso 0 de 0", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_step_info.pack(side="left", expand=True)
        ctk.CTkButton(th_nav, text="Siguiente >", width=90, height=32, font=ctk.CTkFont(size=12, weight="bold"), command=self.next_thompson_step).pack(side="right", padx=5)

        # 3. PESTAÑA AFD
        self.tab_afd.columnconfigure(0, weight=1)
        self.tab_afd.columnconfigure(1, weight=1)
        self.tab_afd.rowconfigure(0, weight=1)

        p2_body = ctk.CTkFrame(self.tab_afd, fg_color="#0f172a")
        p2_body.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(p2_body, text="Tabla de Transiciones (Estados S)", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=12, pady=6)

        tree_frame = ctk.CTkFrame(p2_body, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("estado", "conjunto", "e_closure", "trans_a", "trans_b")
        self.tree_sub = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#1e293b", foreground="white", fieldbackground="#1e293b", rowheight=26, font=('Helvetica', 11))
        style.configure("Treeview.Heading", background="#0d233a", foreground="white", font=('Helvetica', 11, 'bold'))

        for col, title in zip(columns, ["Estado AFD (S)", "Conjunto AFN (q)", "ε-cerradura", "Transición 'a'", "Transición 'b'"]):
            self.tree_sub.heading(col, text=title)
            self.tree_sub.column(col, width=95, anchor="center")
        self.tree_sub.pack(fill="both", expand=True)

        frame_afd_graph = ctk.CTkFrame(self.tab_afd, fg_color="#0f172a")
        frame_afd_graph.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(frame_afd_graph, text="AFD (Estados S - Subconjuntos)", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=6)

        self.fig_afd, self.ax_afd = plt.subplots(figsize=(5, 4.5), facecolor='#0f172a')
        self.canvas_afd = FigureCanvasTkAgg(self.fig_afd, master=frame_afd_graph)
        self.canvas_afd.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # 4. PESTAÑA PROBAR CADENAS (GRÁFICO AMPLIADO)
        self.tab_test.columnconfigure(0, weight=1)
        self.tab_test.rowconfigure(1, weight=1)

        box_test_ctrl = ctk.CTkFrame(self.tab_test, fg_color="#0f172a", corner_radius=8)
        box_test_ctrl.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(box_test_ctrl, text="Cadena a evaluar:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=12)
        self.entry_str = ctk.CTkEntry(box_test_ctrl, width=250, height=38, font=ctk.CTkFont(size=15))
        self.entry_str.insert(0, "aabb")
        self.entry_str.pack(side="left", padx=(0, 12), pady=10)

        ctk.CTkButton(box_test_ctrl, text="► Reproducir", fg_color="#15803d", height=38, font=ctk.CTkFont(size=12, weight="bold"), command=self.reproducir_cadena).pack(side="left", padx=5)
        ctk.CTkButton(box_test_ctrl, text="⏭ Paso a Paso", fg_color="#1d4ed8", height=38, font=ctk.CTkFont(size=12, weight="bold"), command=self.paso_a_paso_cadena).pack(side="left", padx=5)
        ctk.CTkButton(box_test_ctrl, text="⏹ Detener", fg_color="#475569", height=38, font=ctk.CTkFont(size=12, weight="bold"), command=self.detener_animacion).pack(side="left", padx=5)

        ctk.CTkLabel(box_test_ctrl, text="Velocidad:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(20, 5))
        self.slider_speed = ctk.CTkSlider(box_test_ctrl, from_=1, to=5, width=120)
        self.slider_speed.set(3)
        self.slider_speed.pack(side="left")

        self.fig_anim, self.ax_anim = plt.subplots(figsize=(10, 5.8), facecolor='#0f172a')
        self.canvas_anim = FigureCanvasTkAgg(self.fig_anim, master=self.tab_test)
        self.canvas_anim.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.res_box = ctk.CTkFrame(self.tab_test, fg_color="#1e293b", corner_radius=8, height=95)
        self.res_box.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.res_box.pack_propagate(False)

        self.lbl_ref = ctk.CTkLabel(self.res_box, text="Cadena procesada: -", font=ctk.CTkFont(size=14, weight="bold"), text_color="#cbd5e1")
        self.lbl_ref.pack(pady=(10, 0))
        self.lbl_result = ctk.CTkLabel(self.res_box, text="Esperando inicio de prueba...", font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        self.lbl_result.pack(pady=(2, 8))

    # ================= FUNCIONES DE LÓGICA =================

    def set_example(self, text):
        self.entry_regex.delete(0, 'end')
        self.entry_regex.insert(0, text)
        self.process_automatas()

    def limpiar_todo(self):
        self.entry_regex.delete(0, 'end')
        self.entry_str.delete(0, 'end')
        self.lbl_tupla.configure(text="Genera una expresión...")
        self.current_nfa = None
        self.current_dfa = None
        self.thompson_steps = []
        self.current_step_idx = 0
        self.current_char_idx = 0
        self.animating = False
        self.lbl_step_info.configure(text="Paso 0 de 0")
        
        for item in self.tree_sub.get_children():
            self.tree_sub.delete(item)
            
        for ax, canvas in [(self.ax_afn, self.canvas_afn), (self.ax_step, self.canvas_step),
                           (self.ax_afd, self.canvas_afd), (self.ax_anim, self.canvas_anim),
                           (self.ax_all_afn, self.canvas_all_afn), (self.ax_all_afd, self.canvas_all_afd),
                           (self.ax_all_tree, self.canvas_all_tree)]:
            ax.clear()
            ax.set_facecolor('#0f172a' if ax != self.ax_step else '#1e293b')
            ax.axis('off')
            canvas.draw()

    def process_automatas(self):
        regex = self.entry_regex.get().strip()
        if not regex: return
        try:
            raw_tokens = RegexLexer.tokenize(regex)
            tokens = RegexLexer.insert_explicit_concatenation(raw_tokens)
            is_valid, msg = RegexLexer.validate(tokens)
            if not is_valid:
                messagebox.showerror("Error", msg)
                return

            postfix_tokens = RegexParser.to_postfix(tokens)
            tree_root = RegexParser.build_tree(postfix_tokens)
            if tree_root:
                RegexParser.draw_tree(tree_root, "arbol_sintactico")

            self.current_nfa = ThompsonBuilder.build_from_postfix(postfix_tokens)
            if self.current_nfa:
                ThompsonBuilder.draw_nfa(self.current_nfa, "afn_output")

            self.thompson_steps = ThompsonBuilder.build_with_steps(postfix_tokens)
            self.current_step_idx = 0

            self.current_dfa = DFABuilder.build_from_nfa(self.current_nfa)
            DFABuilder.draw_dfa(self.current_dfa, "afd_output")

            self.actualizar_tupla_formal()
            self.actualizar_tabla_subconjuntos()
            self.draw_graphs()
            
            self.current_char_idx = 0
            self.eval_string_at_step(0)

        except Exception as e:
            messagebox.showerror("Error de Procesamiento", f"Ocurrió un error:\n{str(e)}")

    def actualizar_tupla_formal(self):
        if not self.current_dfa:
            self.lbl_tupla.configure(text="No disponible")
            return
        
        states = sorted([f"S{st.id}" for st in self.current_dfa.states])
        alphabet = sorted(list(self.current_dfa.alphabet))
        q0 = f"S{self.current_dfa.start_state.id}" if self.current_dfa.start_state else "S0"
        accepts = [f"S{st.id}" for st in self.current_dfa.states if st.is_accept]

        tupla_str = f"Q = {{{', '.join(states)}}}\n" \
                    f"Σ = {{{', '.join(alphabet)}}}\n" \
                    f"q0 = {q0}\n" \
                    f"F = {{{', '.join(accepts)}}}"
        self.lbl_tupla.configure(text=tupla_str)

    def actualizar_tabla_subconjuntos(self):
        for item in self.tree_sub.get_children():
            self.tree_sub.delete(item)

        if not self.current_dfa: return

        alphabet = sorted(list(self.current_dfa.alphabet))
        for dfa_state in self.current_dfa.states:
            state_label = f"S{dfa_state.id}"
            if dfa_state.is_accept: state_label += " (A)"

            nfa_ids = sorted([st.id for st in dfa_state.nfa_states])
            conjunto_str = "{" + ", ".join(f"q{qid}" for qid in nfa_ids) + "}" if nfa_ids else "Ø"

            row_values = [state_label, conjunto_str, conjunto_str]
            for sym in alphabet:
                if sym in dfa_state.transitions:
                    row_values.append(f"S{dfa_state.transitions[sym].id}")
                else:
                    row_values.append("Ø")

            self.tree_sub.insert("", "end", values=row_values)

    def draw_graphs(self):
        components_all = [
            (self.ax_all_afn, self.canvas_all_afn, "afn_output.png", "1. AFN (Estados q)"),
            (self.ax_all_afd, self.canvas_all_afd, "afd_output.png", "2. AFD (Estados S)"),
            (self.ax_all_tree, self.canvas_all_tree, "arbol_sintactico.png", "3. ÁRBOL SINTÁCTICO")
        ]
        for ax, canvas, file_path, title in components_all:
            ax.clear()
            ax.set_facecolor('#0f172a')
            ax.axis('off')
            if os.path.exists(file_path):
                ax.imshow(Image.open(file_path).convert('RGB'))
                ax.set_title(title, color="white", fontsize=10, fontweight="bold")
            canvas.draw()

        for ax, canvas, file_path in [(self.ax_afn, self.canvas_afn, "afn_output.png"), (self.ax_afd, self.canvas_afd, "afd_output.png")]:
            ax.clear()
            ax.set_facecolor('#0f172a')
            ax.axis('off')
            if os.path.exists(file_path):
                ax.imshow(Image.open(file_path).convert('RGB'))
            canvas.draw()

        self.render_thompson_step()

    def render_thompson_step(self):
        self.ax_step.clear()
        self.ax_step.set_facecolor('#1e293b')
        self.ax_step.axis('off')
        if self.thompson_steps and os.path.exists(self.thompson_steps[self.current_step_idx]):
            self.ax_step.imshow(plt.imread(self.thompson_steps[self.current_step_idx]))
            self.lbl_step_info.configure(text=f"Paso {self.current_step_idx + 1} de {len(self.thompson_steps)}")
        self.canvas_step.draw()

    def prev_thompson_step(self):
        if self.thompson_steps and self.current_step_idx > 0:
            self.current_step_idx -= 1
            self.render_thompson_step()

    def next_thompson_step(self):
        if self.thompson_steps and self.current_step_idx < len(self.thompson_steps) - 1:
            self.current_step_idx += 1
            self.render_thompson_step()

    def reproducir_cadena(self):
        if not self.current_nfa: return
        self.animating = True
        self.current_char_idx = 0
        self.res_box.configure(fg_color="#1e293b")
        self.animate_step()

    def paso_a_paso_cadena(self):
        if not self.current_nfa: return
        self.animating = False
        cadena = self.entry_str.get().strip()
        
        if self.current_char_idx > len(cadena):
            self.current_char_idx = 0
            
        self.eval_string_at_step(self.current_char_idx)
        self.current_char_idx += 1

    def detener_animacion(self):
        self.animating = False
        self.current_char_idx = 0
        self.eval_string_at_step(0)
        self.res_box.configure(fg_color="#1e293b")
        self.lbl_ref.configure(text="Cadena procesada: -")
        self.lbl_result.configure(text="Animación detenida / Reiniciada")

    def animate_step(self):
        if not self.animating: return
        cadena = self.entry_str.get().strip()
        if self.current_char_idx <= len(cadena):
            self.eval_string_at_step(self.current_char_idx)
            self.current_char_idx += 1
            delay = int(800 / self.slider_speed.get())
            self.after(max(100, delay), self.animate_step)
        else:
            self.animating = False

    def eval_string_at_step(self, step_limit):
        if not self.current_nfa: return
        cadena = self.entry_str.get().strip()
        sub = cadena[:step_limit]

        def get_epsilon_closure(states):
            closure = set(states)
            stack = list(states)
            while stack:
                state = stack.pop()
                if 'ε' in state.transitions:
                    for next_st in state.transitions['ε']:
                        if next_st not in closure:
                            closure.add(next_st)
                            stack.append(next_st)
            return closure

        current_states = get_epsilon_closure([self.current_nfa.start_state])
        for char in sub:
            next_states = set()
            for st in current_states:
                if char in st.transitions:
                    for target in st.transitions[char]:
                        next_states.add(target)
            current_states = get_epsilon_closure(next_states)

        self.lbl_ref.configure(text=f"Procesando: {sub if sub else 'ε'}")
        
        try:
            active_ids = [s.id for s in current_states]
            ThompsonBuilder.draw_nfa(self.current_nfa, "anim_temp", active_states=active_ids)
            self.update_animation_graph("anim_temp.png")
        except TypeError:
            ThompsonBuilder.draw_nfa(self.current_nfa, "anim_temp")
            self.update_animation_graph("anim_temp.png")

        if step_limit == len(cadena):
            if self.current_nfa.accept_state in current_states:
                self.res_box.configure(fg_color="#15803d")
                self.lbl_result.configure(text=f"¡CADENA ACEPTADA! ✔ — La cadena '{cadena}' pertenece al lenguaje.")
            else:
                self.res_box.configure(fg_color="#b91c1c")
                self.lbl_result.configure(text=f"CADENA RECHAZADA ✖ — La cadena '{cadena}' NO pertenece al lenguaje.")
        else:
            self.res_box.configure(fg_color="#d97706")
            self.lbl_result.configure(text="Evaluando transiciones paso a paso...")

    def update_animation_graph(self, filepath):
        self.ax_anim.clear()
        self.ax_anim.set_facecolor('#0f172a')
        self.ax_anim.axis('off')
        if os.path.exists(filepath):
            self.ax_anim.imshow(Image.open(filepath).convert('RGB'))
        self.canvas_anim.draw()

    def create_footer(self):
        footer = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color="#070d1e")
        footer.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        ctk.CTkLabel(footer, text="Página 1 | 1", font=ctk.CTkFont(size=11), text_color="#64748b").pack(side="left", padx=20)
        ctk.CTkLabel(footer, text="Grupo 1", font=ctk.CTkFont(size=11), text_color="#64748b").pack(side="left", expand=True)
        
        self.lbl_footer_fecha = ctk.CTkLabel(footer, text="", font=ctk.CTkFont(size=11), text_color="#64748b")
        self.lbl_footer_fecha.pack(side="right", padx=20)
        self.actualizar_reloj_tiempo_real()

    def actualizar_reloj_tiempo_real(self):
        ahora = datetime.datetime.now()
        fecha_str = ahora.strftime("Fecha y Hora: %d de %B %Y - %H:%M:%S")
        self.lbl_footer_fecha.configure(text=fecha_str)
        self.after(1000, self.actualizar_reloj_tiempo_real)

if __name__ == "__main__":
    app = AutoLangIDE()
    app.mainloop()