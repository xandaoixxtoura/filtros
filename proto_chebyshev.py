# proto_chebyshev.py
import numpy as np
import sympy as sp
import control as ct
import matplotlib.pyplot as plt


def chebyshev_pb_analog(Amin: float, Amax: float, Ws: float, Wp: float):
    """
    Aqui eu construo o protótipo analógico Chebyshev tipo I passa-baixa.
    A função recebe Amin, Amax, Ws e Wp (em dB e rad/s) e devolve H(s) e a ordem n.
    """

    s = sp.symbols('s')

    flg = 0

    # A partir de Amax eu calculo o ripple máximo na banda de passagem (epsilon).
    Ep = np.sqrt(10**(0.1 * Amax) - 1)

    # Defino a razão de frequências normalizada para o Chebyshev.
    Omg = Ws / Wp
    Cn = [1.0]
    n = 0

    # Aqui eu começo testando a atenuação na banda de rejeição para n = 0.
    Amin_t = 10 * np.log10(1 + Ep**2 * (Cn[-1])**2)
    if Amin_t >= Amin:
        flg = 1

    # Se ainda não atendeu Amin, testo para n = 1.
    if flg == 0:
        Cn.append(Omg)
        n = 1
        Amin_t = 10 * np.log10(1 + Ep**2 * (Cn[-1])**2)
        if Amin_t >= Amin:
            flg = 1

    # Se ainda não atendeu, eu aumento n de 2 até no máximo 10,
    # usando a recorrência de Chebyshev para encontrar o polinômio.
    if flg == 0:
        for k in range(3, 11):   # k = 3:1:10
            n = k - 1

            if abs(Omg) <= 1:
                Cn_t = np.cos(n * np.arccos(Omg))
            else:
                Cn_t = np.cosh(n * np.arccosh(Omg))

            Cn.append(Cn_t)
            Cn.append(2 * Omg * Cn[-1] - Cn[-3])

            Amin_t = 10 * np.log10(1 + Ep**2 * (Cn[-1])**2)

            if Amin_t >= Amin:
                flg = 1
                break

    print("[Chebyshev PB] Ordem n =", n)

    # Aqui eu normalizo a variável complexa s pela frequência de passagem Wp.
    s_sub = s / Wp

    # Neste laço eu calculo os polos do Chebyshev tipo I no plano s.
    v_S = []
    for k_temp in range(0, 2 * n):
        ang = (np.pi / 2) * ((1 + 2 * k_temp) / n)

        term1 = np.sin(ang) * np.sinh((1 / n) * np.arcsinh(1 / Ep))
        term2 = np.cos(ang) * np.cosh((1 / n) * np.arcsinh(1 / Ep))

        v_S.append(term1 + 1j * term2)

    # A partir dos polos, eu monto o polinômio do denominador do protótipo.
    A = sp.Integer(1)
    for idx in range(2, len(v_S)):  # k_temp = 3:1:length(v_S) em Octave
        A = sp.expand(A * (s_sub - v_S[idx]))

    den_coeffs = sp.Poly(sp.expand(A), s).all_coeffs()
    den_complex = np.array([complex(sp.N(c))
                            for c in den_coeffs], dtype=np.complex128)

    # Forço coeficientes reais, descartando pequenas partes imaginárias numéricas.
    den = np.real_if_close(den_complex, tol=1e-6).astype(float)

    # Para o Chebyshev de tipo I eu uso numerador unitário.
    num = np.array([1.0])

    H_tf = ct.tf(num, den)
    H_tf = ct.minreal(H_tf, verbose=False)

    print("[Chebyshev PB] H(s) =", H_tf)

    # Aqui eu ploto o diagrama de Bode do protótipo Chebyshev sem bloquear a interface.
    ct.bode_plot(H_tf, dB=True)
    plt.grid(True, which='both', linestyle='--')
    plt.show(block=False)

    return H_tf, n


def chebyshev_pha_analog(Amin: float, Amax: float, Ws: float, Wp: float):
    """
    Aqui eu construo o protótipo analógico Chebyshev tipo I passa-alta.

    Eu uso o mesmo cálculo de ordem do passa-baixa, mas com a razão Wp/Ws
    (pois no passa-alta a transição é na outra borda da banda),
    e depois aplico a transformação passa-baixa -> passa-alta nos polos.
    """

    s = sp.symbols('s')

    # Ripple em passband (epsilon).
    Ep = np.sqrt(10**(0.1 * Amax) - 1)

    # Para passa-alta, uso a razão Wp/Ws em vez de Ws/Wp.
    Omega = Wp / Ws

    # Ordem teórica do Chebyshev (análoga ao passa-baixa, com Omega invertido).
    num_n = np.log10((10**(0.1 * Amin) - 1) / (Ep**2))
    den_n = np.log10(Omega**2)
    n_teorico = num_n / den_n
    n = int(np.ceil(n_teorico))

    if n <= 0:
        raise ValueError(f"Ordem Chebyshev n <= 0: especificações inválidas para passa-alta. n_teorico={n_teorico}")

    print(f"[Chebyshev PH] n_teorico = {n_teorico}, n = {n}")

    # Polos do protótipo LP normalizado em Chebyshev.
    Omg = Ws / Wp  # mesmo Omg usado no passa-baixa, para manter coerência
    Cn = [1.0]
    # (Reutilizar a lógica original aqui seria mais detalhado;
    # para simplificar, eu uso o mesmo processo de polos do PB.)

    # Normalização da variável complexa s pela frequência de passagem Wp.
    s_sub = s / Wp

    v_S = []
    for k_temp in range(0, 2 * n):
        ang = (np.pi / 2) * ((1 + 2 * k_temp) / n)
        term1 = np.sin(ang) * np.sinh((1 / n) * np.arcsinh(1 / Ep))
        term2 = np.cos(ang) * np.cosh((1 / n) * np.arcsinh(1 / Ep))
        v_S.append(term1 + 1j * term2)

    # Polos LP escalados em rad/s (já incluído via s_sub = s/Wp).
    v_S_lp = []
    for idx in range(2, len(v_S)):
        # polos do denominador de (s_sub - v_S[idx]) = 0 -> s = v_S[idx] * Wp
        v_S_lp.append(v_S[idx] * Wp)

    # Transformação passa-baixa -> passa-alta: polos_hp = Wp^2 / polos_lp.
    v_S_hp = [Wp**2 / p for p in v_S_lp]

    # Denominador do passa-alta: ∏ (s - p_hp).
    A_poly = 1
    for root in v_S_hp:
        A_poly = sp.expand(A_poly * (s - root))

    den_coeffs = sp.Poly(A_poly, s).all_coeffs()
    den_complex = np.array([complex(sp.N(c)) for c in den_coeffs],
                           dtype=np.complex128)

    den = np.real_if_close(den_complex, tol=1e-6).astype(float)

    # Numerador unitário em alta frequência (s^n normalizado).
    num = np.zeros_like(den)
    num[0] = 1.0  # s^n

    H_hp = ct.tf(num, den)
    H_hp = ct.minreal(H_hp, verbose=False)

    print("[Chebyshev PH] H_hp(s) =", H_hp)

    ct.bode_plot(H_hp, dB=True)
    plt.grid(True, which='both', linestyle='--')
    plt.show(block=False)

    return H_hp, n


def chebyshev_pf_analog(Amin: float, Amax: float, Wp1: float, Wp2: float):
    """
    Aqui eu construo o protótipo analógico Chebyshev tipo I passa-faixa.

    Eu recebo as duas frequências de passagem (inferior e superior) em rad/s,
    calculo automaticamente a frequência central e a largura de banda,
    e a partir disso faço a transformação lowpass -> bandpass
    usando o protótipo Chebyshev passa-baixa.
    """

    s = sp.symbols('s')

    # Frequência central e largura de banda a partir das duas frequências de passagem.
    Wo = np.sqrt(Wp1 * Wp2)          # frequência angular central
    Beta = Wp2 - Wp1                 # largura de banda em rad/s

    # Normalização: Wp = 1 para o protótipo LP.
    Wp_norm = 1.0
    Ws_norm = 2.0  # por enquanto fixo (como no Butterworth PF)

    # Ripple em passband.
    Ep = np.sqrt(10**(0.1 * Amax) - 1)

    # Cálculo de ordem Chebyshev tipo I (análogo ao PB, com Ws_norm).
    num_n = np.log10((10**(0.1 * Amin) - 1) / (Ep**2))
    den_n = np.log10(Ws_norm**2)
    n_teorico = num_n / den_n
    n = int(np.ceil(n_teorico))

    if n <= 0:
        raise ValueError("Ordem Chebyshev n <= 0: especificações inválidas para passa-faixa.")

    print(f"[Chebyshev PF] n_teorico = {n_teorico}, n = {n}")

    # Polos do protótipo LP Chebyshev normalizado.
    Omg = Ws_norm / Wp_norm
    v_S = []
    for k_temp in range(0, 2 * n):
        ang = (np.pi / 2) * ((1 + 2 * k_temp) / n)
        term1 = np.sin(ang) * np.sinh((1 / n) * np.arcsinh(1 / Ep))
        term2 = np.cos(ang) * np.cosh((1 / n) * np.arcsinh(1 / Ep))
        v_S.append(term1 + 1j * term2)

    # Transformação passa-baixa -> passa-faixa: s_LP = (s^2 + Wo^2) / (Beta * s)
    s_sub = (Ep**(1/n) / Wp_norm) * (s**2 + Wo**2) / (Beta * s)

    A = sp.Integer(1)
    for idx in range(2, len(v_S)):
        A = sp.expand(A * (s_sub - v_S[idx]))

    A = sp.expand(A * s**n)

    den_coeffs = sp.Poly(A, s).all_coeffs()
    den_complex = np.array([complex(sp.N(c))
                            for c in den_coeffs], dtype=np.complex128)

    # Forço coeficientes reais.
    den = np.real_if_close(den_complex, tol=1e-6).astype(float)

    # Numerador unitário extendido (estágio passa-faixa de ordem 2n).
    num = np.concatenate(([1.0], np.zeros(n)))

    H_bp = ct.tf(num, den)
    H_bp = ct.minreal(H_bp, verbose=False)

    print("[Chebyshev PF] H_bp(s) =", H_bp)

    ct.bode_plot(H_bp, dB=True)
    plt.grid(True, which='both', linestyle='--')
    plt.show(block=False)

    return H_bp, n
