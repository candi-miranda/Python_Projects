# Linear Regression vs. MLP — Rent Prediction

Implementação manual de um pipeline de treino e validação cruzada para comparar um modelo linear com redes neuronais de complexidade crescente na previsão de valores de arrendamento.

## O que foi feito

- **Função de treino e validação cruzada manual**, sem depender apenas de utilitários prontos do scikit-learn, para maior controlo sobre o processo de avaliação (`KFold`, `cross_val_score`).
- Comparação entre três modelos:
  - Regressão Linear (baseline)
  - MLP Regressor (2 camadas ocultas, 5 neurónios cada, sem função de ativação — equivalente a um modelo linear "disfarçado")
  - MLP Regressor (2 camadas ocultas, 5 neurónios cada, ativação ReLU)
- Análise de **curvas de perda (loss curves)** do MLP com ReLU ao longo das épocas, para diagnosticar overfitting vs. underfitting.
- Discussão crítica sobre a magnitude do erro (MAE/MSE) e não só a forma da curva — evitando conclusões otimistas prematuras.

## Resultados principais

- O treino manual teve desempenho ligeiramente superior ao pipeline automático, sem diferenças notáveis entre MLP e regressão linear — indício de limitações nos dados (ruído, features pouco informativas ou não-linearidades fracas) mais do que na capacidade dos modelos.
- A curva de perda do MLP com ReLU melhora ao longo das épocas, mas a ordem de grandeza do erro final revela que a "melhoria" visual não se traduz necessariamente em qualidade preditiva prática.

## Stack

`pandas` · `numpy` · `scikit-learn` (`LinearRegression`, `Ridge`, `MLPRegressor`) · `matplotlib`

## Como correr

```bash
pip install pandas numpy scikit-learn matplotlib
jupyter notebook regression_models.ipynb
```

> Nota: o notebook espera o ficheiro `rent.csv` na mesma pasta.
