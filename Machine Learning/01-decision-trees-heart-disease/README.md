# Decision Trees for Heart Disease Diagnosis

Análise do impacto dos hiperparâmetros de uma árvore de decisão na capacidade de generalização de um modelo de diagnóstico clínico.

## O que foi feito

- **Pré-processamento**: análise de valores em falta e verificação de variáveis categóricas já codificadas numericamente.
- **Treino inicial**: split estratificado 80-20 (seed fixa), variando `min_samples_leaf` em `{1, 3, 5, 10, 25, 50, 100}` para observar o trade-off entre overfitting e underfitting.
- **Validação estruturada**: split 60-20-20 (treino/validação/teste), com procura em grelha sobre `max_depth ∈ [2, 4]` e `min_samples_leaf ∈ [2, 100]` para selecionar o modelo com melhor desempenho em validação, respeitando um limiar mínimo de exatidão em teste.
- **Interpretabilidade clínica**: análise dos nós-folha associados à classe positiva (doença cardíaca) para identificar os caminhos de decisão e as probabilidades posteriores associadas — ou seja, que combinações de variáveis clínicas mais se associam ao diagnóstico positivo.

## Resultados principais

- Valores baixos de `min_samples_leaf` levam a overfitting claro: alta exatidão em treino, mas instabilidade em teste.
- O modelo selecionado por validação atingiu ~77% de exatidão em teste, próximo do limiar-alvo de 78.5%.
- A análise dos nós-folha permitiu identificar quais variáveis clínicas mais contribuem para o diagnóstico positivo, dando ao modelo uma leitura interpretável e não apenas preditiva.

## Stack

`pandas` · `scikit-learn` (`DecisionTreeClassifier`) · `matplotlib`

## Como correr

```bash
pip install pandas scikit-learn matplotlib
jupyter notebook decision_trees.ipynb
```

> Nota: o notebook espera o ficheiro `hungarian_heart_diseases.csv` na mesma pasta.
