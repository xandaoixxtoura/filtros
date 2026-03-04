# # drawing.py
# import numpy as np
# import sympy as sp
# import control as ct
# import matplotlib.pyplot as plt


# def main(tipo_filtro: str, params: dict):
#     """
#     tipo_filtro: 'passa-baixa', 'passa-alta', 'passa-faixa', ...
#     params: {'Amin': '10', 'Amax': '1', 'Ws': '20', 'Wp': '200'} vindos do GUI
#     """
#     Amin = float(params['Amin'])
#     Amax = float(params['Amax'])

#     if tipo_filtro == 'passa-faixa':
#         desenhar_passa_faixa_butterworth(Amin, Amax)
#     else:
#         print(f"Tipo de filtro '{tipo_filtro}' ainda não implementado.")


# def desenhar_passa_faixa_butterworth(Amin: float, Amax: float):
#     """Tradução numérica do código MATLAB de passa-faixa Butterworth + Bode."""

#     # variável simbólica
#     s = sp.symbols('s')

#     ## Passa Faixa usando a aprox de butterworth
#     Wp_2 = 2 * np.pi * 5e3
#     Wp_1 = 2 * np.pi * 200
#     Ws_2 = 2 * np.pi * 50e3
#     Ws_1 = 2 * np.pi * 20
#     Wo = np.sqrt(Wp_2 * Wp_1)
#     Beta = Wp_2 - Wp_1
#     Wp = 1.0
#     Ws = (Ws_2 - Ws_1) / (Wp_2 - Wp_1)

#     # sem ser passa faixa (mantido como comentário do original)
#     # Wp = 2*pi*200;
#     # Ws = 2*pi*1e3;

#     ### butterworth

#     # Ep numérico para ordem n
#     Ep = np.sqrt(10**(0.1 * Amax) - 1)

#     # cálculo da ordem teórica
#     num_n = np.log10((10**(0.1 * Amin) - 1) / (Ep**2))
#     den_n = np.log10((Ws / Wp)**2)
#     n_teorico = num_n / den_n
#     n = int(np.ceil(n_teorico))
#     k = n

#     print(f"n_teórico = {n_teorico}, n arredondado = {n}")

#     # se n <= 0, não faz sentido montar o filtro
#     if n <= 0:
#         print("Ordem n <= 0: com esses Amin/Amax não há filtro Butterworth válido.")
#         return

#     # s_sub puramente numérico (Ep é número, não simbólico)
#     s_sub = (Ep**(1/n) / Wp) * (s**2 + Wo**2) / (Beta * s)

#     # cálculo dos pólos de Butterworth no plano s_sub
#     v_S = []
#     for k_temp in range(1, k + 1):
#         ang = (np.pi / 2) * (2 * k_temp + n - 1) / n
#         v_S.append(np.cos(ang) + 1j * np.sin(ang))

#     # construção do denominador simbólico em s
#     A = sp.Integer(1)
#     for root in v_S:
#         A = sp.expand(A * (s_sub - root))

#     A = sp.expand(A * s**k)

#     # equivalente ao sym2poly(expand(A));
#     den_coeffs = sp.Poly(A, s).all_coeffs()

#     # converte para complexo e tenta descartar parte imaginária pequena
#     den_complex = np.array([complex(sp.N(c)) for c in den_coeffs], dtype=complex)
#     if np.all(np.abs(den_complex.imag) < 1e-8):
#         den = den_complex.real.astype(float)
#     else:
#         den = den_complex

#     if n == 1:
#         den = np.real_if_close(den)
#         if np.isclose(den[0], 0):
#             den = den[1:]

#     # num = [1, zeros(1,k)];
#     num = np.concatenate(([1.0], np.zeros(k)))

#     # H_tf = tf(num, den);
#     H_tf = ct.tf(num, den)

#     # H_tf = minreal(H_tf)
#     H_tf = ct.minreal(H_tf, verbose=False)

#     print("Ordem n =", n)
#     print("H(s) =", H_tf)

#     # figure; bode(H_tf); grid on;
#     ct.bode_plot(H_tf, dB=True)
#     plt.grid(True, which='both', linestyle='--')
#     plt.show()


# drawing.py
import numpy as np
import sympy as sp
import control as ct
import matplotlib.pyplot as plt


def main(tipo_filtro: str, config: str, topologia: str, params: dict):
    """
    tipo_filtro: 'passa-baixa', 'passa-alta', 'passa-faixa'
    config: 'Butterworth' ou 'Chebyshev'
    topologia: 'sallen-key' ou 'mfb'
    params: {'Amin': '10', 'Amax': '1', 'Ws': '20', 'Wp': '200'} vindos do GUI
    """
    Amin = float(params['Amin'])
    Amax = float(params['Amax'])
    Ws = float(params['Ws'])   # em Hz
    Wp = float(params['Wp'])   # em Hz

    print(
        f">> tipo_filtro = {tipo_filtro}, config = {config}, topologia = {topologia}")

    # por enquanto, só Butterworth passa-faixa está implementado
    if config == 'Butterworth' and tipo_filtro == 'passa-faixa':
        desenhar_passa_faixa_butterworth(Amin, Amax)
    elif config == 'Butterworth' and tipo_filtro == 'passa-baixa':
        desenhar_passa_baixa_butterworth(Amin, Amax, Ws, Wp, topologia)
    elif config == 'Butterworth' and tipo_filtro == 'passa-alta':
        desenhar_passa_alta_butterworth(Amin, Amax, Ws, Wp, topologia)
    else:
        print("Configuração/filtro ainda não implementados para:",
              config, tipo_filtro)


def desenhar_passa_faixa_butterworth(Amin: float, Amax: float):
    """Tradução numérica do código MATLAB de passa-faixa Butterworth + Bode."""

    s = sp.symbols('s')

    # Passa Faixa usando a aprox de butterworth
    Wp_2 = 2 * np.pi * 5e3
    Wp_1 = 2 * np.pi * 200
    Ws_2 = 2 * np.pi * 50e3
    Ws_1 = 2 * np.pi * 20
    Wo = np.sqrt(Wp_2 * Wp_1)
    Beta = Wp_2 - Wp_1
    Wp = 1.0
    Ws = (Ws_2 - Ws_1) / (Wp_2 - Wp_1)

    Ep = np.sqrt(10**(0.1 * Amax) - 1)

    num_n = np.log10((10**(0.1 * Amin) - 1) / (Ep**2))
    den_n = np.log10((Ws / Wp)**2)
    n_teorico = num_n / den_n
    n = int(np.ceil(n_teorico))
    k = n

    print(f"n_teórico = {n_teorico}, n arredondado = {n}")

    if n <= 0:
        print("Ordem n <= 0: com esses Amin/Amax não há filtro Butterworth válido.")
        return

    s_sub = (Ep**(1/n) / Wp) * (s**2 + Wo**2) / (Beta * s)

    v_S = []
    for k_temp in range(1, k + 1):
        ang = (np.pi / 2) * (2 * k_temp + n - 1) / n
        v_S.append(np.cos(ang) + 1j * np.sin(ang))

    A = sp.Integer(1)
    for root in v_S:
        A = sp.expand(A * (s_sub - root))

    A = sp.expand(A * s**k)

    den_coeffs = sp.Poly(A, s).all_coeffs()
    den_complex = np.array([complex(sp.N(c))
                           for c in den_coeffs], dtype=complex)
    if np.all(np.abs(den_complex.imag) < 1e-8):
        den = den_complex.real.astype(float)
    else:
        den = den_complex

    if n == 1:
        den = np.real_if_close(den)
        if np.isclose(den[0], 0):
            den = den[1:]

    num = np.concatenate(([1.0], np.zeros(k)))

    H_tf = ct.tf(num, den)
    H_tf = ct.minreal(H_tf, verbose=False)

    print("Ordem n =", n)
    print("H(s) =", H_tf)

    ct.bode_plot(H_tf, dB=True)
    plt.grid(True, which='both', linestyle='--')
    plt.show()


def desenhar_passa_baixa_butterworth(
    Amin: float, Amax: float, Ws_hz: float, Wp_hz: float, topologia: str
):
    print(">> Passa-baixa Butterworth ainda não implementado.")
    print(
        f"Amin={Amin}, Amax={Amax}, Ws={Ws_hz} Hz, Wp={Wp_hz} Hz, topo={topologia}")


def desenhar_passa_alta_butterworth(
    Amin: float, Amax: float, Ws_hz: float, Wp_hz: float, topologia: str
):
    print(">> Passa-alta Butterworth ainda não implementado.")
    print(
        f"Amin={Amin}, Amax={Amax}, Ws={Ws_hz} Hz, Wp={Wp_hz} Hz, topo={topologia}")
