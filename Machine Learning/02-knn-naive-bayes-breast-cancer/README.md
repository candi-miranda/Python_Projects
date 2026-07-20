# kNN vs. Naïve Bayes — Breast Cancer Diagnosis

Comparação estatisticamente rigorosa entre dois classificadores clássicos aplicados ao diagnóstico de cancro da mama, com foco na validade estatística das conclusões — não apenas em quem "ganha".

## O que foi feito

- **Baseline**: comparação de exatidão entre kNN (k=5) e Naïve Bayes gaussiano com validação cruzada estratificada, avaliando também a estabilidade (desvio-padrão) de cada modelo.
- **Impacto do pré-processamento**: reavaliação do kNN após normalização Min-Max, para isolar o efeito da escala de features num classificador baseado em distância.
- **Significância estatística**: teste estatístico (via `scipy`) para determinar se a melhoria observada no kNN escalado é estatisticamente significativa face ao Naïve Bayes, evitando concluir por diferenças que podem ser ruído amostral.
- **Estudo de sensibilidade**: variação de `k ∈ {1, 5, 10, 15, 20, 25}` com pesos uniformes vs. pesados pela distância, analisando o trade-off entre viés e variância.
- **Discussão aplicada**: análise crítica de qual classificador seria mais apropriado num contexto clínico real, considerando não só exatidão mas também interpretabilidade e custo de erros.

## Resultados principais

- Após normalização, a exatidão do kNN subiu de ~93.5% para ~96.3%, confirmando a sensibilidade deste método à escala das features.
- Apesar da melhoria, o teste estatístico (p ≈ 0.068) não confirmou superioridade estatisticamente significativa do kNN escalado sobre o Naïve Bayes — uma conclusão relevante que só a validação cruzada + teste estatístico permite tirar (comparar apenas médias seria enganador).

## Stack

`pandas` · `scikit-learn` (`KNeighborsClassifier`, `GaussianNB`) · `scipy`

## Como correr

```bash
pip install pandas scikit-learn scipy
jupyter notebook knn_vs_naive_bayes.ipynb
```

> Nota: o notebook espera o ficheiro `Breast_cancer_dataset.csv` na mesma pasta.
