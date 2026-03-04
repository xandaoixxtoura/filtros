# gui.py
import tkinter as tk
from tkinter import ttk


TIPOS_FILTRO = [
    'passa-baixa',
    'passa-alta',
    'passa-faixa',
]

CONFIGS_FILTRO = [
    'Butterworth',
    'Chebyshev',
]

TOPOLOGIAS = [
    'sallen-key',
    'mfb',
]


def abrir_interface(on_escolher):
    """
    Janela única com:
      - Tipo de filtro
      - Configuração (Butterworth / Chebyshev)
      - Topologia (Sallen-key / MFB)
      - Parâmetros: Amin, Amax, Ws, Wp (para todos os casos)

    Campos de parâmetros e botão OK só são habilitados
    depois que tipo e configuração forem escolhidos.
    """

    root = tk.Tk()
    root.title('Projeto de Filtros Analógicos')

    # --------- VARIÁVEIS DE ESTADO ---------
    var_tipo = tk.StringVar(value='')
    var_conf = tk.StringVar(value='')
    var_topo = tk.StringVar(value=TOPOLOGIAS[0])

    entradas = {}
    labels_widgets = {}
    btn_ok = None

    # --------- CALLBACK PARA HABILITAR PARÂMETROS ---------
    def atualizar_estado_parametros(*args):
        tipo_sel = var_tipo.get()
        conf_sel = var_conf.get()

        habilitar = bool(tipo_sel) and bool(conf_sel)
        state = 'normal' if habilitar else 'disabled'

        for ent in entradas.values():
            ent.config(state='disabled')

        if btn_ok is not None:
            btn_ok.config(state='disabled')

        if not habilitar:
            return

        # habilita todos os parâmetros (Amin, Amax, Ws, Wp) para todos os casos
        for nome in ['Amin', 'Amax', 'Ws', 'Wp']:
            entradas[nome].config(state=state)

        if btn_ok is not None:
            btn_ok.config(state='normal')

    var_tipo.trace_add('write', atualizar_estado_parametros)
    var_conf.trace_add('write', atualizar_estado_parametros)

    # ----- FRAME: Tipo de filtro -----
    frame_tipo = ttk.LabelFrame(root, text='Tipo de filtro')
    frame_tipo.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

    for i, tipo in enumerate(TIPOS_FILTRO):
        ttk.Radiobutton(
            frame_tipo,
            text=tipo.capitalize().replace('-', ' '),
            value=tipo,
            variable=var_tipo
        ).grid(row=i, column=0, sticky='w', padx=5, pady=2)

    # ----- FRAME: Configuração -----
    frame_conf = ttk.LabelFrame(root, text='Configuração do filtro')
    frame_conf.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

    for i, conf in enumerate(CONFIGS_FILTRO):
        ttk.Radiobutton(
            frame_conf,
            text=conf,
            value=conf,
            variable=var_conf
        ).grid(row=i, column=0, sticky='w', padx=5, pady=2)

    # ----- FRAME: Topologia -----
    frame_topo = ttk.LabelFrame(root, text='Topologia')
    frame_topo.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')

    for i, topo in enumerate(TOPOLOGIAS):
        ttk.Radiobutton(
            frame_topo,
            text=topo,
            value=topo,
            variable=var_topo
        ).grid(row=i, column=0, sticky='w', padx=5, pady=2)

    # ----- FRAME: Parâmetros -----
    frame_param = ttk.LabelFrame(root, text='Parâmetros')
    frame_param.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

    campos = [
        ('Amin', 'dB'),
        ('Amax', 'dB'),
        ('Ws', 'Hz'),
        ('Wp', 'Hz'),
    ]

    for i, (nome, unidade) in enumerate(campos):
        lbl = ttk.Label(frame_param, text=f"{nome}:")
        lbl.grid(row=i, column=0, sticky='e', padx=5, pady=4)

        ent = ttk.Entry(frame_param, width=15, state='disabled')
        ent.grid(row=i, column=1, padx=5, pady=4, sticky='w')

        lbl_uni = ttk.Label(frame_param, text=unidade)
        lbl_uni.grid(row=i, column=2, sticky='w', padx=5, pady=4)

        entradas[nome] = ent
        labels_widgets[nome] = lbl
        labels_widgets[nome + '_uni'] = lbl_uni

    # ----- Botão OK -----
    def confirmar():
        tipo = var_tipo.get()
        conf = var_conf.get()
        topo = var_topo.get()

        params = {
            'Amin': entradas['Amin'].get(),
            'Amax': entradas['Amax'].get(),
            'Ws': entradas['Ws'].get(),
            'Wp': entradas['Wp'].get(),
        }

        root.destroy()
        on_escolher(tipo, conf, topo, params)

    btn_ok = ttk.Button(root, text='OK', command=confirmar, state='disabled')
    btn_ok.grid(row=2, column=0, columnspan=3, pady=15)

    atualizar_estado_parametros()
    root.mainloop()
