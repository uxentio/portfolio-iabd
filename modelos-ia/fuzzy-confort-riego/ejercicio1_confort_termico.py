# Práctica 3 - Ejercicio 1: índice de confort térmico (ICT) en pabellones deportivos.
# Entradas: T (temperatura interior) y O (% ocupación), ambas normalizadas a [0, 1].

import os
import sys
import json
import numpy as np
import torch
import torch.nn as nn
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# en Windows la consola es cp1252 y revienta con caracteres Unicode
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


# modelo ANFIS (5 capas, Takagi-Sugeno orden 1)
class ANFISLayer(nn.Module):
    def __init__(self, n_inputs, n_rules):
        super().__init__()
        self.mu = nn.Parameter(torch.randn(n_rules, n_inputs))
        # sigma=0.5 porque los datos están en [0, 1]; con 1.0 las gaussianas salen planas
        self.sigma = nn.Parameter(torch.ones(n_rules, n_inputs) * 0.5)
        # n_inputs+1 porque incluye el término bias
        self.p = nn.Parameter(torch.randn(n_rules, n_inputs + 1) * 0.1)

    def forward(self, x):
        # capa 1: pertenencia gaussiana
        diff = x.unsqueeze(1) - self.mu
        mu_vals = torch.exp(-diff ** 2 / (2 * self.sigma ** 2))
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
    return km.cluster_centers_


def entrenar(model, X_tr, y_tr, n_epochs=800, lr=0.01, verbose=False):
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    crit = nn.MSELoss()
    losses = []
    model.train()
    for epoch in range(n_epochs):
        opt.zero_grad()
        loss = crit(model(X_tr), y_tr)
        loss.backward()
        opt.step()
        losses.append(loss.item())
        if verbose and epoch % 100 == 0:
            print(f'  época {epoch:4d} | MSE = {loss.item():.6f}')
    return losses


def etiqueta(v):
    if v < 0.4:
        return 'baja'
    if v < 0.7:
        return 'media'
    return 'alta'


# generación del dataset (sección 1.2 del enunciado)
N = 400
T_norm = np.random.uniform(0, 1, N)
O_norm = np.random.uniform(0, 1, N)
ruido = 0.04 * np.random.randn(N)

# ICT del experto: pico en T=0.6 y O=0.55
ICT = (
    np.exp(-((T_norm - 0.60) ** 2) / 0.06)
    * np.exp(-((O_norm - 0.55) ** 2) / 0.04)
    + ruido
).clip(0, 1)

X = np.column_stack([T_norm, O_norm]).astype(np.float32)
y = ICT.astype(np.float32)

# split 80/20
perm = np.random.permutation(N)
split = int(0.8 * N)
tr_idx, te_idx = perm[:split], perm[split:]
X_train = torch.tensor(X[tr_idx])
y_train = torch.tensor(y[tr_idx])
X_test = torch.tensor(X[te_idx])
y_test = torch.tensor(y[te_idx])

print(f'Dataset: N={N}, train={len(tr_idx)}, test={len(te_idx)}')


# experimento A: curva de entrenamiento
print('\n[A] convergencia')
N_RULES = 4
N_EPOCHS = 800

torch.manual_seed(SEED)
model_rand = ANFISLayer(n_inputs=2, n_rules=N_RULES)
losses_rand = entrenar(model_rand, X_train, y_train, n_epochs=N_EPOCHS, lr=0.01)

torch.manual_seed(SEED)
model_km = ANFISLayer(n_inputs=2, n_rules=N_RULES)
centros_km = init_mu_kmeans(model_km, X[tr_idx], N_RULES)
losses_km = entrenar(model_km, X_train, y_train, n_epochs=N_EPOCHS, lr=0.01, verbose=True)

# segundo lr para cumplir con "al menos 2 valores"
torch.manual_seed(SEED)
model_km_lr2 = ANFISLayer(n_inputs=2, n_rules=N_RULES)
init_mu_kmeans(model_km_lr2, X[tr_idx], N_RULES)
losses_km_lr2 = entrenar(model_km_lr2, X_train, y_train, n_epochs=N_EPOCHS, lr=0.005)

plt.figure(figsize=(9, 4.5))
plt.plot(losses_rand, label='aleatoria, lr=0.01', alpha=0.7)
plt.plot(losses_km, label='K-means, lr=0.01')
plt.plot(losses_km_lr2, label='K-means, lr=0.005', alpha=0.7)
plt.xlabel('Época')
plt.ylabel('MSE (train)')
plt.title('Convergencia del entrenamiento')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'expA_convergencia.png'), dpi=130)
plt.close()

print(f'  MSE final aleatoria  lr=0.01  : {losses_rand[-1]:.6f}')
print(f'  MSE final K-means    lr=0.01  : {losses_km[-1]:.6f}')
print(f'  MSE final K-means    lr=0.005 : {losses_km_lr2[-1]:.6f}')

# uso K-means + lr=0.01 para el resto de experimentos
model = model_km


# experimento B: predicción vs real
print('\n[B] predicción vs real')
model.eval()
with torch.no_grad():
    y_pred = model(X_test).numpy()
y_real = y_test.numpy()

mse = float(((y_pred - y_real) ** 2).mean())
rmse = float(np.sqrt(mse))
ss_res = float(((y_real - y_pred) ** 2).sum())
ss_tot = float(((y_real - y_real.mean()) ** 2).sum())
r2 = float(1 - ss_res / ss_tot)
print(f'  RMSE={rmse:.4f}  R2={r2:.4f}')

plt.figure(figsize=(5.2, 5.2))
plt.scatter(y_real, y_pred, alpha=0.6)
plt.plot([0, 1], [0, 1], 'r--', label='predicción perfecta')
plt.xlabel('ICT real')
plt.ylabel('ICT predicho')
plt.title(f'Predicción vs real (RMSE={rmse:.4f}, R²={r2:.3f})')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'expB_pred_vs_real.png'), dpi=130)
plt.close()


# experimento C: parámetros aprendidos por regla
print('\n[C] parámetros aprendidos')
mu_arr = model.mu.detach().numpy()
sigma_arr = model.sigma.detach().numpy()

reglas_info = []
print(f'{"Regla":<6}{"mu_T":>8}{"sg_T":>8}{"mu_O":>8}{"sg_O":>8}   Zona')
for i in range(N_RULES):
    mu_T, mu_O = mu_arr[i]
    sg_T, sg_O = sigma_arr[i]
    zona = f'T {etiqueta(mu_T)}, O {etiqueta(mu_O)}'
    print(f'R{i+1:<5}{mu_T:>8.3f}{sg_T:>8.3f}{mu_O:>8.3f}{sg_O:>8.3f}   {zona}')
    reglas_info.append({
        'regla': f'R{i+1}',
        'mu_T': float(mu_T), 'sigma_T': float(sg_T),
        'mu_O': float(mu_O), 'sigma_O': float(sg_O),
        'zona': zona,
    })


# experimento D: mapa de confort 2D
print('\n[D] mapa de confort')
xs = np.linspace(0, 1, 80)
ys = np.linspace(0, 1, 80)
TT, OO = np.meshgrid(xs, ys)
grid = np.column_stack([TT.ravel(), OO.ravel()]).astype(np.float32)
with torch.no_grad():
    Z_pred = model(torch.tensor(grid)).numpy().reshape(TT.shape)

# superficie teórica para comparar
Z_real = (np.exp(-((TT - 0.60) ** 2) / 0.06)
          * np.exp(-((OO - 0.55) ** 2) / 0.04))

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
c0 = axes[0].contourf(TT, OO, Z_pred, levels=20, cmap='viridis')
axes[0].scatter([0.6], [0.55], color='red', s=80, marker='*', label='óptimo experto')
axes[0].set_xlabel('T (norm)')
axes[0].set_ylabel('O (norm)')
axes[0].set_title('ICT aprendido por ANFIS')
axes[0].legend(loc='upper left')
plt.colorbar(c0, ax=axes[0])

c1 = axes[1].contourf(TT, OO, Z_real, levels=20, cmap='viridis')
axes[1].scatter([0.6], [0.55], color='red', s=80, marker='*')
axes[1].set_xlabel('T (norm)')
axes[1].set_ylabel('O (norm)')
axes[1].set_title('Criterio experto teórico')
plt.colorbar(c1, ax=axes[1])

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'expD_mapa_confort.png'), dpi=130)
plt.close()


# resumen JSON para la memoria
resumen = {
    'config': {
        'N': N, 'split': '80/20', 'seed': SEED,
        'n_rules': N_RULES, 'n_epochs': N_EPOCHS,
        'sigma_init': 0.5, 'p_init_scale': 0.1,
    },
    'mse_final': {
        'aleatoria_lr0.01': losses_rand[-1],
        'kmeans_lr0.01': losses_km[-1],
        'kmeans_lr0.005': losses_km_lr2[-1],
    },
    'test': {'rmse': rmse, 'r2': r2},
    'reglas': reglas_info,
    'centros_kmeans_iniciales': centros_km.tolist(),
}
with open(os.path.join(OUT_DIR, 'resumen_ej1.json'), 'w', encoding='utf-8') as f:
    json.dump(resumen, f, ensure_ascii=False, indent=2)

print(f'\nRMSE test={rmse:.4f}, R2={r2:.4f}')
print('gráficas y resumen guardados en', OUT_DIR)
