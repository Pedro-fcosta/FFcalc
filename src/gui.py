from pathlib import Path

import customtkinter as ctk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.analise_dashboard import analisar_dashboard
from src.analise_fadiga import calcular_analise_fadiga, formatar_fator
from src.analise_fluencia import (
    calcular_analise_fluencia,
    formatar_cientifico,
    formatar_percentual,
    obter_preset_fluencia,
)
from src.fluencia import calcular_taxa_norton_arrhenius
from src.materiais import carregar_materiais


RAIZ_PROJETO = Path(__file__).resolve().parent.parent

APP_BG = "#04111f"
SIDEBAR_BG = "#061a30"
SURFACE = "#08233f"
SURFACE_SOFT = "#0d3158"
SURFACE_LIGHT = "#124571"
BORDER = "#23608f"
TEXT = "#f8fbff"
TEXT_MUTED = "#b7cbe3"
TEXT_FAINT = "#7fa6c9"
ACCENT = "#7dd3fc"
ACCENT_DARK = "#2563eb"
SUCCESS = "#bfdbfe"
WARNING = "#60a5fa"
DANGER = "#eff6ff"
PLOT_BG = "#061426"
PLOT_PANEL = "#0a2038"
GRID = "#1d4f7a"
PILL_INFO = "#0b3a66"
PILL_OK = "#1d5f99"
PILL_WARN = "#164f83"
PILL_CRIT = "#dbeafe"
PILL_CRIT_TEXT = "#04111f"


MODULOS = {
    "Fadiga": "fadiga",
    "Fluencia": "fluencia",
    "Dashboard": "dashboard",
}


class FFCalcApp(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        super().__init__()

        self.title("FFCalc - Fadiga e Fluencia")
        self.geometry("1280x820")
        self.minsize(1080, 700)
        self.configure(fg_color=APP_BG)

        self.materiais = carregar_materiais()
        self.material_por_opcao = {}
        self.material_opcoes = self._montar_opcoes_materiais()

        self.modulo_atual = "fadiga"
        self.modulo_var = ctk.StringVar(value="Fadiga")
        self.material_var = ctk.StringVar(
            value=self.material_opcoes[0] if self.material_opcoes else ""
        )
        self.entrada_vars = {}
        self.cards_resumo = {}
        self.linhas_criterios = {}
        self.eixo_3 = None
        self.resultado_atual = None

        self._criar_layout()
        self._configurar_modulo("fadiga")

    def _montar_opcoes_materiais(self):
        if self.materiais is None:
            return []

        opcoes = []

        for _, material in self.materiais.iterrows():
            opcao = f"{int(material['id'])} - {material['material']}"
            opcoes.append(opcao)
            self.material_por_opcao[opcao] = material

        return opcoes

    def _criar_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.painel_entrada = ctk.CTkFrame(
            self,
            width=350,
            corner_radius=0,
            fg_color=SIDEBAR_BG,
        )
        self.painel_entrada.grid(row=0, column=0, sticky="nsew")
        self.painel_entrada.grid_columnconfigure(0, weight=1)
        self.painel_entrada.grid_rowconfigure(2, weight=1)

        self.painel_principal = ctk.CTkFrame(self, fg_color=APP_BG)
        self.painel_principal.grid(row=0, column=1, sticky="nsew", padx=18, pady=18)
        self.painel_principal.grid_columnconfigure(0, weight=1)
        self.painel_principal.grid_rowconfigure(2, weight=1)

        self._criar_sidebar()
        self._criar_cabecalho()
        self._criar_area_cards()
        self._criar_area_analise()

    def _criar_sidebar(self):
        topo = ctk.CTkFrame(self.painel_entrada, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", padx=24, pady=(28, 16))
        topo.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            topo,
            text="FFCalc",
            text_color=TEXT,
            font=ctk.CTkFont(size=30, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            topo,
            text="Fadiga e fluencia em um painel modular",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.modulo_selector = ctk.CTkSegmentedButton(
            self.painel_entrada,
            values=["Fadiga", "Fluencia", "Dashboard"],
            variable=self.modulo_var,
            command=self._trocar_modulo,
            height=38,
            corner_radius=8,
            fg_color=SURFACE,
            selected_color=ACCENT_DARK,
            selected_hover_color=ACCENT,
            unselected_color=SURFACE_SOFT,
            unselected_hover_color=SURFACE_LIGHT,
            text_color=TEXT,
        )
        self.modulo_selector.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 14))

        self.sidebar_scroll = ctk.CTkScrollableFrame(
            self.painel_entrada,
            fg_color="transparent",
            scrollbar_button_color=SURFACE_LIGHT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )
        self.sidebar_scroll.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_scroll.grid_columnconfigure(0, weight=1)

        self.entrada_card = self._criar_card(self.sidebar_scroll)
        self.entrada_card.grid(row=0, column=0, sticky="ew", padx=18, pady=(0, 14))
        self.entrada_card.grid_columnconfigure(0, weight=1)

        self.material_card = self._criar_card(self.sidebar_scroll)
        self.material_card.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 14))
        self.material_card.grid_columnconfigure(0, weight=1)
        self._criar_material_card()

        self.botoes_card = ctk.CTkFrame(self.sidebar_scroll, fg_color="transparent")
        self.botoes_card.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))
        self.botoes_card.grid_columnconfigure((0, 1), weight=1)

        self.calcular_button = ctk.CTkButton(
            self.botoes_card,
            text="Calcular",
            command=self.calcular,
            height=40,
            corner_radius=8,
            fg_color=ACCENT_DARK,
            hover_color=ACCENT,
            text_color=TEXT,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.calcular_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.limpar_button = ctk.CTkButton(
            self.botoes_card,
            text="Limpar",
            command=self.limpar,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            hover_color=SURFACE_SOFT,
            text_color=TEXT,
            height=40,
            corner_radius=8,
        )
        self.limpar_button.grid(row=0, column=1, sticky="ew")

        self.exemplo_button = ctk.CTkButton(
            self.sidebar_scroll,
            text="Usar exemplo",
            command=self.usar_exemplo,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            hover_color=SURFACE_SOFT,
            text_color=TEXT_MUTED,
            height=36,
            corner_radius=8,
        )
        self.exemplo_button.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 12))

        self.salvar_button = ctk.CTkButton(
            self.sidebar_scroll,
            text="Salvar grafico PNG",
            command=self.salvar_grafico,
            state="disabled",
            height=38,
            corner_radius=8,
            fg_color=SURFACE_SOFT,
            hover_color=BORDER,
            text_color=TEXT,
        )
        self.salvar_button.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 12))

        self.status_label = ctk.CTkLabel(
            self.sidebar_scroll,
            text="Selecione um modulo e calcule.",
            anchor="w",
            justify="left",
            wraplength=290,
            text_color=TEXT_MUTED,
            fg_color=SURFACE,
            corner_radius=8,
            padx=14,
            pady=12,
        )
        self.status_label.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 18))

        if not self.material_opcoes:
            self.calcular_button.configure(state="disabled")
            self._set_status("Nao foi possivel carregar data/materiais.csv.", "erro")

    def _criar_card(self, master):
        return ctk.CTkFrame(
            master,
            fg_color=SURFACE,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )

    def _criar_material_card(self):
        for widget in self.material_card.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.material_card,
            text="Material",
            text_color=TEXT,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        self.material_menu = ctk.CTkOptionMenu(
            self.material_card,
            values=self.material_opcoes if self.material_opcoes else ["Sem materiais"],
            variable=self.material_var,
            command=self._ao_trocar_material,
            fg_color=SURFACE_SOFT,
            button_color=ACCENT_DARK,
            button_hover_color=ACCENT,
            text_color=TEXT,
            dropdown_fg_color=SURFACE,
            dropdown_hover_color=SURFACE_SOFT,
            corner_radius=8,
            height=38,
        )
        self.material_menu.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))

        self.material_info_label = ctk.CTkLabel(
            self.material_card,
            text="--",
            text_color=TEXT_MUTED,
            justify="left",
            anchor="w",
            wraplength=285,
        )
        self.material_info_label.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))

    def _criar_cabecalho(self):
        self.header_frame = ctk.CTkFrame(self.painel_principal, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Modulo de Fadiga",
            text_color=TEXT,
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        self.header_title.grid(row=0, column=0, sticky="w")

        self.header_subtitle = ctk.CTkLabel(
            self.header_frame,
            text="Compare criterios de fadiga e acompanhe a margem de seguranca.",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=13),
        )
        self.header_subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.status_pill = ctk.CTkLabel(
            self.header_frame,
            text="Aguardando calculo",
            text_color=TEXT,
            fg_color=PILL_INFO,
            corner_radius=18,
            padx=14,
            pady=8,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.status_pill.grid(row=0, column=1, sticky="e")

    def _criar_area_cards(self):
        self.cards_frame = ctk.CTkFrame(self.painel_principal, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 14))

    def _criar_area_analise(self):
        self.area_frame = ctk.CTkFrame(self.painel_principal, fg_color="transparent")
        self.area_frame.grid(row=2, column=0, sticky="nsew")
        self.area_frame.grid_columnconfigure(0, weight=0)
        self.area_frame.grid_columnconfigure(1, weight=1)
        self.area_frame.grid_rowconfigure(0, weight=1)

        self.resultado_frame = self._criar_card(self.area_frame)
        self.resultado_frame.configure(width=340)
        self.resultado_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self.resultado_frame.grid_propagate(False)
        self.resultado_frame.grid_columnconfigure(0, weight=1)

        self.grafico_frame = self._criar_card(self.area_frame)
        self.grafico_frame.grid(row=0, column=1, sticky="nsew")
        self.grafico_frame.grid_columnconfigure(0, weight=1)
        self.grafico_frame.grid_rowconfigure(1, weight=1)

        cabecalho = ctk.CTkFrame(self.grafico_frame, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
        cabecalho.grid_columnconfigure(0, weight=1)

        self.grafico_title = ctk.CTkLabel(
            cabecalho,
            text="Visualizacao",
            text_color=TEXT,
            font=ctk.CTkFont(size=17, weight="bold"),
        )
        self.grafico_title.grid(row=0, column=0, sticky="w")

        self.grafico_subtitle = ctk.CTkLabel(
            cabecalho,
            text="Linhas limite e margem por criterio",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12),
        )
        self.grafico_subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.figura = Figure(figsize=(9.2, 5.0), dpi=100, facecolor=PLOT_BG)
        self.eixo_1 = self.figura.add_subplot(1, 2, 1)
        self.eixo_2 = self.figura.add_subplot(1, 2, 2)
        self.figura.subplots_adjust(
            left=0.075,
            right=0.975,
            top=0.86,
            bottom=0.18,
            wspace=0.32,
        )

        self.canvas = FigureCanvasTkAgg(self.figura, master=self.grafico_frame)
        widget = self.canvas.get_tk_widget()
        widget.configure(bg=SURFACE, highlightthickness=0)
        widget.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

    def _configurar_eixos(self, quantidade):
        self.figura.clear()

        if quantidade == 3:
            self.eixo_1 = self.figura.add_subplot(1, 3, 1)
            self.eixo_2 = self.figura.add_subplot(1, 3, 2)
            self.eixo_3 = self.figura.add_subplot(1, 3, 3)
            self.figura.subplots_adjust(
                left=0.055,
                right=0.98,
                top=0.84,
                bottom=0.27,
                wspace=0.36,
            )
        else:
            self.eixo_1 = self.figura.add_subplot(1, 2, 1)
            self.eixo_2 = self.figura.add_subplot(1, 2, 2)
            self.eixo_3 = None
            self.figura.subplots_adjust(
                left=0.075,
                right=0.975,
                top=0.86,
                bottom=0.18,
                wspace=0.32,
            )

    def _trocar_modulo(self, nome_modulo):
        self._configurar_modulo(MODULOS[nome_modulo])

    def _configurar_modulo(self, modulo):
        self.modulo_atual = modulo
        self.resultado_atual = None
        self.salvar_button.configure(state="disabled")
        self.entrada_vars = {}
        self.cards_resumo = {}
        self.linhas_criterios = {}

        self._limpar_container(self.entrada_card)
        self._limpar_container(self.cards_frame)
        self._limpar_container(self.resultado_frame)

        if modulo == "dashboard":
            self.material_card.grid_remove()
        else:
            self.material_card.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 14))

        if modulo == "fadiga":
            self._configurar_fadiga()
        elif modulo == "fluencia":
            self._configurar_fluencia()
        else:
            self._configurar_dashboard()

        self._configurar_eixos(3 if modulo == "dashboard" else 2)
        self._atualizar_material_card()
        self._desenhar_grafico_vazio()
        self._set_status("Preencha os dados do modulo e clique em Calcular.", "info")
        self._set_status_pill("Aguardando calculo", PILL_INFO, TEXT)

    def _configurar_fadiga(self):
        self.resultado_frame.configure(width=340)
        self.header_title.configure(text="Modulo de Fadiga")
        self.header_subtitle.configure(
            text="Compare Goodman, Soderberg e Gerber para carregamento ciclico."
        )
        self.grafico_subtitle.configure(text="Diagrama sigma_m x sigma_a e fatores de seguranca")
        self.exemplo_button.configure(text="Usar exemplo 250 / 50")
        self.calcular_button.configure(text="Calcular fadiga")

        campos = [
            ("sigma_max", "Tensao maxima", "sigma_max [MPa]", "250", "Ex.: 250"),
            ("sigma_min", "Tensao minima", "sigma_min [MPa]", "50", "Ex.: 50"),
        ]
        self._criar_campos_entrada("Entradas de fadiga", campos)

        cards = [
            ("sigma_a", "Tensao alternada", "--", "MPa"),
            ("sigma_m", "Tensao media", "--", "MPa"),
            ("razao_r", "Razao R", "--", ""),
            ("menor_fs", "Menor fator n", "--", ""),
        ]
        self._criar_cards_resumo(cards)
        self._criar_painel_resultados(
            "Criterios de fadiga",
            "Resumo por metodo",
            ["Goodman", "Soderberg", "Gerber"],
            "Detalhes do ciclo",
            "Calcule para visualizar os parametros.",
        )

    def _configurar_fluencia(self):
        self.resultado_frame.configure(width=340)
        self.header_title.configure(text="Modulo de Fluencia")
        self.header_subtitle.configure(
            text="Estime temperatura homologa, taxa de fluencia e consumo de deformacao."
        )
        self.grafico_subtitle.configure(text="Taxa por temperatura e deformacao acumulada no tempo")
        self.exemplo_button.configure(text="Usar exemplo de fluencia")
        self.calcular_button.configure(text="Calcular fluencia")

        preset = self._preset_material_atual()
        campos = [
            ("tensao_mpa", "Tensao aplicada", "sigma [MPa]", "120", "Ex.: 120"),
            (
                "temperatura_operacao_c",
                "Temperatura de operacao",
                "T [C]",
                "550",
                "Ex.: 550",
            ),
            (
                "temperatura_fusao_c",
                "Temperatura de fusao",
                "Tf [C]",
                f"{preset['temperatura_fusao_c']:.0f}",
                "Ex.: 1450",
            ),
            ("tempo_operacao_h", "Tempo de operacao", "t [h]", "10000", "Ex.: 10000"),
            (
                "coeficiente_a",
                "Coeficiente Norton",
                "A",
                f"{preset['coeficiente_a']:.3e}",
                "Ex.: 1e-2",
            ),
            (
                "expoente_n",
                "Expoente Norton",
                "n",
                f"{preset['expoente_n']:.2f}",
                "Ex.: 4",
            ),
            (
                "energia_ativacao_kj_mol",
                "Energia de ativacao",
                "Q [kJ/mol]",
                f"{preset['energia_ativacao_kj_mol']:.0f}",
                "Ex.: 220",
            ),
            (
                "deformacao_limite_percentual",
                "Deformacao limite",
                "epsilon_lim [%]",
                "1",
                "Ex.: 1",
            ),
        ]
        self._criar_campos_entrada("Entradas de fluencia", campos)

        cards = [
            ("temperatura_homologa", "Temperatura homologa", "--", "T/Tf"),
            ("taxa_fluencia_h", "Taxa estimada", "--", "1/h"),
            ("deformacao_percentual", "Deformacao", "--", "%"),
            ("consumo_limite_percentual", "Consumo limite", "--", "%"),
        ]
        self._criar_cards_resumo(cards)
        self._criar_painel_resultados(
            "Criterios de fluencia",
            "Resumo preliminar",
            ["Temperatura homologa", "Taxa estimada", "Consumo do limite"],
            "Detalhes de fluencia",
            "Calcule para visualizar taxa, tempo e consumo.",
        )

    def _configurar_dashboard(self):
        self.resultado_frame.configure(width=430)
        self.header_title.configure(text="Modulo Dashboard")
        self.header_subtitle.configure(
            text="Compare materiais sob a mesma condicao de fadiga e fluencia."
        )
        self.grafico_subtitle.configure(
            text="Ranking preliminar, fator minimo de fadiga e consumo por fluencia"
        )
        self.exemplo_button.configure(text="Usar exemplo do Dashboard")
        self.calcular_button.configure(text="Calcular Dashboard")

        campos = [
            ("sigma_max", "Tensao maxima", "sigma_max [MPa]", "250", "Ex.: 250"),
            ("sigma_min", "Tensao minima", "sigma_min [MPa]", "50", "Ex.: 50"),
            (
                "sigma_creep",
                "Tensao para fluencia",
                "sigma_creep [MPa]",
                "120",
                "Ex.: 120",
            ),
            (
                "temperatura_operacao_c",
                "Temperatura de operacao",
                "T [C]",
                "550",
                "Ex.: 550",
            ),
            ("tempo_h", "Tempo de operacao", "t [h]", "10000", "Ex.: 10000"),
            (
                "deformacao_limite_pct",
                "Deformacao limite",
                "epsilon_lim [%]",
                "1",
                "Ex.: 1",
            ),
        ]
        self._criar_campos_entrada("Condicao de operacao", campos)

        cards = [
            ("melhor_material", "Melhor material preliminar", "--", "score"),
            ("maior_fs", "Maior fator minimo", "--", "fadiga"),
            ("menor_consumo", "Menor consumo", "--", "fluencia"),
            ("materiais_avaliados", "Materiais avaliados", "--", "total"),
        ]
        self._criar_cards_resumo(cards)
        self._criar_painel_dashboard()

    def _criar_painel_dashboard(self):
        self.resultado_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self.resultado_frame,
            text="Ranking de materiais",
            text_color=TEXT,
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 6))

        ctk.CTkLabel(
            self.resultado_frame,
            text="Comparacao didatica ordenada por score preliminar",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 10))

        self.ranking_container = ctk.CTkScrollableFrame(
            self.resultado_frame,
            fg_color="transparent",
            scrollbar_button_color=SURFACE_LIGHT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )
        self.ranking_container.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.ranking_container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.ranking_container,
            text="Calcule para visualizar o ranking preliminar.",
            text_color=TEXT_MUTED,
            justify="left",
            anchor="w",
            wraplength=360,
        ).grid(row=0, column=0, sticky="ew", padx=8, pady=8)

    def _criar_campos_entrada(self, titulo, campos):
        ctk.CTkLabel(
            self.entrada_card,
            text=titulo,
            text_color=TEXT,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 14))

        row = 1
        for chave, nome, simbolo, valor, placeholder in campos:
            ctk.CTkLabel(
                self.entrada_card,
                text=f"{nome}  |  {simbolo}",
                text_color=TEXT_MUTED,
                anchor="w",
            ).grid(row=row, column=0, sticky="ew", padx=16, pady=(0, 6))
            row += 1

            var = ctk.StringVar(value=valor)
            self.entrada_vars[chave] = var
            entry = ctk.CTkEntry(
                self.entrada_card,
                textvariable=var,
                placeholder_text=placeholder,
                fg_color=SURFACE_SOFT,
                border_color=BORDER,
                text_color=TEXT,
                placeholder_text_color=TEXT_FAINT,
                corner_radius=8,
                height=38,
            )
            entry.grid(row=row, column=0, sticky="ew", padx=16, pady=(0, 14))
            row += 1

    def _criar_cards_resumo(self, definicoes):
        self.cards_frame.grid_columnconfigure(tuple(range(len(definicoes))), weight=1, uniform="cards")

        for coluna, (chave, titulo, valor, unidade) in enumerate(definicoes):
            card = self._criar_card(self.cards_frame)
            card.grid(
                row=0,
                column=coluna,
                sticky="ew",
                padx=(0, 10 if coluna < len(definicoes) - 1 else 0),
            )
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                card,
                text=titulo,
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=12),
            ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 2))

            valor_label = ctk.CTkLabel(
                card,
                text=valor,
                text_color=TEXT,
                font=ctk.CTkFont(size=23, weight="bold"),
            )
            valor_label.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 2))

            ctk.CTkLabel(
                card,
                text=unidade or " ",
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=11),
            ).grid(row=2, column=0, sticky="w", padx=16, pady=(0, 14))

            self.cards_resumo[chave] = valor_label

    def _criar_painel_resultados(
        self,
        titulo,
        subtitulo,
        criterios,
        detalhes_titulo,
        detalhes_texto,
    ):
        ctk.CTkLabel(
            self.resultado_frame,
            text=titulo,
            text_color=TEXT,
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 6))

        ctk.CTkLabel(
            self.resultado_frame,
            text=subtitulo,
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 10))

        criterios_container = ctk.CTkFrame(self.resultado_frame, fg_color="transparent")
        criterios_container.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))
        criterios_container.grid_columnconfigure(0, weight=1)

        for indice, criterio in enumerate(criterios):
            self._criar_linha_criterio(criterios_container, criterio, indice)

        ctk.CTkFrame(self.resultado_frame, fg_color=BORDER, height=1).grid(
            row=3,
            column=0,
            sticky="ew",
            padx=18,
            pady=(4, 14),
        )

        ctk.CTkLabel(
            self.resultado_frame,
            text=detalhes_titulo,
            text_color=TEXT,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=4, column=0, sticky="w", padx=18, pady=(0, 8))

        self.detalhes_label = ctk.CTkLabel(
            self.resultado_frame,
            text=detalhes_texto,
            text_color=TEXT_MUTED,
            justify="left",
            anchor="nw",
            wraplength=290,
        )
        self.detalhes_label.grid(row=5, column=0, sticky="nsew", padx=18, pady=(0, 16))

    def _criar_linha_criterio(self, master, criterio, row):
        linha = ctk.CTkFrame(master, fg_color=SURFACE_SOFT, corner_radius=8)
        linha.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        linha.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            linha,
            text=criterio,
            text_color=TEXT,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 0))

        valor_label = ctk.CTkLabel(
            linha,
            text="--",
            text_color=TEXT,
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        valor_label.grid(row=0, column=1, sticky="e", padx=12, pady=(10, 0))

        classificacao_label = ctk.CTkLabel(
            linha,
            text="Aguardando calculo",
            text_color=TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=285,
            font=ctk.CTkFont(size=12),
        )
        classificacao_label.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=12,
            pady=(2, 10),
        )

        self.linhas_criterios[criterio] = {
            "frame": linha,
            "valor": valor_label,
            "classificacao": classificacao_label,
        }

    def calcular(self):
        try:
            if self.modulo_atual == "fadiga":
                self.resultado_atual = self._calcular_fadiga()
                self._mostrar_resultado_fadiga()
                self._desenhar_graficos_fadiga()
            elif self.modulo_atual == "fluencia":
                self.resultado_atual = self._calcular_fluencia()
                self._mostrar_resultado_fluencia()
                self._desenhar_graficos_fluencia()
            else:
                self.resultado_atual = self._calcular_dashboard()
                self._mostrar_resultado_dashboard()
                self._desenhar_graficos_dashboard()
        except ValueError as erro:
            self.resultado_atual = None
            self.salvar_button.configure(state="disabled")
            self._set_status(str(erro), "erro")
            self._set_status_pill("Entrada invalida", PILL_CRIT, PILL_CRIT_TEXT)
            return

        self.salvar_button.configure(state="normal")
        self._set_status("Calculo concluido. Graficos atualizados.", "ok")
        self._atualizar_status_pill_resultado()

    def _calcular_fadiga(self):
        material = self._material_selecionado()

        if material is None:
            raise ValueError("Selecione um material valido.")

        return calcular_analise_fadiga(
            self._ler_float("sigma_max", "tensao maxima"),
            self._ler_float("sigma_min", "tensao minima"),
            material,
        )

    def _calcular_fluencia(self):
        material = self._material_selecionado()

        if material is None:
            raise ValueError("Selecione um material valido.")

        return calcular_analise_fluencia(
            tensao_mpa=self._ler_float("tensao_mpa", "tensao aplicada"),
            temperatura_operacao_c=self._ler_float(
                "temperatura_operacao_c",
                "temperatura de operacao",
            ),
            temperatura_fusao_c=self._ler_float(
                "temperatura_fusao_c",
                "temperatura de fusao",
            ),
            tempo_operacao_h=self._ler_float("tempo_operacao_h", "tempo de operacao"),
            coeficiente_a=self._ler_float("coeficiente_a", "coeficiente Norton A"),
            expoente_n=self._ler_float("expoente_n", "expoente Norton n"),
            energia_ativacao_kj_mol=self._ler_float(
                "energia_ativacao_kj_mol",
                "energia de ativacao",
            ),
            deformacao_limite_percentual=self._ler_float(
                "deformacao_limite_percentual",
                "deformacao limite",
            ),
            material=material,
        )

    def _calcular_dashboard(self):
        return analisar_dashboard(
            sigma_max=self._ler_float("sigma_max", "tensao maxima"),
            sigma_min=self._ler_float("sigma_min", "tensao minima"),
            sigma_creep=self._ler_float("sigma_creep", "tensao para fluencia"),
            temperatura_operacao_c=self._ler_float(
                "temperatura_operacao_c",
                "temperatura de operacao",
            ),
            tempo_h=self._ler_float("tempo_h", "tempo de operacao"),
            deformacao_limite_pct=self._ler_float(
                "deformacao_limite_pct",
                "deformacao limite",
            ),
            materiais=self.materiais,
        )

    def limpar(self):
        self.resultado_atual = None
        self.salvar_button.configure(state="disabled")
        self._configurar_modulo(self.modulo_atual)
        self._set_status("Campos restaurados.", "info")

    def usar_exemplo(self):
        if self.modulo_atual == "fadiga":
            valores = {"sigma_max": "250", "sigma_min": "50"}
        elif self.modulo_atual == "fluencia":
            preset = self._preset_material_atual()
            valores = {
                "tensao_mpa": "120",
                "temperatura_operacao_c": "550",
                "temperatura_fusao_c": f"{preset['temperatura_fusao_c']:.0f}",
                "tempo_operacao_h": "10000",
                "coeficiente_a": f"{preset['coeficiente_a']:.3e}",
                "expoente_n": f"{preset['expoente_n']:.2f}",
                "energia_ativacao_kj_mol": f"{preset['energia_ativacao_kj_mol']:.0f}",
                "deformacao_limite_percentual": "1",
            }
        else:
            valores = {
                "sigma_max": "250",
                "sigma_min": "50",
                "sigma_creep": "120",
                "temperatura_operacao_c": "550",
                "tempo_h": "10000",
                "deformacao_limite_pct": "1",
            }

        for chave, valor in valores.items():
            self.entrada_vars[chave].set(valor)

        self.calcular()

    def salvar_grafico(self):
        if self.resultado_atual is None:
            self._set_status("Calcule antes de salvar o grafico.", "erro")
            return

        nomes = {
            "fadiga": "grafico_fadiga.png",
            "fluencia": "grafico_fluencia.png",
            "dashboard": "grafico_dashboard.png",
        }
        nome = nomes[self.modulo_atual]
        saida = RAIZ_PROJETO / "outputs" / nome
        saida.parent.mkdir(exist_ok=True)
        self.figura.savefig(saida, dpi=180, facecolor=PLOT_BG, bbox_inches="tight")
        self._set_status(f"Grafico salvo em {saida}", "ok")

    def _mostrar_resultado_fadiga(self):
        resultado = self.resultado_atual
        ciclo = resultado["ciclo"]
        fatores = resultado["fatores"]
        razao_r = "--" if ciclo["razao_r"] is None else f"{ciclo['razao_r']:.3f}"
        menor_criterio, menor_fator = min(fatores.items(), key=lambda item: item[1])

        self.cards_resumo["sigma_a"].configure(text=f"{ciclo['sigma_a']:.2f}")
        self.cards_resumo["sigma_m"].configure(text=f"{ciclo['sigma_m']:.2f}")
        self.cards_resumo["razao_r"].configure(text=razao_r)
        self.cards_resumo["menor_fs"].configure(text=formatar_fator(menor_fator))

        self.detalhes_label.configure(
            text="\n".join(
                [
                    f"sigma_max: {ciclo['sigma_max']:.2f} MPa",
                    f"sigma_min: {ciclo['sigma_min']:.2f} MPa",
                    f"Metodo critico: {menor_criterio}",
                    "",
                    "Leitura rapida:",
                    self._resumo_fadiga(menor_fator),
                ]
            )
        )

        for criterio, fator in fatores.items():
            linha = self.linhas_criterios[criterio]
            cor = self._cor_fator_fadiga(fator)
            linha["frame"].configure(border_width=1, border_color=cor)
            linha["valor"].configure(text=f"n = {formatar_fator(fator)}", text_color=cor)
            linha["classificacao"].configure(text=resultado["classificacoes"][criterio])

    def _mostrar_resultado_fluencia(self):
        resultado = self.resultado_atual
        valores = resultado["resultados"]
        entradas = resultado["entradas"]
        criterios = resultado["criterios"]

        self.cards_resumo["temperatura_homologa"].configure(
            text=f"{valores['temperatura_homologa']:.3f}"
        )
        self.cards_resumo["taxa_fluencia_h"].configure(
            text=formatar_cientifico(valores["taxa_fluencia_h"])
        )
        self.cards_resumo["deformacao_percentual"].configure(
            text=f"{valores['deformacao_percentual']:.4f}"
        )
        self.cards_resumo["consumo_limite_percentual"].configure(
            text=f"{valores['consumo_limite_percentual']:.2f}"
        )

        self.detalhes_label.configure(
            text="\n".join(
                [
                    f"Tensao: {entradas['tensao_mpa']:.2f} MPa",
                    f"Temperatura: {entradas['temperatura_operacao_c']:.1f} C",
                    f"Tempo: {entradas['tempo_operacao_h']:.0f} h",
                    f"Tempo ate limite: {self._formatar_horas(valores['tempo_limite_h'])}",
                    "",
                    "Leitura rapida:",
                    self._resumo_fluencia(valores["consumo_limite_percentual"]),
                ]
            )
        )

        for criterio, dados in criterios.items():
            linha = self.linhas_criterios[criterio]
            cor = self._cor_criterio_fluencia(criterio, dados["valor"])
            linha["frame"].configure(border_width=1, border_color=cor)
            linha["valor"].configure(
                text=self._formatar_valor_criterio_fluencia(criterio, dados["valor"]),
                text_color=cor,
            )
            linha["classificacao"].configure(text=dados["classificacao"])

    def _mostrar_resultado_dashboard(self):
        ranking = self.resultado_atual
        melhor = ranking.iloc[0]
        maior_fs = ranking.loc[ranking["menor_fs_fadiga"].idxmax()]
        menor_consumo = ranking.loc[ranking["consumo_fluencia_pct"].idxmin()]

        self.cards_resumo["melhor_material"].configure(
            text=f"{self._abreviar(melhor['material'], 18)}\n{melhor['score_total']:.2f}"
        )
        self.cards_resumo["maior_fs"].configure(
            text=f"{self._abreviar(maior_fs['material'], 18)}\n{maior_fs['menor_fs_fadiga']:.2f}"
        )
        self.cards_resumo["menor_consumo"].configure(
            text=(
                f"{self._abreviar(menor_consumo['material'], 18)}\n"
                f"{menor_consumo['consumo_fluencia_pct']:.2f}%"
            )
        )
        self.cards_resumo["materiais_avaliados"].configure(text=str(len(ranking)))

        self._preencher_ranking_dashboard(ranking)

    def _preencher_ranking_dashboard(self, ranking):
        self._limpar_container(self.ranking_container)

        for indice, (_, material) in enumerate(ranking.iterrows()):
            cor = self._cor_score_dashboard(material["score_total"])
            card = ctk.CTkFrame(
                self.ranking_container,
                fg_color=SURFACE_SOFT,
                corner_radius=8,
                border_width=1,
                border_color=cor,
            )
            card.grid(row=indice, column=0, sticky="ew", pady=(0, 10))
            card.grid_columnconfigure(0, weight=1)

            titulo = (
                f"#{int(material['ranking'])}  "
                f"{material['material']}"
            )
            ctk.CTkLabel(
                card,
                text=titulo,
                text_color=TEXT,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
                wraplength=370,
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))

            detalhes = (
                f"FS min: {material['menor_fs_fadiga']:.2f} | "
                f"Fluencia: {material['consumo_fluencia_pct']:.2f}%\n"
                f"T/Tf: {material['temperatura_homologa']:.3f} | "
                f"Score: {material['score_total']:.2f}"
            )
            ctk.CTkLabel(
                card,
                text=detalhes,
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=12),
                justify="left",
                anchor="w",
            ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 4))

            ctk.CTkLabel(
                card,
                text=material["classificacao_geral"],
                text_color=cor,
                font=ctk.CTkFont(size=12, weight="bold"),
                justify="left",
                anchor="w",
                wraplength=370,
            ).grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 10))

    def _desenhar_grafico_vazio(self):
        for eixo in self._eixos_ativos():
            eixo.clear()
            self._preparar_eixo(eixo)

        if self.modulo_atual == "fadiga":
            textos = (
                "Diagrama sigma_m x sigma_a",
                "Calcule para comparar Goodman, Soderberg e Gerber.",
                "Margem de seguranca",
                "As barras mostram o fator n por criterio.",
            )
        elif self.modulo_atual == "fluencia":
            textos = (
                "Taxa de fluencia x temperatura",
                "Calcule para estimar a sensibilidade termica.",
                "Deformacao acumulada x tempo",
                "A linha mostra a evolucao ate o limite informado.",
            )
        else:
            textos = (
                "FS minimo por material",
                "Compare a margem preliminar de fadiga.",
                "Consumo por fluencia",
                "Compare o consumo do limite informado.",
                "Score geral",
                "Ranking didatico de adequacao preliminar.",
            )

        self._texto_central(self.eixo_1, textos[0], textos[1])
        self._texto_central(self.eixo_2, textos[2], textos[3])
        if self.eixo_3 is not None:
            self._texto_central(self.eixo_3, textos[4], textos[5])
        self.canvas.draw_idle()

    def _texto_central(self, eixo, titulo, subtitulo):
        eixo.text(
            0.5,
            0.55,
            titulo,
            ha="center",
            va="center",
            transform=eixo.transAxes,
            color=TEXT,
            fontsize=13,
            weight="bold",
            wrap=True,
        )
        eixo.text(
            0.5,
            0.43,
            subtitulo,
            ha="center",
            va="center",
            transform=eixo.transAxes,
            color=TEXT_MUTED,
            fontsize=10,
            wrap=True,
        )
        eixo.set_xticks([])
        eixo.set_yticks([])

    def _desenhar_graficos_fadiga(self):
        resultado = self.resultado_atual
        ciclo = resultado["ciclo"]
        limites = resultado["limites"]
        fatores = resultado["fatores"]

        sigma_m = float(ciclo["sigma_m"])
        sigma_a = float(ciclo["sigma_a"])
        limite_fadiga = limites["limite_fadiga_mpa"]
        limite_resistencia = limites["limite_resistencia_mpa"]
        limite_escoamento = limites["limite_escoamento_mpa"]

        x_min = min(0.0, sigma_m * 1.2)
        x_max = max(limite_resistencia, limite_escoamento, sigma_m * 1.25, 1.0) * 1.08
        xs = np.linspace(x_min, x_max, 360)
        xs_tracao = np.maximum(xs, 0.0)

        goodman = np.maximum(
            limite_fadiga * (1 - xs_tracao / limite_resistencia),
            0.0,
        )
        soderberg = np.maximum(
            limite_fadiga * (1 - xs_tracao / limite_escoamento),
            0.0,
        )
        gerber = np.maximum(
            limite_fadiga * (1 - (xs_tracao / limite_resistencia) ** 2),
            0.0,
        )
        y_max = max(limite_fadiga * 1.28, sigma_a * 1.28, 1.0)

        self.eixo_1.clear()
        self._preparar_eixo(self.eixo_1)
        self.eixo_1.fill_between(
            xs,
            0,
            soderberg,
            color=SUCCESS,
            alpha=0.10,
            label="Regiao segura conservadora",
        )
        self.eixo_1.fill_between(
            xs,
            gerber,
            y_max,
            color=DANGER,
            alpha=0.07,
            label="Acima do limite Gerber",
        )
        self.eixo_1.plot(xs, gerber, label="Gerber", color=SUCCESS, linewidth=2.6)
        self.eixo_1.plot(xs, goodman, label="Goodman", color=ACCENT, linewidth=2.4)
        self.eixo_1.plot(xs, soderberg, label="Soderberg", color=WARNING, linewidth=2.4)
        self.eixo_1.axvline(sigma_m, color=TEXT_MUTED, linestyle=":", linewidth=1, alpha=0.8)
        self.eixo_1.axhline(sigma_a, color=TEXT_MUTED, linestyle=":", linewidth=1, alpha=0.8)
        self.eixo_1.scatter(
            [sigma_m],
            [sigma_a],
            label="Ponto analisado",
            color=TEXT,
            edgecolor=ACCENT,
            linewidth=2,
            s=86,
            zorder=6,
        )
        self.eixo_1.annotate(
            f"({sigma_m:.0f}, {sigma_a:.0f}) MPa",
            xy=(sigma_m, sigma_a),
            xytext=(12, 12),
            textcoords="offset points",
            color=TEXT,
            fontsize=9,
            bbox={
                "boxstyle": "round,pad=0.35",
                "facecolor": PLOT_BG,
                "edgecolor": BORDER,
                "alpha": 0.92,
            },
        )
        self.eixo_1.set_title("Diagrama de fadiga", color=TEXT, fontsize=13, weight="bold")
        self.eixo_1.set_xlabel("Tensao media sigma_m [MPa]", color=TEXT_MUTED)
        self.eixo_1.set_ylabel("Tensao alternada sigma_a [MPa]", color=TEXT_MUTED)
        self.eixo_1.set_xlim(x_min, x_max)
        self.eixo_1.set_ylim(0, y_max)
        self._aplicar_legenda(self.eixo_1)

        nomes = list(fatores.keys())
        valores_reais = list(fatores.values())
        valores_finitos = [valor for valor in valores_reais if np.isfinite(valor)]
        topo = max(3.0, max(valores_finitos, default=1.0) * 1.28)
        valores_plot = [valor if np.isfinite(valor) else topo for valor in valores_reais]
        cores = [self._cor_fator_fadiga(valor) for valor in valores_reais]

        self.eixo_2.clear()
        self._preparar_eixo(self.eixo_2)
        self.eixo_2.axhspan(0, 1, color=DANGER, alpha=0.08)
        self.eixo_2.axhspan(1, 2, color=WARNING, alpha=0.08)
        self.eixo_2.axhspan(2, topo, color=SUCCESS, alpha=0.08)
        barras = self.eixo_2.bar(
            nomes,
            valores_plot,
            color=cores,
            width=0.58,
            edgecolor=TEXT,
            linewidth=0.8,
        )
        self.eixo_2.axhline(1.0, color=DANGER, linestyle="--", linewidth=1.2)
        self.eixo_2.axhline(2.0, color=SUCCESS, linestyle="--", linewidth=1.2)
        self.eixo_2.text(2.47, 1.02, "limite", color=DANGER, fontsize=8, va="bottom")
        self.eixo_2.text(2.47, 2.02, "conforto", color=SUCCESS, fontsize=8, va="bottom")
        self.eixo_2.set_title("Fatores de seguranca", color=TEXT, fontsize=13, weight="bold")
        self.eixo_2.set_ylabel("fator n", color=TEXT_MUTED)
        self.eixo_2.set_ylim(0, topo)

        for barra, valor in zip(barras, valores_reais):
            self.eixo_2.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height() + topo * 0.025,
                formatar_fator(valor),
                ha="center",
                va="bottom",
                fontsize=10,
                color=TEXT,
                weight="bold",
            )

        self.canvas.draw_idle()

    def _desenhar_graficos_fluencia(self):
        resultado = self.resultado_atual
        entradas = resultado["entradas"]
        valores = resultado["resultados"]

        tensao = entradas["tensao_mpa"]
        temp_operacao = entradas["temperatura_operacao_c"]
        temp_fusao = entradas["temperatura_fusao_c"]
        tempo_operacao = entradas["tempo_operacao_h"]
        coeficiente_a = entradas["coeficiente_a"]
        expoente_n = entradas["expoente_n"]
        energia_q = entradas["energia_ativacao_kj_mol"]
        deformacao_limite = entradas["deformacao_limite_percentual"]
        taxa = valores["taxa_fluencia_h"]

        t_min = max(20.0, temp_operacao - 300)
        t_max = min(temp_fusao - 1, temp_operacao + 300)
        if t_max <= t_min:
            t_min = max(20.0, temp_operacao * 0.7)
            t_max = temp_operacao * 1.3

        temperaturas = np.linspace(t_min, t_max, 260)
        taxas = np.array(
            [
                calcular_taxa_norton_arrhenius(
                    tensao,
                    temperatura,
                    coeficiente_a,
                    expoente_n,
                    energia_q,
                )
                for temperatura in temperaturas
            ]
        )

        self.eixo_1.clear()
        self._preparar_eixo(self.eixo_1)
        self.eixo_1.plot(temperaturas, taxas, color=ACCENT, linewidth=2.6)
        self.eixo_1.scatter(
            [temp_operacao],
            [taxa],
            color=TEXT,
            edgecolor=ACCENT,
            linewidth=2,
            s=84,
            zorder=5,
        )
        self.eixo_1.set_yscale("log")
        self.eixo_1.set_title("Taxa de fluencia", color=TEXT, fontsize=13, weight="bold")
        self.eixo_1.set_xlabel("Temperatura [C]", color=TEXT_MUTED)
        self.eixo_1.set_ylabel("taxa [1/h]", color=TEXT_MUTED)
        self.eixo_1.axvline(temp_operacao, color=TEXT_MUTED, linestyle=":", linewidth=1)
        self.eixo_1.annotate(
            formatar_cientifico(taxa),
            xy=(temp_operacao, taxa),
            xytext=(12, 12),
            textcoords="offset points",
            color=TEXT,
            fontsize=9,
            bbox={
                "boxstyle": "round,pad=0.35",
                "facecolor": PLOT_BG,
                "edgecolor": BORDER,
                "alpha": 0.92,
            },
        )

        tempo_limite = valores["tempo_limite_h"]
        tempo_plot_max = max(tempo_operacao * 1.2, min(tempo_limite, tempo_operacao * 3))
        if not np.isfinite(tempo_plot_max) or tempo_plot_max <= 0:
            tempo_plot_max = max(tempo_operacao, 1.0)

        tempos = np.linspace(0, tempo_plot_max, 260)
        deformacoes = taxa * tempos * 100

        self.eixo_2.clear()
        self._preparar_eixo(self.eixo_2)
        self.eixo_2.plot(tempos, deformacoes, color=ACCENT, linewidth=2.6, label="deformacao")
        self.eixo_2.axhline(
            deformacao_limite,
            color=SUCCESS,
            linestyle="--",
            linewidth=1.4,
            label="limite informado",
        )
        self.eixo_2.scatter(
            [tempo_operacao],
            [valores["deformacao_percentual"]],
            color=TEXT,
            edgecolor=ACCENT,
            linewidth=2,
            s=84,
            zorder=5,
        )
        self.eixo_2.fill_between(
            tempos,
            0,
            deformacoes,
            color=ACCENT,
            alpha=0.12,
        )
        self.eixo_2.set_title("Deformacao acumulada", color=TEXT, fontsize=13, weight="bold")
        self.eixo_2.set_xlabel("Tempo [h]", color=TEXT_MUTED)
        self.eixo_2.set_ylabel("deformacao [%]", color=TEXT_MUTED)
        self._aplicar_legenda(self.eixo_2)

        self.canvas.draw_idle()

    def _desenhar_graficos_dashboard(self):
        ranking = self.resultado_atual
        nomes = [self._abreviar(nome, 14) for nome in ranking["material"]]
        posicoes = np.arange(len(ranking))

        fs = ranking["menor_fs_fadiga"].to_numpy(dtype=float)
        consumo = ranking["consumo_fluencia_pct"].to_numpy(dtype=float)
        score = ranking["score_total"].to_numpy(dtype=float)

        self.eixo_1.clear()
        self._preparar_eixo(self.eixo_1)
        fs_plot, topo_fs = self._valores_plot(fs, minimo_topo=3.0)
        barras_fs = self.eixo_1.bar(
            posicoes,
            fs_plot,
            color=[self._cor_fator_fadiga(valor) for valor in fs],
            edgecolor=TEXT,
            linewidth=0.7,
        )
        self.eixo_1.axhline(1, color=DANGER, linestyle="--", linewidth=1.1)
        self.eixo_1.axhline(2, color=SUCCESS, linestyle="--", linewidth=1.1)
        self.eixo_1.set_title("Fadiga por material", color=TEXT, fontsize=12, weight="bold")
        self.eixo_1.set_ylabel("menor fator n", color=TEXT_MUTED)
        self.eixo_1.set_ylim(0, topo_fs)
        self._configurar_rotulos_x(self.eixo_1, posicoes, nomes)
        self._rotular_barras(self.eixo_1, barras_fs, fs, topo_fs, "{:.2f}")

        self.eixo_2.clear()
        self._preparar_eixo(self.eixo_2)
        consumo_plot, topo_consumo = self._valores_consumo_dashboard(consumo)
        barras_consumo = self.eixo_2.bar(
            posicoes,
            consumo_plot,
            color=[self._cor_consumo_dashboard(valor) for valor in consumo],
            edgecolor=TEXT,
            linewidth=0.7,
        )
        self.eixo_2.axhline(100, color=DANGER, linestyle="--", linewidth=1.1)
        self.eixo_2.set_title("Consumo por fluencia", color=TEXT, fontsize=12, weight="bold")
        self.eixo_2.set_ylabel("consumo [%]", color=TEXT_MUTED)
        self.eixo_2.set_ylim(0, topo_consumo)
        self._configurar_rotulos_x(self.eixo_2, posicoes, nomes)
        self._rotular_barras(self.eixo_2, barras_consumo, consumo, topo_consumo, "{:.1f}%")

        self.eixo_3.clear()
        self._preparar_eixo(self.eixo_3)
        barras_score = self.eixo_3.bar(
            posicoes,
            score,
            color=[self._cor_score_dashboard(valor) for valor in score],
            edgecolor=TEXT,
            linewidth=0.7,
        )
        self.eixo_3.axhline(0.50, color=WARNING, linestyle="--", linewidth=1.1)
        self.eixo_3.axhline(0.75, color=SUCCESS, linestyle="--", linewidth=1.1)
        self.eixo_3.set_title("Score geral", color=TEXT, fontsize=12, weight="bold")
        self.eixo_3.set_ylabel("score 0-1", color=TEXT_MUTED)
        self.eixo_3.set_ylim(0, 1.05)
        self._configurar_rotulos_x(self.eixo_3, posicoes, nomes)
        self._rotular_barras(self.eixo_3, barras_score, score, 1.05, "{:.2f}")

        self.canvas.draw_idle()

    def _preparar_eixo(self, eixo):
        eixo.set_facecolor(PLOT_PANEL)
        eixo.grid(True, color=GRID, alpha=0.45, linewidth=0.8)
        eixo.tick_params(colors=TEXT_MUTED, labelsize=9)
        for spine in eixo.spines.values():
            spine.set_color(BORDER)
        eixo.title.set_color(TEXT)
        eixo.xaxis.label.set_color(TEXT_MUTED)
        eixo.yaxis.label.set_color(TEXT_MUTED)

    def _eixos_ativos(self):
        eixos = [self.eixo_1, self.eixo_2]

        if self.eixo_3 is not None:
            eixos.append(self.eixo_3)

        return eixos

    def _aplicar_legenda(self, eixo):
        legenda = eixo.legend(
            fontsize=8,
            loc="best",
            frameon=True,
            facecolor=PLOT_BG,
            edgecolor=BORDER,
        )
        for texto in legenda.get_texts():
            texto.set_color(TEXT)

    def _ler_float(self, chave, campo):
        texto = self.entrada_vars[chave].get().strip().replace(",", ".")

        if not texto:
            raise ValueError(f"Informe a {campo}.")

        try:
            return float(texto)
        except ValueError as erro:
            raise ValueError(f"Valor invalido para {campo}.") from erro

    def _material_selecionado(self):
        return self.material_por_opcao.get(self.material_var.get())

    def _ao_trocar_material(self, _opcao):
        if self.modulo_atual == "fluencia":
            self._aplicar_preset_fluencia()
        self._atualizar_material_card()

    def _preset_material_atual(self):
        material = self._material_selecionado()
        nome = "" if material is None else material["material"]
        return obter_preset_fluencia(nome)

    def _aplicar_preset_fluencia(self):
        if self.modulo_atual != "fluencia":
            return

        preset = self._preset_material_atual()
        valores = {
            "temperatura_fusao_c": f"{preset['temperatura_fusao_c']:.0f}",
            "coeficiente_a": f"{preset['coeficiente_a']:.3e}",
            "expoente_n": f"{preset['expoente_n']:.2f}",
            "energia_ativacao_kj_mol": f"{preset['energia_ativacao_kj_mol']:.0f}",
        }

        for chave, valor in valores.items():
            if chave in self.entrada_vars:
                self.entrada_vars[chave].set(valor)

    def _atualizar_material_card(self):
        material = self._material_selecionado()

        if self.modulo_atual == "dashboard":
            self.material_info_label.configure(
                text="Dashboard compara todos os materiais cadastrados no CSV."
            )
            return

        if material is None:
            self.material_info_label.configure(text="Nenhum material carregado.")
            return

        if self.modulo_atual == "fadiga":
            texto = "\n".join(
                [
                    f"{material['material']}",
                    f"Se  {float(material['limite_fadiga_mpa']):.0f} MPa",
                    f"Sut {float(material['limite_resistencia_mpa']):.0f} MPa",
                    f"Sy  {float(material['limite_escoamento_mpa']):.0f} MPa",
                ]
            )
        else:
            preset = self._preset_material_atual()
            texto = "\n".join(
                [
                    f"{material['material']}",
                    f"Tf estimada {preset['temperatura_fusao_c']:.0f} C",
                    f"A {preset['coeficiente_a']:.2e}",
                    f"n {preset['expoente_n']:.2f} | Q {preset['energia_ativacao_kj_mol']:.0f} kJ/mol",
                ]
            )

        self.material_info_label.configure(text=texto)

    def _set_status(self, texto, tipo):
        cores = {
            "ok": SUCCESS,
            "erro": DANGER,
            "info": TEXT_MUTED,
        }
        self.status_label.configure(text=texto, text_color=cores.get(tipo, TEXT_MUTED))

    def _set_status_pill(self, texto, cor, text_color=TEXT):
        self.status_pill.configure(text=texto, fg_color=cor, text_color=text_color)

    def _atualizar_status_pill_resultado(self):
        if self.modulo_atual == "fadiga":
            menor = min(self.resultado_atual["fatores"].values())
            if menor >= 2:
                self._set_status_pill("Fadiga: baixo risco", PILL_OK)
            elif menor >= 1:
                self._set_status_pill("Fadiga: atencao", PILL_WARN)
            else:
                self._set_status_pill("Fadiga: critico", PILL_CRIT, PILL_CRIT_TEXT)
            return

        if self.modulo_atual == "dashboard":
            score = float(self.resultado_atual.iloc[0]["score_total"])
            if score >= 0.75:
                self._set_status_pill("Dashboard: bom preliminar", PILL_OK)
            elif score >= 0.50:
                self._set_status_pill("Dashboard: cautela", PILL_WARN)
            else:
                self._set_status_pill("Dashboard: critico", PILL_CRIT, PILL_CRIT_TEXT)
            return

        consumo = self.resultado_atual["resultados"]["consumo_limite_percentual"]
        if consumo < 50:
            self._set_status_pill("Fluencia: baixo risco", PILL_OK)
        elif consumo < 100:
            self._set_status_pill("Fluencia: atencao", PILL_WARN)
        else:
            self._set_status_pill("Fluencia: critico", PILL_CRIT, PILL_CRIT_TEXT)

    def _resumo_fadiga(self, menor_fator):
        if menor_fator >= 2:
            return "A margem minima ficou acima de 2. O resultado preliminar e confortavel."

        if menor_fator >= 1:
            return "A margem minima ficou entre 1 e 2. Vale revisar carregamento e material."

        return "A margem minima ficou abaixo de 1. Ha indicio preliminar de falha."

    def _resumo_fluencia(self, consumo):
        if consumo < 50:
            return "O consumo estimado do limite de deformacao ficou baixo."

        if consumo < 100:
            return "O consumo estimado esta proximo do limite informado."

        return "O limite de deformacao informado foi excedido na estimativa."

    def _formatar_valor_criterio_fluencia(self, criterio, valor):
        if criterio == "Temperatura homologa":
            return f"{valor:.3f}"

        if criterio == "Taxa estimada":
            return formatar_cientifico(valor)

        return f"{valor:.1f}%"

    def _formatar_horas(self, horas):
        if horas == float("inf"):
            return "infinito"

        if horas >= 8760:
            return f"{horas / 8760:.2f} anos"

        return f"{horas:.0f} h"

    def _abreviar(self, texto, tamanho):
        texto = str(texto)

        if len(texto) <= tamanho:
            return texto

        return texto[: tamanho - 3] + "..."

    def _configurar_rotulos_x(self, eixo, posicoes, nomes):
        eixo.set_xticks(posicoes)
        eixo.set_xticklabels(nomes, rotation=35, ha="right", color=TEXT_MUTED, fontsize=8)

    def _rotular_barras(self, eixo, barras, valores, topo, formato):
        for barra, valor in zip(barras, valores):
            if np.isfinite(valor):
                rotulo = formato.format(valor)
            else:
                rotulo = "inf"

            eixo.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height() + topo * 0.025,
                rotulo,
                ha="center",
                va="bottom",
                fontsize=8,
                color=TEXT,
                weight="bold",
            )

    def _valores_plot(self, valores, minimo_topo):
        finitos = [valor for valor in valores if np.isfinite(valor)]
        topo = max(minimo_topo, max(finitos, default=1.0) * 1.25)
        valores_plot = np.array(
            [valor if np.isfinite(valor) else topo for valor in valores],
            dtype=float,
        )
        return valores_plot, topo

    def _valores_consumo_dashboard(self, valores):
        finitos = [valor for valor in valores if np.isfinite(valor)]
        maior_finito = max(finitos, default=1.0)

        if maior_finito > 120:
            topo = 130.0
            valores_plot = np.array(
                [
                    min(valor, 120.0) if np.isfinite(valor) else 120.0
                    for valor in valores
                ],
                dtype=float,
            )
            return valores_plot, topo

        topo = max(120.0, maior_finito * 1.25)
        valores_plot = np.array(
            [valor if np.isfinite(valor) else topo for valor in valores],
            dtype=float,
        )
        return valores_plot, topo

    def _cor_fator_fadiga(self, valor):
        if valor >= 2:
            return SUCCESS

        if valor >= 1:
            return WARNING

        return DANGER

    def _cor_criterio_fluencia(self, criterio, valor):
        if criterio == "Temperatura homologa":
            if valor < 0.30:
                return SUCCESS
            if valor < 0.50:
                return WARNING
            return DANGER

        if criterio == "Taxa estimada":
            if valor < 1e-10:
                return SUCCESS
            if valor < 1e-7:
                return WARNING
            return DANGER

        if valor < 50:
            return SUCCESS
        if valor < 100:
            return WARNING
        return DANGER

    def _cor_consumo_dashboard(self, valor):
        if not np.isfinite(valor):
            return DANGER

        if valor < 50:
            return SUCCESS

        if valor < 100:
            return WARNING

        return DANGER

    def _cor_score_dashboard(self, valor):
        if valor >= 0.75:
            return SUCCESS

        if valor >= 0.50:
            return WARNING

        return DANGER

    def _limpar_container(self, container):
        for widget in container.winfo_children():
            widget.destroy()
