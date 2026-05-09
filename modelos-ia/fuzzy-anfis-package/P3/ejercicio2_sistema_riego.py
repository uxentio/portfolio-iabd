# Práctica 3 - Ejercicio 2: sistema de riego adaptativo (cooperativa AgroSmart Levante).
# 3 entradas: H humedad del suelo, T temperatura máx. diaria, P precipitación 24 h. Todas en [0, 1].
# Salida: dosis de riego en [0, 1] (1 = 8 mm/día).

import os
import sys
import json
import numpy as np
import torch
import torch.nn as nn
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SEED = 123
np.random.seed(SEED)
torch.manual_seed(SEED)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


# versión robusta de ANFIS (sección 2.4): clamp en sigma para evitar NaN con 3 entradas
class ANFISLayerRobust(nn.Module):
    def __init__(self, n_inputs, n_rules):
        super().__init__()
        self.mu = nn.Parameter(torch.randn(n_rules, n_inputs))
        self.sigma = nn.Parameter(torch.ones(n_rules, n_inputs) * 0.5)
        self.p = nn.Parameter(torch.randn(n_rules, n_inputs + 1) * 0.1)

    def forward(self, x):
        # clamp obliga sigma >= 1e-3 (sin esto, w se va a 0 y los gradientes salen NaN)
        sigma_pos = torch.clamp(self.sigma, min=1e-3)
        # capa 1: pertenencia gaussiana
        diff = x.unsqueeze(1) - self.mu
        mu_vals = torch.exp(-diff ** 2 / (2 * sigma_pos ** 2))
        # capa 2: fuerza de disparo
        w = mu_vals.prod(dim=2)
        # capa 3: normalización
        w_bar = w / (w.sum(dim=1, keepdim=True) + 1e-8)
        # capa 4: consecuente lineal
        x_ext = torch.cat([x, torch.ones(x.shape[0], 1)], dim=1)
        y_i = (x_ext.unsqueeze(1) * self.p).sum(dim=2)
        # capa 5: salida ponderada
        return (w_bar * y_i).sum(dim=1)


def init_mu_kmeans(model, X_np, n_rules):
    km = KMeans(n_clusters=n_rules, random_state=SEED, n_init=10).fit(X_np)
    with torch.no_grad():
        model.mu.copy_(torch.tensor(km.cluster_centers_, dtype=torch.float32))


def entrenar(model, X_tr, y_tr, n_epochs=1000, lr=0.005, weight_decay=1e-4):
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    crit = nn.MSELoss()
    losses = []
    model.train()
    for _ in range(n_epochs):
        opt.zero_grad()
        loss = crit(model(X_tr), y_tr)
        loss.backward()
        opt.step()
        losses.append(loss.item())
    return losses


def dosis_experto(H, T, P, ruido_local=None):
    # los ? del enunciado: efecto centrado en 1.0 (extremo activo).
    # multiplicar por (1-efecto) reproduce el veto del agrónomo.
    efecto_lluvia = np.exp(-((P - 1.0) ** 2) / 0.30)
    efecto_humedad = np.exp(-((H - 1.0) ** 2) / 0.30)
    efecto_calor = np.exp(-((T - 1.0) ** 2) / 0.20)
    dosis = (
        (1 - efecto_lluvia) *
        (1 - efecto_humedad) *
        (0.6 + 0.4 * efecto_calor)
    )
    if ruido_local is not None:
        dosis = dosis + ruido_local
    return np.clip(dosis, 0.0, 1.0)


def evaluar(model, X_test, y_test):
    model.eval()
    with torch.no_grad():
        pred = model(X_test).numpy()
    real = y_test.numpy()
    rmse = float(np.sqrt(((pred - real) ** 2).mean()))
    ss_res = ((real - pred) ** 2).sum()
    ss_tot = ((real - real.mean()) ** 2).sum()
    r2 = float(1 - ss_res / ss_tot)
    return rmse, r2, pred, real


def explicar_decision(model, H, T, P):
    # adaptación a 3 entradas de la función del ejemplo 3 del documento
    x = torch.tensor([[H, T, P]], dtype=torch.float32)
    with torch.no_grad():
        sigma_pos = torch.clamp(model.sigma, min=1e-3)
        diff = x.unsqueeze(1) - model.mu
        mu_vals = torch.exp(-diff ** 2 / (2 * sigma_pos ** 2))
        w = mu_vals.prod(dim=2)
        w_bar = w / (w.sum(dim=1, keepdim=True) + 1e-8)
        dosis_n = float(model(x).item())
    dosis_mm = dosis_n * 8.0
    print(f'\n  Parcela: H={H:.2f}, T={T:.2f}, P={P:.2f}')
    print(f'  Dosis: {dosis_n:.3f} ({dosis_mm:.2f} mm/día)')
    if dosis_n < 0.10:
        nivel = 'NO REGAR'
    elif dosis_n < 0.40:
        nivel = 'riego BAJO'
    elif dosis_n < 0.70:
        nivel = 'riego MEDIO'
    else:
        nivel = 'riego ALTO'
    print(f'  -> {nivel}')
    print('  activación de reglas:')
    for i, w in enumerate(w_bar[0]):
        barra = '#' * int(w.item() * 20)
        print(f'    R{i+1}: {w.item():.3f}  {barra}')
    return {'H': H, 'T': T, 'P': P,
            'dosis_norm': dosis_n, 'dosis_mm_dia': dosis_mm,
            'nivel': nivel,
            'activacion_reglas': [float(v) for v in w_bar[0]]}


# generación del dataset (sección 2.3 del enunciado)
N = 600
H_norm = np.random.beta(2, 2, N)
T_norm = np.random.uniform(0, 1, N)
P_norm = np.random.beta(1, 4, N)
ruido = 0.03 * np.random.randn(N)

dosis = dosis_experto(H_norm, T_norm, P_norm, ruido_local=ruido)

X = np.column_stack([H_norm, T_norm, P_norm]).astype(np.float32)
y = dosis.astype(np.float32)

# split 75/25
perm = np.random.permutation(N)
split = int(0.75 * N)
tr_idx, te_idx = perm[:split], perm[split:]
X_train = torch.tensor(X[tr_idx])
y_train = torch.tensor(y[tr_idx])
X_test = torch.tensor(X[te_idx])
y_test = torch.tensor(y[te_idx])

print(f'Dataset: N={N}, train={len(tr_idx)}, test={len(te_idx)}')


# experimento A: barrido n_rules en {3, 5, 8}
print('\n[A] convergencia con distintos n_rules')
expA = {}
for nr in (3, 5, 8):
    torch.manual_seed(SEED)
    m = ANFISLayerRobust(n_inputs=3, n_rules=nr)
    init_mu_kmeans(m, X[tr_idx], nr)
    losses = entrenar(m, X_train, y_train, n_epochs=1000, lr=0.005)
    rmse, r2, _, _ = evaluar(m, X_test, y_test)
    expA[nr] = {'losses': losses, 'rmse': rmse, 'r2': r2, 'model': m}
    n_params = sum(p.numel() for p in m.parameters())
    print(f'  n_rules={nr:>2} | RMSE_test={rmse:.4f}  R2={r2:.4f}  params={n_params}')

best_nr = min(expA.keys(), key=lambda k: expA[k]['rmse'])
print(f'  mejor n_rules según RMSE de test: {best_nr}')

plt.figure(figsize=(9, 4.5))
for nr, info in expA.items():
    plt.plot(info['losses'], label=f'n_rules={nr} (RMSE={info["rmse"]:.4f})', alpha=0.85)
plt.xlabel('Época')
plt.ylabel('MSE (train)')
plt.title('Convergencia para distintos n_rules')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'expA_n_rules.png'), dpi=130)
plt.close()


# experimento B: aleatoria vs K-means con el n_rules elegido
print('\n[B] impacto de la inicialización')
NR = best_nr

torch.manual_seed(SEED)
m_rand = ANFISLayerRobust(n_inputs=3, n_rules=NR)
losses_rand = entrenar(m_rand, X_train, y_train, n_epochs=1000, lr=0.005)
rmse_rand, _, _, _ = evaluar(m_rand, X_test, y_test)

torch.manual_seed(SEED)
m_km = ANFISLayerRobust(n_inputs=3, n_rules=NR)
init_mu_kmeans(m_km, X[tr_idx], NR)
losses_km = entrenar(m_km, X_train, y_train, n_epochs=1000, lr=0.005)
rmse_km, r2_km, pred_km, real_km = evaluar(m_km, X_test, y_test)

# tolerancia del 5 % sobre el MSE final del K-means
target = losses_km[-1] * 1.05
ep_km = next((i for i, v in enumerate(losses_km) if v <= target), 1000)
ep_rand = next((i for i, v in enumerate(losses_rand) if v <= target), 1000)
ahorro = ep_rand - ep_km
ahorro_pct = 100 * ahorro / ep_rand if ep_rand > 0 else 0

print(f'  RMSE | aleatoria={rmse_rand:.4f}  K-means={rmse_km:.4f}')
print(f'  épocas para alcanzar MSE_final(K-means)*1.05:')
print(f'    K-means    : {ep_km}')
print(f'    aleatoria  : {ep_rand}')
print(f'    ahorro     : {ahorro} épocas (~{ahorro_pct:.0f} %)')

plt.figure(figsize=(9, 4.5))
plt.plot(losses_rand, label=f'aleatoria (RMSE={rmse_rand:.4f})')
plt.plot(losses_km, label=f'K-means (RMSE={rmse_km:.4f})')
plt.axhline(target, color='gray', ls=':', alpha=0.6, label='1.05 * MSE final K-means')
plt.xlabel('Época')
plt.ylabel('MSE (train)')
plt.title(f'Inicialización con n_rules={NR}')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'expB_init.png'), dpi=130)
plt.close()

model = m_km


# experimento C: importancia de variables (sigma media por columna)
print('\n[C] importancia de variables')
sigma = model.sigma.detach().numpy()
mu = model.mu.detach().numpy()
nombres = ['H', 'T', 'P']

print(f'{"Regla":<6}{"mu_H":>8}{"sg_H":>8}{"mu_T":>8}{"sg_T":>8}{"mu_P":>8}{"sg_P":>8}')
for i in range(NR):
    print(f'R{i+1:<5}{mu[i,0]:>8.3f}{sigma[i,0]:>8.3f}'
          f'{mu[i,1]:>8.3f}{sigma[i,1]:>8.3f}'
          f'{mu[i,2]:>8.3f}{sigma[i,2]:>8.3f}')

# sigma pequeña -> regla selectiva en esa variable
sigma_media = sigma.mean(axis=0)
print('\n  sigma media por variable:')
for k, name in enumerate(nombres):
    print(f'    {name}: {sigma_media[k]:.3f}')
mas_selectiva = nombres[int(np.argmin(sigma_media))]
print(f'  variable más determinante: {mas_selectiva}')


# experimento D: vértices del cubo [0,1]^3
print('\n[D] vértices del hipercubo')
vertices = np.array(
    [[h, t, p] for h in (0.0, 1.0) for t in (0.0, 1.0) for p in (0.0, 1.0)],
    dtype=np.float32,
)

with torch.no_grad():
    pred_v = model(torch.tensor(vertices)).numpy()
exp_v = dosis_experto(vertices[:, 0], vertices[:, 1], vertices[:, 2]).astype(float)

vertices_tabla = []
print(f'{"H":>4}{"T":>4}{"P":>4}{"ANFIS":>10}{"Experto":>10}{"|err|":>8}   Comentario')
for v, p_anfis, p_exp in zip(vertices, pred_v, exp_v):
    H_, T_, P_ = v
    err = abs(float(p_anfis) - float(p_exp))
    if P_ > 0.5:
        coment = 'lluvia intensa, no regar'
    elif H_ > 0.5:
        coment = 'suelo saturado, no regar'
    elif H_ < 0.5 and T_ > 0.5:
        coment = 'seco + calor, dosis MAX'
    else:
        coment = 'seco y fresco, riego medio'
    print(f'{H_:>4.0f}{T_:>4.0f}{P_:>4.0f}'
          f'{float(p_anfis):>10.3f}{float(p_exp):>10.3f}{err:>8.3f}   {coment}')
    vertices_tabla.append({
        'H': float(H_), 'T': float(T_), 'P': float(P_),
        'pred_anfis': float(p_anfis),
        'experto': float(p_exp),
        'error_abs': float(err),
        'comentario': coment,
    })

err_max = max(v['error_abs'] for v in vertices_tabla)
err_med = sum(v['error_abs'] for v in vertices_tabla) / len(vertices_tabla)
print(f'\n  error medio en vértices: {err_med:.3f}, máx: {err_max:.3f}')


# experimento E: sistema explicable con dos casos reales
print('\n[E] sistema explicable en producción')
print('  (a) tarde de julio seca tras semanas sin lluvia')
caso_a = explicar_decision(model, H=0.15, T=0.85, P=0.05)
print('\n  (b) mañana lluviosa de noviembre con suelo saturado')
caso_b = explicar_decision(model, H=0.90, T=0.30, P=0.80)


# métrica final
print('\n[final]')
rmse, r2, pred, real = evaluar(model, X_test, y_test)
print(f'  Modelo: K-means + n_rules={NR} + lr=0.005 + L2=1e-4')
print(f'  RMSE test={rmse:.4f}, R2 test={r2:.4f}')

plt.figure(figsize=(5.2, 5.2))
plt.scatter(real, pred, alpha=0.6)
plt.plot([0, 1], [0, 1], 'r--', label='predicción perfecta')
plt.xlabel('Dosis real')
plt.ylabel('Dosis predicha')
plt.title(f'Predicción vs real (RMSE={rmse:.4f}, R²={r2:.3f})')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'ej2_pred_vs_real.png'), dpi=130)
plt.close()


# resumen JSON para la memoria
def reglas_json(m, nr):
    mu_, sg_ = m.mu.detach().numpy(), m.sigma.detach().numpy()
    return [
        {'regla': f'R{i+1}',
         'mu': [float(mu_[i, 0]), float(mu_[i, 1]), float(mu_[i, 2])],
         'sigma': [float(sg_[i, 0]), float(sg_[i, 1]), float(sg_[i, 2])]}
        for i in range(nr)
    ]


resumen = {
    'config': {
        'N': N, 'split': '75/25', 'seed': SEED,
        'n_rules_elegido': NR, 'n_epochs': 1000,
        'lr': 0.005, 'weight_decay': 1e-4,
        'sigma_init': 0.5, 'p_init_scale': 0.1,
    },
    'expA': {str(nr): {'rmse': info['rmse'], 'r2': info['r2'],
                       'mse_final_train': info['losses'][-1]}
             for nr, info in expA.items()},
    'expB': {
        'rmse_aleatoria': rmse_rand, 'rmse_kmeans': rmse_km,
        'epocas_kmeans': ep_km, 'epocas_aleatoria': ep_rand,
        'epocas_ahorradas': ahorro,
        'ahorro_pct': ahorro_pct,
    },
    'expC': {
        'reglas': reglas_json(model, NR),
        'sigma_media_por_variable': {
            'H': float(sigma_media[0]),
            'T': float(sigma_media[1]),
            'P': float(sigma_media[2]),
        },
        'mas_selectiva': mas_selectiva,
    },
    'expD': {
        'tabla_vertices': vertices_tabla,
        'error_medio': err_med,
        'error_max': err_max,
    },
    'expE': {'caso_a': caso_a, 'caso_b': caso_b},
    'final': {'rmse_test': rmse, 'r2_test': r2},
}
with open(os.path.join(OUT_DIR, 'resumen_ej2.json'), 'w', encoding='utf-8') as f:
    json.dump(resumen, f, ensure_ascii=False, indent=2)

print('\nguardadas las gráficas y el resumen JSON')
