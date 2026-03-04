# cenarios.py
import numpy as np
from proto_butterworth import (
    butterworth_pf_analog,
    butterworth_pb_analog,
    butterworth_pha_analog,
)
from proto_chebyshev import (
    chebyshev_pb_analog,
    chebyshev_pha_analog,
    chebyshev_pf_analog,
)
import topologia_sallen_key as topo_sk
import topologia_mfb as topo_mfb


def executar(tipo_filtro: str, config: str, topologia: str, params: dict):
    """
    Esta função é o orquestrador do projeto:
    ela recebe o tipo de filtro, a aproximação, a topologia e os parâmetros
    e decide qual protótipo analógico e qual topologia de implementação chamar.

    Entradas:
      Amin, Amax em dB
      Ws, Wp em Hz

    Saída:
      Um dict com os dados do protótipo e da topologia (quando implementada),
      para ser usado pela interface de saída.
    """

    Amin = float(params['Amin'])
    Amax = float(params['Amax'])
    Ws_hz = float(params['Ws'])
    Wp_hz = float(params['Wp'])

    # Aqui eu converto as frequências de Hz para rad/s, pois os protótipos trabalham em rad/s.
    Ws = 2 * np.pi * Ws_hz
    Wp = 2 * np.pi * Wp_hz

    print(f">> [CENÁRIO] tipo={tipo_filtro}, config={config}, topo={topologia}")
    print(f"   Amin={Amin}, Amax={Amax}, Ws={Ws_hz} Hz, Wp={Wp_hz} Hz")

    resultado = {
        "tipo_filtro": tipo_filtro,
        "config": config,
        "topologia": topologia,
        "Amin": Amin,
        "Amax": Amax,
        "Ws_hz": Ws_hz,
        "Wp_hz": Wp_hz,
        "protótipo": None,
        "topologia_result": None,
        "mensagem": "",
    }

    # -------- Butterworth --------

    # Caso 1: Butterworth passa-baixa.
    if config == 'Butterworth' and tipo_filtro == 'passa-baixa':
        H_tf, n = butterworth_pb_analog(Amin, Amax, Ws, Wp)
        resultado["protótipo"] = {"H_str": str(H_tf), "n": n}
        resultado["topologia_result"] = _chamar_topologia(topologia, tipo_filtro, H_tf, n)
        return resultado

    # Caso 2: Butterworth passa-alta.
    if config == 'Butterworth' and tipo_filtro == 'passa-alta':
        H_tf, n = butterworth_pha_analog(Amin, Amax, Ws, Wp)
        resultado["protótipo"] = {"H_str": str(H_tf), "n": n}
        resultado["topologia_result"] = _chamar_topologia(topologia, tipo_filtro, H_tf, n)
        return resultado

    # Caso 3: Butterworth passa-faixa.
    if config == 'Butterworth' and tipo_filtro == 'passa-faixa':
        # Aqui eu interpreto Ws_hz como frequência de passagem inferior (fp1)
        # e Wp_hz como frequência de passagem superior (fp2).
        H_tf, n = butterworth_pf_analog(Amin, Amax, Ws, Wp)
        resultado["protótipo"] = {"H_str": str(H_tf), "n": n}
        resultado["topologia_result"] = _chamar_topologia(topologia, tipo_filtro, H_tf, n)
        return resultado

    # -------- Chebyshev --------

    # Caso 4: Chebyshev passa-baixa.
    if config == 'Chebyshev' and tipo_filtro == 'passa-baixa':
        H_tf, n = chebyshev_pb_analog(Amin, Amax, Ws, Wp)
        resultado["protótipo"] = {"H_str": str(H_tf), "n": n}
        resultado["topologia_result"] = _chamar_topologia(topologia, tipo_filtro, H_tf, n)
        return resultado

    # Caso 5: Chebyshev passa-alta.
    if config == 'Chebyshev' and tipo_filtro == 'passa-alta':
        H_tf, n = chebyshev_pha_analog(Amin, Amax, Ws, Wp)
        resultado["protótipo"] = {"H_str": str(H_tf), "n": n}
        resultado["topologia_result"] = _chamar_topologia(topologia, tipo_filtro, H_tf, n)
        return resultado

    # Caso 6: Chebyshev passa-faixa.
    if config == 'Chebyshev' and tipo_filtro == 'passa-faixa':
        # Ws_hz -> frequência de passagem inferior (fp1)
        # Wp_hz -> frequência de passagem superior (fp2)
        H_tf, n = chebyshev_pf_analog(Amin, Amax, Ws, Wp)
        resultado["protótipo"] = {"H_str": str(H_tf), "n": n}
        resultado["topologia_result"] = _chamar_topologia(topologia, tipo_filtro, H_tf, n)
        return resultado

    # Qualquer outra combinação cai aqui como ainda não implementada.
    msg = f"Combinação ainda não implementada: {config}, {tipo_filtro}, {topologia}"
    print(">>", msg)
    resultado["mensagem"] = msg
    return resultado


def _chamar_topologia(topologia: str, tipo_filtro: str, H_tf, n: int):
    """
    Esta função interna só encaminha a função de transferência H(s) e a ordem n
    para a topologia escolhida (Sallen-Key ou MFB), mantendo o código organizado.
    """
    if topologia == 'sallen-key':
        return topo_sk.realizar(tipo_filtro, H_tf, n)
    elif topologia == 'mfb':
        # Aqui eu apenas chamo a função da MFB como placeholder,
        # pois ela ainda não retorna os componentes dimensionados.
        topo_mfb.realizar(tipo_filtro, H_tf, n)
        return {"mensagem": "Topologia MFB ainda não retorna componentes."}
    else:
        print("Topologia desconhecida:", topologia)
        return {"mensagem": "Topologia desconhecida."}
