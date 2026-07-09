# FFCalc — Sistema de Análise de Fadiga e Fluência

O **FFCalc** é um sistema desenvolvido em Python para análise preliminar de fadiga, fluência, vida em serviço e dano acumulado em componentes metálicos.

O projeto tem como objetivo aplicar conceitos de **Engenharia Mecânica**, **Resistência dos Materiais**, **Materiais de Construção Mecânica** e **Análise de Falhas** em uma ferramenta computacional voltada ao estudo de componentes sujeitos a carregamentos cíclicos, altas temperaturas e mecanismos progressivos de dano.

> **Observação importante:** o FFCalc possui caráter educacional e preliminar. O sistema não substitui normas técnicas, ensaios experimentais, avaliações de integridade estrutural ou análises realizadas por profissionais habilitados.

---

## Objetivo do projeto

O objetivo principal do FFCalc é criar uma ferramenta técnica capaz de auxiliar no estudo de falhas mecânicas relacionadas a:

- fadiga mecânica;
- fluência em alta temperatura;
- vida útil e vida residual;
- dano acumulado;
- tensão alternada e tensão média;
- critérios preliminares de segurança;
- interpretação inicial de risco em componentes metálicos.

O sistema foi pensado como um projeto de portfólio técnico em Python, com aplicação direta em temas como manutenção industrial, integridade estrutural, equipamentos metálicos, indústria pesada, óleo e gás, offshore e análise de falhas.

---

## Funcionalidades iniciais

A primeira versão do sistema possui foco no módulo de fadiga.

### Módulo de fadiga

O sistema calcula:

- tensão máxima;
- tensão mínima;
- tensão alternada;
- tensão média;
- razão de carregamento;
- fator de segurança pelo critério de Goodman;
- fator de segurança pelo critério de Soderberg;
- fator de segurança pelo critério de Gerber;
- classificação preliminar de risco.

---

## Funcionalidades planejadas

As próximas versões do FFCalc poderão incluir:

### Fadiga

- curva S-N simplificada;
- dano acumulado de Miner;
- múltiplos blocos de carregamento;
- gráfico de Goodman;
- gráfico de vida em fadiga;
- exportação de resultados.

### Propagação de trinca

- cálculo de ΔK;
- Lei de Paris-Erdogan;
- estimativa de crescimento de trinca;
- vida restante até tamanho crítico de trinca.

### Fluência

- temperatura homóloga;
- avaliação preliminar de risco por fluência;
- Lei de Norton;
- taxa de fluência estacionária;
- parâmetro de Larson-Miller;
- estimativa preliminar de tempo até ruptura.

### Dano combinado

- dano por fadiga;
- dano por fluência;
- dano total;
- classificação preliminar da condição do componente.

### Relatórios

- geração de relatório técnico em PDF;
- exportação de gráficos;
- histórico de análises;
- comparação entre materiais e condições de operação.

---

## Estrutura do projeto

```text
FFCalc/
│
├── main.py
├── README.md
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── fadiga.py
│   └── classificacao.py
│
├── data/
│   └── materiais.csv
│
└── outputs/
```

---

## Tecnologias utilizadas

- Python
- NumPy
- Pandas
- Matplotlib

Futuramente, o projeto poderá utilizar também:

- SciPy;
- OpenPyXL;
- ReportLab;
- CustomTkinter.

---

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU-USUARIO/FFCalc.git
```

Entre na pasta do projeto:

```bash
cd FFCalc
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

### 3. Ativar o ambiente virtual

No Windows usando PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a ativação do ambiente virtual, use temporariamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois tente ativar novamente:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Executar o sistema

```bash
python main.py
```

---

## Exemplo de uso

Dados de entrada:

```text
Tensão máxima: 250 MPa
Tensão mínima: 50 MPa
Limite de fadiga: 200 MPa
Limite de resistência: 500 MPa
Limite de escoamento: 350 MPa
```

Resultados esperados aproximados:

```text
Tensão alternada: 100 MPa
Tensão média: 150 MPa
Razão de carregamento: 0,20

Fator de segurança por Goodman: 1,25
Fator de segurança por Soderberg: 1,08
Fator de segurança por Gerber: 1,69
```

---

## Conceitos utilizados

O projeto utiliza conceitos fundamentais de engenharia mecânica e materiais, como:

- tensão normal;
- tensão alternada;
- tensão média;
- razão de carregamento;
- limite de fadiga;
- limite de escoamento;
- limite de resistência;
- critérios de falha por fadiga;
- vida em serviço;
- dano acumulado;
- fluência em altas temperaturas.

---

## Limitações

O FFCalc ainda está em desenvolvimento e possui limitações importantes:

- os resultados são preliminares;
- os cálculos dependem da qualidade dos dados inseridos;
- não considera todos os efeitos de concentração de tensão;
- não substitui normas como ASME, API, ASTM ou procedimentos internos de engenharia;
- não substitui análise por elementos finitos;
- não substitui ensaios mecânicos, metalográficos ou fractográficos;
- não deve ser usado isoladamente para tomada de decisão em projeto real.

---

## Próximos passos

- [ ] Melhorar validação de entradas;
- [ ] Criar banco de materiais;
- [ ] Adicionar gráfico de Goodman;
- [ ] Adicionar curva S-N;
- [ ] Implementar dano acumulado de Miner;
- [ ] Implementar módulo inicial de fluência;
- [ ] Criar geração de relatório técnico;
- [ ] Criar interface gráfica simples;
- [ ] Adicionar testes automatizados;
- [ ] Melhorar documentação técnica.

---

## Autor

Desenvolvido por **Pedro Fernandes da Costa**.

Estudante de Engenharia Mecânica no CEFET/RJ, com interesse em Python aplicado à engenharia, análise de falhas, integridade estrutural, manutenção industrial, materiais metálicos, óleo e gás e indústria pesada.

---

## Licença

Este projeto está em desenvolvimento. A licença poderá ser definida futuramente.
