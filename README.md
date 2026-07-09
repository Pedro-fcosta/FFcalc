# FFCalc — Sistema de Análise de Fadiga e Fluência

O **FFCalc** é um sistema desenvolvido em Python para análise preliminar de **fadiga**, **fluência**, **vida em serviço** e **dano em componentes metálicos**.

O projeto aplica conceitos de Engenharia Mecânica, Resistência dos Materiais, Materiais de Construção Mecânica e Análise de Falhas em uma ferramenta computacional com interface gráfica e modo terminal.

> **Aviso importante:** o FFCalc possui caráter educacional e preliminar. O sistema não substitui normas técnicas, ensaios experimentais, avaliação de integridade estrutural, análise por elementos finitos ou avaliação feita por profissional habilitado.

---

## Visão geral

O FFCalc foi criado para estudar condições mecânicas associadas a dois mecanismos importantes de dano em componentes metálicos:

- **fadiga**, associada a carregamentos cíclicos;
- **fluência**, associada a tensão, tempo e temperatura elevada.

A versão atual possui:

- interface gráfica em **CustomTkinter**;
- modo terminal opcional;
- módulo de análise de fadiga;
- módulo de análise de fluência;
- banco inicial de materiais em CSV;
- gráficos técnicos;
- exportação de gráficos em PNG;
- validação básica de entradas e materiais.

---

## Funcionalidades atuais

### Módulo de fadiga

O módulo de fadiga calcula:

- tensão máxima;
- tensão mínima;
- tensão alternada;
- tensão média;
- razão de carregamento;
- fator de segurança por Goodman;
- fator de segurança por Soderberg;
- fator de segurança por Gerber;
- menor fator de segurança encontrado;
- classificação preliminar de risco;
- gráfico do diagrama de fadiga;
- gráfico comparativo dos fatores de segurança.

Critérios implementados:

```text
Goodman:
sigma_a / Se + sigma_m / Sut = 1 / n

Soderberg:
sigma_a / Se + sigma_m / Sy = 1 / n

Gerber:
sigma_a / Se + (sigma_m / Sut)^2 = 1 / n
```

Onde:

```text
sigma_a = tensão alternada
sigma_m = tensão média
Se      = limite de fadiga
Sut     = limite de resistência
Sy      = limite de escoamento
n       = fator de segurança
```

---

### Módulo de fluência

O módulo de fluência calcula:

- temperatura homóloga;
- taxa estimada de fluência;
- deformação acumulada;
- consumo do limite de deformação;
- tempo estimado até atingir o limite de deformação;
- classificação preliminar da condição;
- gráfico de taxa de fluência por temperatura;
- gráfico de deformação acumulada no tempo.

Modelo simplificado utilizado:

```text
Temperatura homóloga:
T_h = T_operacao / T_fusao

Lei de Norton com termo térmico tipo Arrhenius:
taxa = A * sigma^n * exp(-Q / (R * T))
```

Onde:

```text
A     = coeficiente de Norton
n     = expoente de Norton
sigma = tensão aplicada
Q     = energia de ativação
R     = constante universal dos gases
T     = temperatura absoluta em Kelvin
```

> Os parâmetros de fluência usados na versão atual são valores didáticos/presets simplificados. Para aplicação real, é necessário utilizar dados experimentais, normas aplicáveis e informações específicas do material.

---

## Interface gráfica

Por padrão, o sistema abre a interface gráfica.

```bash
python main.py
```

A interface possui:

- seleção entre os módulos **Fadiga** e **Fluência**;
- campos de entrada para os dados de cálculo;
- seleção de material;
- cards com os principais resultados;
- área de critérios;
- visualização gráfica;
- botão para salvar gráfico em PNG;
- botão para carregar exemplo.

---

## Modo terminal

Além da interface gráfica, o FFCalc também pode ser executado pelo terminal.

### Fadiga

```bash
python main.py --cli --modulo fadiga
```

### Fluência

```bash
python main.py --cli --modulo fluencia
```

---

## Exemplo de uso — fadiga

Entrada:

```text
sigma_max = 250 MPa
sigma_min = 50 MPa
material = Aco carbono generico
```

Propriedades do material:

```text
Se  = 200 MPa
Sut = 500 MPa
Sy  = 350 MPa
```

Resultados aproximados:

```text
sigma_a = 100 MPa
sigma_m = 150 MPa
R = 0.200

Goodman  = 1.25
Soderberg = 1.08
Gerber   = 1.69
```

Interpretação preliminar:

```text
A menor margem ocorre pelo critério de Soderberg.
Como o menor fator está entre 1 e 2, a condição exige atenção.
```

---

## Exemplo de uso — fluência

Entrada didática:

```text
tensao = 120 MPa
temperatura de operacao = 550 °C
temperatura de fusao = 1450 °C
tempo de operacao = 10000 h
A = 1.00e-02
n = 4.00
Q = 220 kJ/mol
deformacao limite = 1%
```

Resultados aproximados:

```text
Temperatura homóloga = 0.478
Taxa estimada = 2.272e-08 1/h
Deformação acumulada = 0.0227%
Consumo do limite = 2.27%
Tempo até limite ≈ 50.24 anos
```

Interpretação preliminar:

```text
Baixo consumo do limite de deformação para os dados informados.
```

---

## Banco de materiais

O arquivo de materiais fica em:

```text
data/materiais.csv
```

Formato atual:

```csv
id;material;limite_fadiga_mpa;limite_resistencia_mpa;limite_escoamento_mpa;observacao
1;Aco carbono generico;200;500;350;Valores didaticos para teste inicial
2;Aco ASTM A36;160;400;250;Valores aproximados para uso educacional
3;Aco ASTM A572 Gr 50;190;450;345;Valores aproximados para uso educacional
4;Aco inoxidavel austenitico generico;180;520;215;Valores aproximados para uso educacional
5;Aluminio 7075-T6;160;570;500;Valores aproximados para uso educacional
```

Observações:

- o separador usado é `;`;
- os nomes estão sem acento para evitar problemas de codificação no Windows;
- os valores são didáticos e aproximados;
- o sistema valida colunas obrigatórias e valores numéricos;
- o arquivo é lido com tratamento para codificação `utf-8-sig` e `latin1`.

---

## Estrutura do projeto

```text
FFcalc/
│
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   └── materiais.csv
│
├── outputs/
│   ├── grafico_fadiga.png
│   └── grafico_fluencia.png
│
└── src/
    ├── __init__.py
    ├── analise.py
    ├── analise_fadiga.py
    ├── analise_fluencia.py
    ├── classificacao.py
    ├── fadiga.py
    ├── fluencia.py
    ├── gui.py
    └── materiais.py
```

---

## Papel dos principais arquivos

### `main.py`

Arquivo principal do projeto.

Responsável por:

- iniciar a interface gráfica por padrão;
- permitir execução via terminal;
- controlar argumentos de linha de comando;
- chamar o módulo de fadiga ou fluência.

---

### `src/fadiga.py`

Contém as funções fundamentais de cálculo de fadiga:

- parâmetros do ciclo;
- Goodman;
- Soderberg;
- Gerber.

---

### `src/analise_fadiga.py`

Camada de análise do módulo de fadiga.

Responsável por:

- receber entradas;
- usar propriedades do material;
- calcular os fatores de segurança;
- aplicar classificações preliminares;
- organizar os resultados em dicionários.

---

### `src/fluencia.py`

Contém as funções fundamentais de cálculo de fluência:

- conversão de Celsius para Kelvin;
- temperatura homóloga;
- taxa de fluência por Norton-Arrhenius;
- deformação acumulada;
- tempo estimado até deformação limite.

---

### `src/analise_fluencia.py`

Camada de análise do módulo de fluência.

Responsável por:

- aplicar presets didáticos por tipo de material;
- calcular resultados principais;
- classificar temperatura homóloga, taxa estimada e consumo do limite;
- organizar os resultados em dicionários.

---

### `src/gui.py`

Contém a interface gráfica do sistema.

Responsável por:

- layout visual;
- alternância entre os módulos;
- entradas do usuário;
- seleção de material;
- cards de resultado;
- gráficos;
- exportação de gráficos em PNG.

---

### `src/materiais.py`

Responsável por:

- carregar `data/materiais.csv`;
- tratar codificação;
- validar colunas obrigatórias;
- converter colunas numéricas;
- listar materiais no terminal;
- permitir seleção de material por ID no modo CLI.

---

### `src/classificacao.py`

Contém a função de classificação preliminar pelo fator de segurança.

---

## Tecnologias utilizadas

- Python
- Pandas
- NumPy
- Matplotlib
- CustomTkinter
- Pillow

As demais bibliotecas presentes no `requirements.txt` são dependências auxiliares instaladas junto com os pacotes principais.

---

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/Pedro-fcosta/FFcalc.git
```

### 2. Entrar na pasta

```bash
cd FFcalc
```

### 3. Criar ambiente virtual

```bash
python -m venv .venv
```

### 4. Ativar ambiente virtual no Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a ativação, execute:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois tente ativar novamente:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Instalar dependências

```bash
pip install -r requirements.txt
```

### 6. Executar o sistema

Interface gráfica:

```bash
python main.py
```

Modo terminal — fadiga:

```bash
python main.py --cli --modulo fadiga
```

Modo terminal — fluência:

```bash
python main.py --cli --modulo fluencia
```

---

## Dependências

O projeto utiliza as dependências listadas em `requirements.txt`.

Exemplo de pacotes principais:

```text
customtkinter
matplotlib
numpy
pandas
pillow
```

---

## Limitações técnicas

O FFCalc ainda está em desenvolvimento e possui limitações importantes:

- os cálculos são preliminares;
- os valores dos materiais no CSV são didáticos;
- os critérios de fadiga são simplificados;
- a influência de acabamento superficial, tamanho, temperatura, confiabilidade e concentração de tensão ainda não está implementada;
- não há curva S-N completa nesta versão;
- não há dano acumulado de Miner nesta versão;
- não há propagação de trinca por Lei de Paris nesta versão;
- a análise de fluência usa modelo simplificado;
- os presets de fluência não substituem dados experimentais;
- não há validação por normas técnicas;
- não deve ser usado para tomada de decisão em projeto real.

---

## Funcionalidades planejadas

Próximas melhorias possíveis:

- implementar curva S-N;
- adicionar fatores modificadores do limite de fadiga;
- adicionar fator de concentração de tensão;
- implementar dano acumulado de Miner;
- adicionar múltiplos blocos de carregamento;
- implementar propagação de trinca por Lei de Paris-Erdogan;
- melhorar o banco de materiais com fontes técnicas;
- implementar relatório técnico em PDF;
- adicionar testes automatizados;
- melhorar validações de entrada;
- adicionar logs;
- criar empacotamento executável;
- melhorar documentação técnica das equações.

---

## Status atual

O projeto está em fase inicial funcional.

A versão atual já permite:

- executar o sistema por interface gráfica;
- executar os módulos pelo terminal;
- calcular parâmetros básicos de fadiga;
- calcular parâmetros preliminares de fluência;
- selecionar materiais de um CSV;
- visualizar gráficos;
- salvar gráficos em PNG.

Ainda não é uma versão final de engenharia, mas já funciona como ferramenta educacional e projeto de portfólio técnico.

---

## Autor

Desenvolvido por **Pedro Fernandes da Costa**.

Estudante de Engenharia Mecânica no CEFET/RJ, com interesse em Python aplicado à engenharia, análise de falhas, integridade estrutural, materiais metálicos, manutenção industrial, óleo e gás e indústria pesada.

---

## Licença

Este projeto ainda não possui uma licença definida.
