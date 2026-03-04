from gui import abrir_interface
import cenarios
import tkinter as tk


def depois_da_escolha(tipo_filtro: str, config: str, topologia: str, params: dict):
    # executa cálculos normalmente
    resultado = cenarios.executar(tipo_filtro, config, topologia, params)

    prot = resultado.get("protótipo") or {}
    topo_res = resultado.get("topologia_result") or {}

    H_str = prot.get("H_str", "")
    ordem = prot.get("ordem", topo_res.get("ordem", ""))

    # monta texto do resumo
    texto = ""
    texto += "=== RESUMO DO PROJETO ===\n\n"
    texto += f"Tipo de filtro: {tipo_filtro}\n"
    texto += f"Configuração: {config}\n"
    texto += f"Topologia: {topologia}\n"
    texto += f"Parâmetros de entrada: {params}\n\n"
    texto += f"Ordem do filtro: {ordem}\n\n"
    texto += "Função de transferência H(s):\n"
    texto += f"{H_str}\n\n"

    estagios = topo_res.get("estagios") or []
    if estagios:
        texto += "Estágios Sallen-Key:\n"
        for i, e in enumerate(estagios, start=1):
            texto += (
                f"\nEstágio {i}:\n"
                f"  f0 = {e['f0']:.2f} Hz, Q = {e['Q']:.3f}\n"
                f"  R1 = {e['R1']:.1f} Ω, R2 = {e['R2']:.1f} Ω\n"
                f"  C1 = {e['C1']*1e9:.1f} nF, C2 = {e['C2']*1e9:.1f} nF\n"
                f"  K  = {e['K']:.2f}\n"
            )
    else:
        texto += "Sem dados de estágios (talvez topologia não implementada).\n"

    # cria janela de saída2
    # se você já tiver um root em gui.py, isso ainda funciona porque Toplevel usa o root existente
    janela = tk.Toplevel()
    janela.title("Resultado do projeto de filtro")

    txt = tk.Text(janela, width=90, height=30)
    txt.pack(padx=10, pady=10)
    txt.insert("1.0", texto)
    txt.configure(state="disabled")  # somente leitura

    # botão para fechar a janela de resultado
    btn_fechar = tk.Button(janela, text="Fechar", command=janela.destroy)
    btn_fechar.pack(pady=(0, 10))


def main():
    abrir_interface(depois_da_escolha)


if __name__ == '__main__':
    main()
