# 📊 Dashboard de Ventas

## Top Clientes
```dataview
TABLE cliente, sum(importe) as Total_Ventas
FROM "Facturas"
GROUP BY cliente
SORT Total_Ventas DESC
```

## Producto más vendido
```dataview
TABLE producto, sum(importe) as Total
FROM "Facturas"
GROUP BY producto
SORT Total DESC
LIMIT 1
```

## Grafo de relaciones
→ Abre el **Graph View** filtrado en `Proyecto/`.
