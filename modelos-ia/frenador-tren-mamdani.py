# -*- coding: utf-8 -*-
"""
Control de frenado de tren con lógica difusa Mamdani.

Entradas:
    v     -> velocidad del tren, 0-200 km/h
    d     -> distancia al obstáculo, 0-1000 m
    theta -> pendiente de la vía, -10 a +10 % (neg = bajada, pos = subida)

Salida:
    F     -> fuerza de frenado, 0-100 %

Dependencias: numpy, matplotlib, scikit-fuzzy.
Uso skfuzzy.control porque ya trae el motor Mamdani, así no tengo que
montar agregación y defuzzificación a mano.
"""

import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# =============================================================================
# (1) UNIVERSOS DE DISCURSO
# =============================================================================
# El paso de discretización importa sobre todo para F (la salida). Con un
# paso grande, el centroide sale poco preciso. Con 0.5 queda estable y no
# se dispara el tiempo de cálculo.

v_universe     = np.arange(0,    200.5, 0.5)   # velocidad, km/h
d_universe     = np.arange(0,   1000.5, 0.5)   # distancia, m
theta_universe = np.arange(-10,   10.1, 0.1)   # pendiente, %
F_universe     = np.arange(0,    100.5, 0.5)   # fuerza de frenado, %

# Las entradas van como Antecedent, la salida como Consequent. Fijo
# defuzzify_method='centroid' en la salida (lo justifico en la Tarea 1.4.a).
velocidad = ctrl.Antecedent(v_universe,     'velocidad')
distancia = ctrl.Antecedent(d_universe,     'distancia')
pendiente = ctrl.Antecedent(theta_universe, 'pendiente')
fuerza    = ctrl.Consequent(F_universe,     'fuerza', defuzzify_method='centroid')


# =============================================================================
# (2) FUNCIONES DE MEMBRESÍA DE LAS ENTRADAS
# =============================================================================
# Tres conjuntos por variable. Extremos en trapezoidal (dan meseta de
# pertenencia total cuando la entrada está claramente en ese lado),
# intermedios en triangular. Los solapo al 50% entre etiquetas vecinas
# para que la transición sea suave; sin solapamiento, el freno daría
# saltos y se notaría como tirones.

# Velocidad
velocidad['LENTA']  = fuzz.trapmf(v_universe, [0,   0,   30, 70])
velocidad['MEDIA']  = fuzz.trimf (v_universe, [40,  90, 140])
velocidad['RAPIDA'] = fuzz.trapmf(v_universe, [110, 150, 200, 200])

# Distancia
distancia['CERCA'] = fuzz.trapmf(d_universe, [0,   0,   100, 300])
distancia['MEDIA'] = fuzz.trimf (d_universe, [200, 450, 700])
distancia['LEJOS'] = fuzz.trapmf(d_universe, [600, 800, 1000, 1000])

# Pendiente. Signo según enunciado: θ < 0 es bajada, θ > 0 es subida.
pendiente['BAJADA'] = fuzz.trapmf(theta_universe, [-10, -10, -6, -1])
pendiente['LLANO']  = fuzz.trimf (theta_universe, [-3,   0,   3])
pendiente['SUBIDA'] = fuzz.trapmf(theta_universe, [1,    6,   10, 10])


# =============================================================================
# (3) FUNCIONES DE MEMBRESÍA DE LA SALIDA F
# =============================================================================
# Seis niveles de freno cubriendo [0, 100]. Extremos (MUY_BAJO y MAXIMO)
# en trapezoidal porque son zonas saturadas: freno al mínimo y freno al
# tope. Los cuatro niveles intermedios van en triangular, centrados en un
# valor concreto.
fuerza['MUY_BAJO'] = fuzz.trapmf(F_universe, [0,  0,  5,  15])
fuerza['BAJO']     = fuzz.trimf (F_universe, [10, 22, 35])
fuerza['MEDIO']    = fuzz.trimf (F_universe, [28, 42, 55])
fuerza['ALTO']     = fuzz.trimf (F_universe, [48, 65, 78])
fuerza['MUY_ALTO'] = fuzz.trimf (F_universe, [68, 82, 95])
fuerza['MAXIMO']   = fuzz.trapmf(F_universe, [88, 95, 100, 100])


# =============================================================================
# (4) BASE DE REGLAS
# =============================================================================
# Las 12 reglas del enunciado, copiadas tal cual de la tabla.
#
# Detalle importante: ninguna de estas reglas lleva SUBIDA en la premisa.
# Solo aparecen LLANO y BAJADA. Esto tiene consecuencias en E5 (θ=+7):
# con la t-norma mínimo, todos los firing strengths salen 0 y skfuzzy
# lanza KeyError al pedir la salida. Lo capturo en evaluar_mamdani() y
# lo comento en el PDF (Tarea 1.3).

reglas = [
    ctrl.Rule(velocidad['LENTA']  & distancia['LEJOS'] & pendiente['LLANO'],  fuerza['MUY_BAJO']),  # R1
    ctrl.Rule(velocidad['LENTA']  & distancia['LEJOS'] & pendiente['BAJADA'], fuerza['BAJO']),      # R2
    ctrl.Rule(velocidad['LENTA']  & distancia['MEDIA'] & pendiente['LLANO'],  fuerza['BAJO']),      # R3
    ctrl.Rule(velocidad['LENTA']  & distancia['CERCA'] & pendiente['LLANO'],  fuerza['MEDIO']),     # R4
    ctrl.Rule(velocidad['MEDIA']  & distancia['LEJOS'] & pendiente['LLANO'],  fuerza['BAJO']),      # R5
    ctrl.Rule(velocidad['MEDIA']  & distancia['LEJOS'] & pendiente['BAJADA'], fuerza['MEDIO']),     # R6
    ctrl.Rule(velocidad['MEDIA']  & distancia['MEDIA'] & pendiente['LLANO'],  fuerza['MEDIO']),     # R7
    ctrl.Rule(velocidad['MEDIA']  & distancia['CERCA'] & pendiente['BAJADA'], fuerza['MUY_ALTO']),  # R8
    ctrl.Rule(velocidad['RAPIDA'] & distancia['LEJOS'] & pendiente['BAJADA'], fuerza['ALTO']),      # R9
    ctrl.Rule(velocidad['RAPIDA'] & distancia['MEDIA'] & pendiente['LLANO'],  fuerza['ALTO']),      # R10
    ctrl.Rule(velocidad['RAPIDA'] & distancia['CERCA'] & pendiente['LLANO'],  fuerza['MUY_ALTO']),  # R11
    ctrl.Rule(velocidad['RAPIDA'] & distancia['CERCA'] & pendiente['BAJADA'], fuerza['MAXIMO']),    # R12
]


# =============================================================================
# (5) SISTEMA DE CONTROL Y FUNCIÓN DE EVALUACIÓN
# =============================================================================
# El ControlSystem lo monto una vez (es caro). El Simulation lo recreo por
# cada consulta para que no arrastre estado de llamadas anteriores.
sistema_mamdani = ctrl.ControlSystem(reglas)


def evaluar_mamdani(v, d, theta):
    """Devuelve F (%) para una terna (v, d, θ).

    Si ninguna regla se dispara (caso E5, pendiente en SUBIDA), skfuzzy
    lanza KeyError al leer la salida. Lo capturo y devuelvo NaN.
    """
    sim = ctrl.ControlSystemSimulation(sistema_mamdani)
    sim.input['velocidad'] = float(v)
    sim.input['distancia'] = float(d)
    sim.input['pendiente'] = float(theta)
    try:
        sim.compute()
        return float(sim.output['fuerza'])
    except (KeyError, ValueError):
        return float('nan')


# =============================================================================
# (6) ESCENARIOS DE PRUEBA Y TRAZADO MANUAL DE E4
# =============================================================================
ESCENARIOS = [
    ('E1 Marcha tranquila, vía despejada',       25, 850,   0),
    ('E2 Velocidad media, curva en bajada',      95, 280,  -5),
    ('E3 Aproximación rápida a estación',       155, 140,   0),
    ('E4 Situación crítica: rápido + bajada',   175,  70,  -8),
    ('E5 Subida pronunciada, obstáculo lejos',   70, 600,  +7),
]


def trazar_inferencia_E4(v, d, theta):
    """Trazado paso a paso de E4, hecho a mano.

    Hago este trazado por mi cuenta porque skfuzzy no deja inspeccionar
    fácilmente los firing strengths intermedios. Calculo membresías,
    firing strengths con t-norma mínimo, agregación por max y centroide.
    Debe coincidir con evaluar_mamdani(175, 70, -8).
    """
    # Paso 1: fuzzificación. Grado de pertenencia de cada entrada.
    mu_v = {
        'LENTA':  fuzz.interp_membership(v_universe, velocidad['LENTA'].mf,  v),
        'MEDIA':  fuzz.interp_membership(v_universe, velocidad['MEDIA'].mf,  v),
        'RAPIDA': fuzz.interp_membership(v_universe, velocidad['RAPIDA'].mf, v),
    }
    mu_d = {
        'CERCA': fuzz.interp_membership(d_universe, distancia['CERCA'].mf, d),
        'MEDIA': fuzz.interp_membership(d_universe, distancia['MEDIA'].mf, d),
        'LEJOS': fuzz.interp_membership(d_universe, distancia['LEJOS'].mf, d),
    }
    mu_t = {
        'BAJADA': fuzz.interp_membership(theta_universe, pendiente['BAJADA'].mf, theta),
        'LLANO':  fuzz.interp_membership(theta_universe, pendiente['LLANO'].mf,  theta),
        'SUBIDA': fuzz.interp_membership(theta_universe, pendiente['SUBIDA'].mf, theta),
    }

    # Paso 2: tabla de las 12 reglas como tuplas (nombre, premisas, consecuente).
    definicion_reglas = [
        ('R1',  ('LENTA',  'LEJOS', 'LLANO'),  'MUY_BAJO'),
        ('R2',  ('LENTA',  'LEJOS', 'BAJADA'), 'BAJO'),
        ('R3',  ('LENTA',  'MEDIA', 'LLANO'),  'BAJO'),
        ('R4',  ('LENTA',  'CERCA', 'LLANO'),  'MEDIO'),
        ('R5',  ('MEDIA',  'LEJOS', 'LLANO'),  'BAJO'),
        ('R6',  ('MEDIA',  'LEJOS', 'BAJADA'), 'MEDIO'),
        ('R7',  ('MEDIA',  'MEDIA', 'LLANO'),  'MEDIO'),
        ('R8',  ('MEDIA',  'CERCA', 'BAJADA'), 'MUY_ALTO'),
        ('R9',  ('RAPIDA', 'LEJOS', 'BAJADA'), 'ALTO'),
        ('R10', ('RAPIDA', 'MEDIA', 'LLANO'),  'ALTO'),
        ('R11', ('RAPIDA', 'CERCA', 'LLANO'),  'MUY_ALTO'),
        ('R12', ('RAPIDA', 'CERCA', 'BAJADA'), 'MAXIMO'),
    ]

    print(f"\n--- Trazado detallado E4: v={v}, d={d}, θ={theta} ---")
    print("Membresías de entrada:")
    print(f"  v={v}     -> {mu_v}")
    print(f"  d={d}     -> {mu_d}")
    print(f"  θ={theta} -> {mu_t}")

    # Paso 3: firing strength con min, recorte del conjunto de salida al
    # nivel w, agregación con max sobre el conjunto global.
    print("\nFiring strengths (t-norma = min):")
    agregado = np.zeros_like(F_universe)
    mfs_salida = {
        'MUY_BAJO': fuerza['MUY_BAJO'].mf,
        'BAJO':     fuerza['BAJO'].mf,
        'MEDIO':    fuerza['MEDIO'].mf,
        'ALTO':     fuerza['ALTO'].mf,
        'MUY_ALTO': fuerza['MUY_ALTO'].mf,
        'MAXIMO':   fuerza['MAXIMO'].mf,
    }
    for nombre, (ev, ed, et), cons in definicion_reglas:
        w = min(mu_v[ev], mu_d[ed], mu_t[et])
        if w > 1e-6:
            print(f"  {nombre:<4} -> {ev}+{ed}+{et} => {cons:<9}  w={w:.4f}")
        recortada = np.minimum(w, mfs_salida[cons])
        agregado = np.maximum(agregado, recortada)

    # Paso 4: centroide = integral(x*μ(x)) / integral(μ(x)).
    # Uso la regla del trapecio para las dos integrales.
    area = np.trapezoid(agregado, F_universe)
    if area < 1e-9:
        centroide = float('nan')
    else:
        centroide = np.trapezoid(agregado * F_universe, F_universe) / area
    print(f"\nCentroide (F defuzzificado) = {centroide:.2f} %")
    return centroide


# =============================================================================
# (7) MAIN
# =============================================================================
if __name__ == '__main__':
    print("=" * 70)
    print("Sistema Mamdani, Control de Frenado de Tren")
    print("=" * 70)
    print(f"{'Escenario':<42} {'v':>4} {'d':>5} {'θ':>6}  {'F (%)':>7}")
    print("-" * 70)

    for etiqueta, v, d, theta in ESCENARIOS:
        F = evaluar_mamdani(v, d, theta)
        F_txt = f"{F:>7.2f}" if not np.isnan(F) else "   N/A "
        print(f"{etiqueta:<42} {v:>4} {d:>5} {theta:>+6}  {F_txt}")

    # Trazado manual de E4 para el PDF de respuestas.
    trazar_inferencia_E4(175, 70, -8)

    # Gráficas view() que pide el enunciado. view() abre una figura de
    # matplotlib; la guardo como PNG para pegarla en el Word.
    for var, nombre in [(velocidad, 'velocidad'),
                        (distancia, 'distancia'),
                        (pendiente, 'pendiente'),
                        (fuerza,    'fuerza')]:
        var.view()
        fig = plt.gcf()
        fig.suptitle(f"MF de {nombre}", fontsize=12)
        fig.tight_layout()
        fig.savefig(f"mf_{nombre}.png", dpi=120, bbox_inches='tight')
        print(f"  Guardada figura mf_{nombre}.png")

    plt.close('all')
    print("\nFin.")
