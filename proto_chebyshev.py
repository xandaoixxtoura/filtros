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
                            for c in den_coeffs], dtype=complex)
    if np.all(np.abs(den_complex.imag) < 1e-8):
        den = den_complex.real.astype(float)
    else:
        den = den_complex

    # Para o Chebyshev de tipo I eu uso numerador unitário.
    num = np.array([1.0])

    H_tf = ct.tf(num, den)
    H_tf = ct.minreal(H_tf, verbose=False)

    print("[Chebyshev PB] H(s) =", H_tf)

    # Aqui eu ploto o diagrama de Bode do protótipo Chebyshev.
    ct.bode_plot(H_tf, dB=True)
    plt.grid(True, which='both', linestyle='--')
    plt.show()

    return H_tf, n
