# FFCalc - Sistema de Analise de Fadiga e Fluencia

O **FFCalc** e um sistema em Python para analise preliminar e educacional de fadiga, fluencia e comparacao de materiais metalicos. O projeto possui interface grafica em CustomTkinter, modo terminal, banco de materiais em CSV e graficos com Matplotlib.

> Observacao importante: o FFCalc tem carater didatico e preliminar. Ele nao substitui normas tecnicas, ensaios experimentais, propriedades reais certificadas, avaliacao de integridade estrutural ou analise de profissional habilitado.

## Funcionalidades

- Interface grafica em CustomTkinter.
- Modo terminal opcional.
- Banco de materiais em `data/materiais.csv`.
- Modulo de Fadiga.
- Modulo de Fluencia.
- Modulo Dashboard para comparacao preliminar de materiais.
- Graficos integrados com Matplotlib.
- Exportacao de graficos em PNG para a pasta `outputs/`.

## Modulo de Fadiga

O modulo de fadiga calcula parametros de carregamento ciclico e fatores de seguranca preliminares.

Entradas principais:

- tensao maxima `sigma_max` [MPa];
- tensao minima `sigma_min` [MPa];
- material selecionado no banco CSV.

Resultados:

- tensao alternada;
- tensao media;
- razao de carregamento `R`;
- fator de seguranca por Goodman;
- fator de seguranca por Soderberg;
- fator de seguranca por Gerber;
- classificacao preliminar de risco;
- grafico `sigma_m x sigma_a`;
- grafico comparativo dos fatores de seguranca.

## Modulo de Fluencia

O modulo de fluencia estima, de forma didatica, indicadores preliminares de risco por fluencia.

Entradas principais:

- tensao aplicada [MPa];
- temperatura de operacao [C];
- temperatura de fusao [C];
- tempo de operacao [h];
- coeficiente de Norton `A`;
- expoente de Norton `n`;
- energia de ativacao `Q` [kJ/mol];
- deformacao limite [%].

Resultados:

- temperatura homologa `T/Tf`;
- taxa estimada de fluencia;
- deformacao acumulada;
- tempo estimado ate o limite informado;
- consumo do limite de deformacao;
- classificacao preliminar;
- grafico de taxa por temperatura;
- grafico de deformacao acumulada no tempo.

## Modulo Dashboard

O Dashboard compara todos os materiais cadastrados sob uma mesma condicao de operacao. A ideia e responder, de forma preliminar:

> Para esta tensao, temperatura e tempo de operacao, quais materiais parecem mais adequados?

Entradas:

- tensao maxima de fadiga `sigma_max` [MPa];
- tensao minima de fadiga `sigma_min` [MPa];
- tensao de operacao para fluencia `sigma_creep` [MPa];
- temperatura de operacao [C];
- tempo de operacao [h];
- deformacao limite [%].

O Dashboard calcula, para cada material:

- menor fator de seguranca em fadiga;
- consumo estimado do limite de deformacao por fluencia;
- temperatura homologa;
- classificacao preliminar de fadiga;
- classificacao preliminar de fluencia;
- score geral de adequacao preliminar;
- ranking ordenado de materiais.

Graficos do Dashboard:

- fator de seguranca em fadiga por material;
- consumo do limite de fluencia por material;
- score geral por material.

O resultado usa termos como "mais adequado preliminarmente", "avaliar com cautela" e "pouco adequado preliminarmente". Ele nao indica selecao definitiva de material para projeto real.

## Banco de materiais

O arquivo principal e:

```text
data/materiais.csv
```

Colunas obrigatorias:

- `id`
- `material`
- `limite_fadiga_mpa`
- `limite_resistencia_mpa`
- `limite_escoamento_mpa`
- `observacao`

O Dashboard funciona mesmo sem propriedades especificas de fluencia no CSV. Quando essas propriedades nao existem, o sistema usa presets didaticos por tipo de material.

Colunas opcionais futuras:

- `temperatura_fusao_c`
- `norton_a`
- `norton_n`
- `energia_ativacao_kj_mol`

## Como executar

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

Execute a interface grafica:

```powershell
python main.py
```

Execute o modo terminal:

```powershell
python main.py --cli --modulo fadiga
python main.py --cli --modulo fluencia
python main.py --cli --modulo dashboard
```

## Exportacao de graficos

Os graficos sao salvos em:

```text
outputs/
```

Arquivos gerados:

- `grafico_fadiga.png`
- `grafico_fluencia.png`
- `grafico_dashboard.png`

## Estrutura do projeto

```text
FFCalc/
|-- main.py
|-- README.md
|-- requirements.txt
|-- data/
|   |-- materiais.csv
|-- outputs/
|-- src/
|   |-- analise.py
|   |-- analise_dashboard.py
|   |-- analise_fadiga.py
|   |-- analise_fluencia.py
|   |-- classificacao.py
|   |-- fadiga.py
|   |-- fluencia.py
|   |-- gui.py
|   |-- materiais.py
|   |-- __init__.py
```

## Melhorias planejadas

- Banco de materiais mais robusto.
- Propriedades reais de fluencia por material.
- Fontes normativas e rastreabilidade de dados.
- Curvas S-N por material.
- Dano acumulado de Miner.
- Lei de Paris para propagacao de trinca.
- Criterios mais avancados de selecao preliminar de materiais.
- Relatorios tecnicos em PDF.
- Historico de analises.

## Tecnologias

- Python
- CustomTkinter
- Pandas
- NumPy
- Matplotlib
