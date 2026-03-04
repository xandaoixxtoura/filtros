# topologia_sallen_key.py
import numpy as np


C_PADRAO = 10e-9  # 10 nF


def _decompor_em_secoes_lp(H_tf):
    """
    Aqui eu pego o denominador do protótipo H(s)
    e decomponho em seções de 1ª e 2ª ordem, a partir dos polos.
    Essa decomposição é a base para dimensionar os estágios Sallen-Key,
    para passa-baixa, passa-alta e passa-faixa.
    """
    # Primeiro eu extraio o denominador como um array 1D de coeficientes reais.
    den = np.asarray(H_tf.den[0][0], dtype=float)
    # Em seguida, normalizo o coeficiente líder para ficar igual a 1.
    den = den / den[0]

    # Aqui eu calculo as raízes do denominador (polos do protótipo).
    raizes = np.roots(den)

    polos_complexos = []
    polos_reais = []
    for p in raizes:
        if abs(p.imag) < 1e-6:
            polos_reais.append(p.real)
        else:
            polos_complexos.append(p)

    usados = np.zeros(len(polos_complexos), dtype=bool)
    secoes = []

    # Nesta parte eu procuro pares de polos complexos conjugados
    # para formar seções de 2ª ordem do tipo (s^2 + a1 s + a0).
    for i, p in enumerate(polos_complexos):
        if usados[i]:
            continue
        conj_idx = None
        for j in range(i + 1, len(polos_complexos)):
            if usados[j]:
                continue
            if abs(polos_complexos[j] - np.conj(p)) < 1e-6:
                conj_idx = j
                break
        if conj_idx is None:
            continue

        usados[i] = True
        usados[conj_idx] = True
        p1 = polos_complexos[i]
        p2 = polos_complexos[conj_idx]

        # A partir do par de polos, eu monto o polinômio de 2ª ordem correspondente.
        a2 = 1.0
        a1 = -(p1 + p2).real
        a0 = (p1 * p2).real

        # A frequência natural w0 e o fator de qualidade Q saem diretamente dos coeficientes.
        w0 = np.sqrt(a0)
        Q = w0 / a1

        secoes.append({
            "tipo": "2ord",
            "w0": float(w0),
            "Q": float(Q),
            "coef": [float(a2), float(a1), float(a0)],
        })

    # Qualquer polo real restante gera uma seção de 1ª ordem (s + wc).
    for pr in polos_reais:
        wc = -pr
        secoes.append({
            "tipo": "1ord",
            "wc": float(wc),
            "coef": [1.0, float(wc)],
        })

    return secoes


def _dimensionar_sallen_key_lp(w0, Q, C=C_PADRAO):
    """
    Aqui eu faço um dimensionamento simples de um estágio Sallen-Key passa-baixa de 2ª ordem,
    assumindo:
      - C1 = C2 = C
      - R1 = R2 = R
      - ganho em malha fechada K = 1.

    A partir de w0 e C, eu encontro R que satisfaz a frequência natural desejada.
    """
    R = 1.0 / (w0 * C)
    K = 1.0
    return {
        "R1": R,
        "R2": R,
        "C1": C,
        "C2": C,
        "K": K,
    }


def _dimensionar_sallen_key_hp(w0, Q, C=C_PADRAO):
    """
    Aqui eu dimensiono um estágio Sallen-Key passa-alta de 2ª ordem,
    fazendo uma versão análoga ao caso passa-baixa e assumindo:
      - C1 = C2 = C
      - R1 = R2 = R
      - ganho em malha fechada K = 1.

    Para o passa-alta simples, a frequência de corte também segue w0 = 1 / (R * C),
    então eu uso a mesma relação para calcular R.
    """
    R = 1.0 / (w0 * C)
    K = 1.0
    return {
        "R1": R,
        "R2": R,
        "C1": C,
        "C2": C,
        "K": K,
    }


def _dimensionar_sallen_key_bp(w0, Q, C=C_PADRAO):
    """
    Aqui eu dimensiono um estágio Sallen-Key passa-faixa de 2ª ordem de forma simplificada,
    assumindo:
      - C1 = C2 = C
      - R1 = R2 = R
      - ganho em malha fechada K = 1.

    Eu uso a mesma relação aproximada w0 ≈ 1 / (R * C) para definir R
    a partir da frequência central dada por w0.
    """
    R = 1.0 / (w0 * C)
    K = 1.0
    return {
        "R1": R,
        "R2": R,
        "C1": C,
        "C2": C,
        "K": K,
    }


def realizar(tipo_filtro: str, H_tf, n: int):
    """
    Aqui eu implemento a topologia Sallen-Key para o protótipo fornecido.

    Atualmente eu trato os casos:
      - passa-baixa (LP)
      - passa-alta (HP)
      - passa-faixa (BP, de forma simplificada)

    Fluxo:
      - Decomponho H(s) em seções de 2ª e 1ª ordem.
      - Para cada seção de 2ª ordem, dimensiono um estágio Sallen-Key
        assumindo C1 = C2 = 10 nF e R1 = R2.
      - Devolvo uma estrutura com a descrição das seções e
        os componentes de cada estágio Sallen-Key.

    Para outros tipos de filtro, eu apenas retorno uma mensagem indicando
    que o dimensionamento ainda não foi implementado.
    """
    resultado = {
        "tipo_filtro": tipo_filtro,
        "H_str": str(H_tf),
        "ordem": n,
        "secoes": [],
        "estagios": [],
    }

    # Aqui eu só aceito, por enquanto, passa-baixa, passa-alta e passa-faixa.
    if tipo_filtro not in ("passa-baixa", "passa-alta", "passa-faixa"):
        resultado["mensagem"] = "Dimensionamento Sallen-Key ainda não implementado para este tipo."
        return resultado

    # Primeiro eu decomponho o protótipo em seções de 1ª e 2ª ordem.
    secoes = _decompor_em_secoes_lp(H_tf)
    if not secoes:
        resultado["mensagem"] = "Não foi possível decompor o denominador em seções."
        return resultado

    # Aqui eu salvo as informações das seções (w0, Q ou wc) em termos de frequência em Hz.
    for sec in secoes:
        if sec["tipo"] == "2ord":
            w0 = sec["w0"]
            Q = sec["Q"]
            f0 = w0 / (2 * np.pi)
            resultado["secoes"].append({
                "tipo": "2ord",
                "w0": w0,
                "Q": Q,
                "f0": f0,
            })
        elif sec["tipo"] == "1ord":
            wc = sec["wc"]
            fc = wc / (2 * np.pi)
            resultado["secoes"].append({
                "tipo": "1ord",
                "wc": wc,
                "fc": fc,
            })

    # Em seguida, para cada seção de 2ª ordem, eu calculo os componentes do estágio Sallen-Key,
    # escolhendo se é passa-baixa, passa-alta ou passa-faixa conforme o tipo de filtro.
    for sec in secoes:
        if sec["tipo"] != "2ord":
            continue
        w0 = sec["w0"]
        Q = sec["Q"]

        if tipo_filtro == "passa-baixa":
            comp = _dimensionar_sallen_key_lp(w0, Q, C_PADRAO)
        elif tipo_filtro == "passa-alta":
            comp = _dimensionar_sallen_key_hp(w0, Q, C_PADRAO)
        else:  # tipo_filtro == "passa-faixa"
            comp = _dimensionar_sallen_key_bp(w0, Q, C_PADRAO)

        f0 = w0 / (2 * np.pi)
        resultado["estagios"].append({
            "f0": f0,
            "Q": Q,
            "R1": comp["R1"],
            "R2": comp["R2"],
            "C1": comp["C1"],
            "C2": comp["C2"],
            "K": comp["K"],
        })

    resultado["mensagem"] = "OK"
    return resultado
