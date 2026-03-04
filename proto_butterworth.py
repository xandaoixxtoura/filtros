# proto_butterworth.py
import numpy as np
import sympy as sp
import control as ct
import matplotlib.pyplot as plt


def butterworth_pf_analog(Amin: float, Amax: float, Wp1: float, Wp2: float):
    """
    Aqui eu construo o protótipo analógico Butterworth passa-faixa.

    Eu recebo as duas frequências de passagem (inferior e superior) em rad/s,
    calculo automaticamente a frequência central e a largura de banda,
    e a partir disso faço a transformação do protótipo passa-baixa.

    Entradas:
      Amin : atenuação mínima na banda de rejeição (dB)
      Amax : atenuação máxima na banda de passagem (dB)
      Wp1  : frequência de passagem inferior (rad/s)
      Wp2  : frequência de passagem superior (rad/s)

    Saída:
      H_tf : função de transferência passa-faixa (control.tf)
      n    : ordem do protótipo Butterworth de referência
    """

    s = sp.symbols('s')

    # Frequência central e largura de banda a partir das duas frequências de passagem.
    Wo = np.sqrt(Wp1 * Wp2)          # frequência angular central
    Beta = Wp2 - Wp1                 # largura de banda em rad/s

    # Eu normalizo o passa-faixa em torno de Wo e Beta.
    # As especificações Amin e Amax continuam sendo usadas como no passa-baixa.
    Wp = 1.0

    # Aqui eu escolho uma frequência de stopband normalizada para o protótipo
    # (por enquanto fixo, para simplificar). Mais tarde posso expor isso na GUI.
    Ws_norm = 2.0  # por exemplo, Ws/Wp = 2

    # Ripple na banda de passagem.
    Ep = np.sqrt(10**(0.1 * Amax) - 1)

    # Mesma fórmula de ordem de Butterworth, usando Ws_norm/Wp.
    num_n = np.log10((10**(0.1 * Amin) - 1) / (Ep**2))
    den_n = np.log10(Ws_norm**2)
    n_teorico = num_n / den_n
    n = int(np.ceil(n_teorico))
    k = n

    print(f"[Butterworth PF] n_teórico = {n_teorico}, n = {n}")

    if n <= 0:
        raise ValueError("Ordem n <= 0: especificações inválidas para Butterworth passa-faixa.")

    # Transformação passa-baixa -> passa-faixa na variável simbólica s.
    # Forma padrão: s_LP = (s^2 + Wo^2) / (Beta * s).
    s_sub = (Ep**(1/n) / Wp) * (s**2 + Wo**2) / (Beta * s)

    # Polos do protótipo Butterworth passa-baixa normalizado.
    v_S = []
    for k_temp in range(1, k + 1):
        ang = (np.pi / 2) * (2 * k_temp + n - 1) / n
        v_S.append(np.cos(ang) + 1j * np.sin(ang))

    # A partir das raízes eu monto o polinômio do denominador substituído.
    A = sp.Integer(1)
    for root in v_S:
        A = sp.expand(A * (s_sub - root))

    A = sp.expand(A * s**k)

    den_coeffs = sp.Poly(A, s).all_coeffs()
    den_complex = np.array([complex(sp.N(c))
                            for c in den_coeffs], dtype=np.complex128)

    # Forço coeficientes reais, descartando pequenas partes imaginárias numéricas.
    den = np.real_if_close(den_complex, tol=1e-6).astype(float)

    # Caso especial n = 1.
    if n == 1:
        den = np.real_if_close(den)
        if np.isclose(den[0], 0):
            den = den[1:]

    # Numerador do passa-faixa: 1 seguido de zeros até a ordem k.
    num = np.concatenate(([1.0], np.zeros(k)))

    H_tf = ct.tf(num, den)
    H_tf = ct.minreal(H_tf, verbose=False)

    print("[Butterworth PF] H(s) =", H_tf)

    # Bode não bloqueante para o protótipo passa-faixa.
    ct.bode_plot(H_tf, dB=True)
    plt.grid(True, which='both', linestyle='--')
    plt.show(block=False)

    return H_tf, n


def butterworth_pb_analog(Amin: float, Amax: float, Ws: float, Wp: float):
    """
    Aqui eu construo o protótipo analógico Butterworth passa-baixa.
    Eu uso as especificações de atenuação (Amin, Amax) e as frequências (Ws, Wp)
    para calcular a ordem do filtro e a função de transferência H(s).
    """

    s = sp.symbols('s')

    # A partir de Amax eu calculo o ripple máximo na banda de passagem.
    Ep = np.sqrt(10**(0.1 * Amax) - 1)

    # Defino a razão de frequências de stopband e passband.
    Omega_s = Ws / Wp

    # Aplico a fórmula da ordem teórica do Butterworth de baixa frequência.
    num_n = np.log10((10**(0.1 * Amin) - 1) / (Ep**2))
    den_n = np.log10(Omega_s**2)
    n_teorico = num_n / den_n
    n = int(np.ceil(n_teorico))

    if n <= 0:
        raise ValueError("Ordem Butterworth n <= 0: especificações inválidas.")

    print(f"[Butterworth PB] n_teorico = {n_teorico}, n = {n}")

    # Aqui eu calculo a frequência de corte aproximada para o protótipo Butterworth.
    Wc = Wp / (Ep**(1.0 / n))
    print(f"[Butterworth PB] Wc = {Wc} rad/s")

    # Neste laço eu encontro os polos do Butterworth no semi-plano esquerdo.
    v_S = []
    for k in range(1, 2 * n + 1):
        ang = (np.pi / (2 * n)) * (2 * k - 1)
        sk = np.exp(1j * ang)
        if sk.real < 0:
            v_S.append(sk)

    # Depois eu escalo os polos pela frequência de corte Wc.
    v_S = [Wc * p for p in v_S]

    # Aqui eu monto o polinômio do denominador como produto (s - p_k).
    A_poly = 1
    for root in v_S:
        A_poly = sp.expand(A_poly * (s - root))

    den_coeffs = sp.Poly(A_poly, s).all_coeffs()
    den_complex = np.array([complex(sp.N(c)) for c in den_coeffs],
                           dtype=np.complex128)

    # Eu forço os coeficientes a serem reais, descartando pequenas partes imaginárias numéricas.
    den = np.real_if_close(den_complex, tol=1e-6).astype(float)

    # Escolho o numerador para ter ganho aproximadamente igual a 1 em baixa frequência.
    num = np.array([den[-1]], dtype=float)

    H_tf = ct.tf(num, den)
    H_tf = ct.minreal(H_tf, verbose=False)

    print("[Butterworth PB] H(s) =", H_tf)

    # Aqui eu ploto o diagrama de Bode do protótipo passa-baixa sem bloquear a interface.
    ct.bode_plot(H_tf, dB=True)
    plt.grid(True, which='both', linestyle='--')
    plt.show(block=False)

    return H_tf, n


def butterworth_pha_analog(Amin: float, Amax: float, Ws: float, Wp: float):
    """
    Aqui eu construo o protótipo analógico Butterworth passa-alta.
    Eu reaproveito a lógica do passa-baixa, mas aplico a transformação
    analógica passa-baixa -> passa-alta nos polos.
    """

    s = sp.symbols('s')

    # Mesma conta de ripple do passa-baixa.
    Ep = np.sqrt(10**(0.1 * Amax) - 1)

    # Para passa-alta, uso a razão Wp/Ws em vez de Ws/Wp.
    Omega = Wp / Ws

    # Mesma fórmula da ordem teórica do Butterworth, mas com Omega invertido.
    num_n = np.log10((10**(0.1 * Amin) - 1) / (Ep**2))
    den_n = np.log10(Omega**2)
    n_teorico = num_n / den_n
    n = int(np.ceil(n_teorico))

    if n <= 0:
        raise ValueError(f"Ordem Butterworth n <= 0: especificações inválidas para passa-alta. n_teorico={n_teorico}")

    print(f"[Butterworth PH] n_teorico = {n_teorico}, n = {n}")

    # Mesma expressão de Wc do passa-baixa.
    Wc = Wp / (Ep**(1.0 / n))
    print(f"[Butterworth PH] Wc = {Wc} rad/s")

    # Polos do protótipo passa-baixa (igual butterworth_pb_analog, sem o Wc ainda).
    v_S_lp = []
    for k in range(1, 2 * n + 1):
        ang = (np.pi / (2 * n)) * (2 * k - 1)
        sk = np.exp(1j * ang)
        if sk.real < 0:
            v_S_lp.append(sk)

    # Escalo os polos pela frequência de corte Wc (protótipo passa-baixa).
    v_S_lp = [Wc * p for p in v_S_lp]

    # Transformação passa-baixa -> passa-alta nos polos.
    v_S_hp = [Wc**2 / p for p in v_S_lp]

    # Denominador do passa-alta: ∏ (s - p_hp).
    A_poly = 1
    for root in v_S_hp:
        A_poly = sp.expand(A_poly * (s - root))

    den_coeffs = sp.Poly(A_poly, s).all_coeffs()
    den_complex = np.array([complex(sp.N(c)) for c in den_coeffs],
                           dtype=np.complex128)

    den = np.real_if_close(den_complex, tol=1e-6).astype(float)

    # Numerador para ganho ~1 em alta frequência: s^n normalizado.
    num = np.zeros_like(den)
    num[0] = 1.0  # s^n

    H_hp = ct.tf(num, den)
    H_hp = ct.minreal(H_hp, verbose=False)

    print("[Butterworth PH] H_hp(s) =", H_hp)

    ct.bode_plot(H_hp, dB=True)
    plt.grid(True, which='both', linestyle='--')
    plt.show(block=False)

    return H_hp, n
