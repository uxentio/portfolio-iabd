# -*- coding: utf-8 -*-
"""
Control de frenado de tren con lógica difusa Takagi-Sugeno-Kang (TSK).

TSK orden 1, hecho a mano en NumPy (scikit-fuzzy no trae TSK de forma
nativa). Cada regla tiene un consecuente lineal y_i = p·v + q·d + r·θ + c,
y la salida final es la media ponderada de los y_i con los firing
strengths w_i como pesos: F = Σ(w_i · y_i) / Σ(w_i).

Mantengo las mismas MF de entrada que el Mamdani de la Parte 1, así la
comparación aísla solo el efecto del consecuente y de la t-norma.

Dependencias: numpy, scikit-fuzzy (solo para definir y evaluar las MF).
"""

import numpy as np
import skfuzzy as fuzz


# =============================================================================
# (1) UNIVERSOS Y FUNCIONES DE MEMBRESÍA (idénticas a Mamdani)
# =============================================================================
# Guardo las MF como arrays de NumPy en lugar de objetos de skfuzzy.control.
# En TSK a mano solo necesito evaluar membresías puntuales, no montar todo
# un sistema de control.
v_universe     = np.arange(0, 200.5, 0.5)
d_universe     = np.arange(0, 1000.5, 0.5)
theta_universe = np.arange(-10, 10.1, 0.1)

MF_V = {
    'LENTA':  fuzz.trapmf(v_universe, [0,   0,   30, 70]),
    'MEDIA':  fuzz.trimf (v_universe, [40,  90, 140]),
    'RAPIDA': fuzz.trapmf(v_universe, [110, 150, 200, 200]),
}
MF_D = {
    'CERCA': fuzz.trapmf(d_universe, [0,   0,   100, 300]),
    'MEDIA': fuzz.trimf (d_universe, [200, 450, 700]),
    'LEJOS': fuzz.trapmf(d_universe, [600, 800, 1000, 1000]),
}
MF_T = {
    'BAJADA': fuzz.trapmf(theta_universe, [-10, -10, -6, -1]),
    'LLANO':  fuzz.trimf (theta_universe, [-3,  0,  3]),
    'SUBIDA': fuzz.trapmf(theta_universe, [1,   6,  10, 10]),
}


# =============================================================================
# (2) BASE DE REGLAS TSK
# =============================================================================
# Cada regla tiene 4 parámetros lineales: y_i = p·v + q·d + r·θ + c.
#
# Uso los mismos p, q, r en todas las reglas y cambio solo c. Los tres
# coeficientes comunes salen del sentido físico:
#
#   p = +0.08   más velocidad pide más freno
#   q = -0.015  más distancia permite frenar menos
#   r = -0.8    más subida baja el freno (0.8 puntos por cada % de pendiente)
#
# La c de cada regla la calculo para que, en el centro de la región que
# cubre la regla, la salida y_i dé el mismo valor que el centroide del
# conjunto Mamdani equivalente (MUY_BAJO=5, BAJO=22, MEDIO=42, ALTO=65,
# MUY_ALTO=82, MAXIMO=95). Así los dos sistemas dan parecido en los
# puntos centrales y las diferencias entre métodos se ven en los bordes.
#
# Puntos centrales que uso para calcular c:
#   v:  LENTA=25,  MEDIA=90,  RAPIDA=170
#   d:  CERCA=100, MEDIA=450, LEJOS=850
#   θ:  BAJADA=-6, LLANO=0,   SUBIDA=+6
#
# Ejemplo para R1 (LENTA + LEJOS + LLANO -> MUY_BAJO, centroide=5):
#   5 = 0.08·25 - 0.015·850 - 0.8·0 + c
#   5 = 2 - 12.75 + 0 + c
#   c = 15.75

REGLAS_TSK = [
    # (nombre, (et_v, et_d, et_θ), (p, q, r, c))      -> conjunto Mamdani equivalente
    ('R1',  ('LENTA',  'LEJOS', 'LLANO'),  (0.08, -0.015, -0.8, 15.75)),   # MUY_BAJO = 5
    ('R2',  ('LENTA',  'LEJOS', 'BAJADA'), (0.08, -0.015, -0.8, 27.95)),   # BAJO     = 22
    ('R3',  ('LENTA',  'MEDIA', 'LLANO'),  (0.08, -0.015, -0.8, 26.75)),   # BAJO     = 22
    ('R4',  ('LENTA',  'CERCA', 'LLANO'),  (0.08, -0.015, -0.8, 41.50)),   # MEDIO    = 42
    ('R5',  ('MEDIA',  'LEJOS', 'LLANO'),  (0.08, -0.015, -0.8, 27.55)),   # BAJO     = 22
    ('R6',  ('MEDIA',  'LEJOS', 'BAJADA'), (0.08, -0.015, -0.8, 42.75)),   # MEDIO    = 42
    ('R7',  ('MEDIA',  'MEDIA', 'LLANO'),  (0.08, -0.015, -0.8, 41.55)),   # MEDIO    = 42
    ('R8',  ('MEDIA',  'CERCA', 'BAJADA'), (0.08, -0.015, -0.8, 71.50)),   # MUY_ALTO = 82
    ('R9',  ('RAPIDA', 'LEJOS', 'BAJADA'), (0.08, -0.015, -0.8, 59.35)),   # ALTO     = 65
    ('R10', ('RAPIDA', 'MEDIA', 'LLANO'),  (0.08, -0.015, -0.8, 58.15)),   # ALTO     = 65
    ('R11', ('RAPIDA', 'CERCA', 'LLANO'),  (0.08, -0.015, -0.8, 69.90)),   # MUY_ALTO = 82
    ('R12', ('RAPIDA', 'CERCA', 'BAJADA'), (0.08, -0.015, -0.8, 78.10)),   # MAXIMO   = 95
]


# =============================================================================
# (3) FUNCIONES DE INFERENCIA TSK
# =============================================================================
# Parto la inferencia en tres pasos (membresías, firing strengths,
# consecuentes) y luego los combino en evaluar_tsk(). Así cada paso queda
# legible y es fácil depurarlo por separado si algo sale raro.

def membresias_entrada(v, d, theta):
    """Grado de pertenencia de (v, d, θ) a los 9 conjuntos difusos.

    Devuelvo tres diccionarios, uno por variable, en vez de un solo
    diccionario plano. Así luego en firing_strengths() se lee igual que
    se escribiría la regla en lenguaje natural: mu_v[ev] * mu_d[ed] * mu_t[et].
    """
    mu_v = {et: float(fuzz.interp_membership(v_universe,     mf, v))
            for et, mf in MF_V.items()}
    mu_d = {et: float(fuzz.interp_membership(d_universe,     mf, d))
            for et, mf in MF_D.items()}
    mu_t = {et: float(fuzz.interp_membership(theta_universe, mf, theta))
            for et, mf in MF_T.items()}
    return mu_v, mu_d, mu_t


def firing_strengths(mu_v, mu_d, mu_t, t_norma='prod'):
    """Firing strength w_i de cada una de las 12 reglas.

    Por defecto uso PRODUCTO como t-norma, no mínimo. Dos razones:

    1) El producto es derivable en todo el dominio; el mínimo no lo es en
       el punto de empate (min(0.3, 0.3) no tiene derivada bien definida).
       Esto importa si más adelante se quiere refinar el TSK con descenso
       de gradiente, que es la vía natural hacia ANFIS (ver PDF de teoría,
       PDF TSK sección 3.4).

    2) El producto da superficies de control más suaves, que encaja mejor
       con los consecuentes lineales.
    """
    pesos = []
    for _, (ev, ed, et), _ in REGLAS_TSK:
        a, b, c = mu_v[ev], mu_d[ed], mu_t[et]
        if t_norma == 'prod':
            w = a * b * c
        elif t_norma == 'min':
            w = min(a, b, c)
        else:
            raise ValueError("t_norma debe ser 'prod' o 'min'.")
        pesos.append(w)
    return np.array(pesos, dtype=float)


def consecuentes(v, d, theta):
    """Valor y_i del consecuente lineal de cada regla.

    Solo evalúa p·v + q·d + r·θ + c con los parámetros de cada regla.
    """
    ys = []
    for _, _, (p, q, r, c) in REGLAS_TSK:
        ys.append(p * v + q * d + r * theta + c)
    return np.array(ys, dtype=float)


def evaluar_tsk(v, d, theta, t_norma='prod', verbose=False):
    """Salida F (%) del sistema TSK para la terna (v, d, θ).

    Aplica la fórmula central del TSK:
        F = Σ(w_i · y_i) / Σ(w_i)

    Dos protecciones:
      - Si la suma de w_i es menor que un EPS (caso E5: pendiente en SUBIDA,
        sin reglas que cubran esa zona), devuelvo NaN en vez de dividir
        por cero.
      - Saturo el resultado a [0, 100]. El consecuente lineal no está
        acotado y puede salirse de rango si nos alejamos del punto central
        de la regla activa.
    """
    EPS = 1e-8

    mu_v, mu_d, mu_t = membresias_entrada(v, d, theta)
    w = firing_strengths(mu_v, mu_d, mu_t, t_norma=t_norma)
    y = consecuentes(v, d, theta)
    sw = w.sum()

    if sw < EPS:
        if verbose:
            print(f"  [TSK] Ninguna regla activa para v={v}, d={d}, θ={theta}")
        return float('nan')

    F = (w * y).sum() / sw
    F_clip = max(0.0, min(100.0, F))

    if verbose:
        print(f"  [TSK] v={v}, d={d}, θ={theta}")
        print(f"        sum(w)={sw:.4f}, F_raw={F:.3f}, F_clip={F_clip:.3f}")
        for (nombre, premisa, _), wi, yi in zip(REGLAS_TSK, w, y):
            if wi > 1e-4:
                print(f"        {nombre:<4} {premisa}  w={wi:.4f}  y={yi:.2f}")
    return F_clip


# =============================================================================
# (4) MAIN
# =============================================================================
ESCENARIOS = [
    ('E1 Marcha tranquila, vía despejada',       25, 850,   0),
    ('E2 Velocidad media, curva en bajada',      95, 280,  -5),
    ('E3 Aproximación rápida a estación',       155, 140,   0),
    ('E4 Situación crítica: rápido + bajada',   175,  70,  -8),
    ('E5 Subida pronunciada, obstáculo lejos',   70, 600,  +7),
]

if __name__ == '__main__':
    print("=" * 70)
    print("Sistema TSK orden 1, Control de Frenado de Tren")
    print("=" * 70)
    print(f"{'Escenario':<42} {'v':>4} {'d':>5} {'θ':>6}  {'F (%)':>7}")
    print("-" * 70)

    for etiqueta, v, d, theta in ESCENARIOS:
        F = evaluar_tsk(v, d, theta, t_norma='prod')
        F_txt = f"{F:>7.2f}" if not np.isnan(F) else "   N/A "
        print(f"{etiqueta:<42} {v:>4} {d:>5} {theta:>+6}  {F_txt}")

    # Trazado detallado del E4 para pegar en el PDF.
    print("\n--- Trazado detallado E4 ---")
    evaluar_tsk(175, 70, -8, t_norma='prod', verbose=True)
