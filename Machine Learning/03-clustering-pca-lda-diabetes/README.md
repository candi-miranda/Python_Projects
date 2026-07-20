# Clustering, PCA & LDA — Diabetes Risk Analysis

Exploração não-supervisionada e redução de dimensionalidade aplicada a dados clínicos, comparando abordagens de agrupamento e de projeção para separação de classes.

## O que foi feito

**Parte A — Clustering**
- K-Means com `k ∈ {2, ..., 11}`, análise do SSE (curva do cotovelo) para escolha do número de clusters.
- Atribuição de rótulos por maioria de classe em cada cluster (k=6), avaliando exatidão, precisão e outras métricas de classificação indireta.
- Identificação dos clusters mais discriminativos e interpretação clínica dos seus centros (que perfis de pacientes cada cluster representa).

**Parte B — Redução de dimensionalidade**
- PCA com análise da variância explicada acumulada, para decidir quantas componentes reter.
- Visualização da distribuição de classes ao longo da 1ª componente principal.
- LDA como alternativa supervisionada, otimizada diretamente para separação de classes.
- Comparação crítica entre PCA e LDA quanto à adequação para construir uma regra discriminante.

## Resultados principais

- O agrupamento por K-Means (k=6) atingiu ~70% de exatidão indireta na distinção diabético/não-diabético, com clusters claramente dominados por uma das classes (ex: um cluster com 254 não-diabéticos vs. 26 diabéticos).
- O PC1 da PCA mostrou sobreposição considerável entre classes — esperado, já que a PCA otimiza variância total e não separação de classes.
- A LDA, apesar de otimizada para separação, ainda revelou sobreposição relevante, sugerindo que as features disponíveis não separam perfeitamente as classes — uma conclusão importante sobre os limites do dataset, não do método.

## Stack

`pandas` · `scikit-learn` (`KMeans`, `PCA`, `LDA`) · `matplotlib`

## Como correr

```bash
pip install pandas scikit-learn matplotlib
jupyter notebook clustering_pca_lda.ipynb
```

> Nota: o notebook espera o ficheiro `diabetes.csv` na mesma pasta.
