# README.md

# AgendaFácil — Sistema de Gestão de Agendamentos Clínicos

Projeto de refatoração, padronização e blindagem defensiva do núcleo de agendamentos clínicos, desenvolvido para a disciplina de Boas Práticas de Programação. O sistema realiza o gerenciamento de consultas médicas em memória, garantindo integridade temporal, validação de regras de negócio em formato *fail-fast* e desacoplamento entre regras de domínio e apresentação em console.

---

## 1. Estrutura do Projeto

```text
BPP/
├── agenda_base.py     # Núcleo da aplicação com regras de domínio, validações e demonstração
├── docs/              # Documentação de API estática gerada via pdoc
│   ├── agenda_base.html
│   ├── index.html
│   └── search.js
├── README.md          # Instruções de instalação, execução e documentação
└── RELATORIO.md       # Relatório de engenharia detalhando anomalias e refatoração

```

---

## 2. Pré-requisitos

* **Python 3.10** ou superior instalado no sistema operacional.
* Gerenciador de pacotes **pip** configurado no `PATH`.
* Biblioteca **pdoc** (para compilação e visualização da documentação HTML).

Para instalar a dependência de documentação, execute no terminal:

```powershell
pip install pdoc

```

---

## 3. Instruções de Execução

### Execução da Demonstração Principal

O arquivo `agenda_base.py` contém o fluxo padrão de demonstração clínica ao final do script. Para executá-lo:

```powershell
python agenda_base.py

```

#### Saída Esperada no Terminal:

```text
Atendimento marcado para Ana
Horario ocupado
Atendimento marcado para Carla
Remarcado
14 Carla Dra. Souza MARCADO

```

---

## 4. Geração da Documentação de API

A documentação da API foi estruturada utilizando **Sphinx/Google-Style Docstrings**, contemplando detalhadamente os contratos de parâmetros (`Args`), retorno (`Returns`) e exceções disparadas (`Raises`) para todas as entidades e funções públicas.

Para compilar ou atualizar os arquivos HTML da pasta `docs/`, execute:

```powershell
python -m pdoc -o docs agenda_base

```

### Visualização no Navegador

* **Pelo Windows Explorer:** Navegue até a pasta `docs/` e dê um duplo clique no arquivo `index.html`.
* **Pelo Servidor Local do pdoc (Modo Interativo):**
```powershell
python -m pdoc agenda_base

```


Abra a URL indicada no terminal (`http://localhost:8080`) no navegador de sua preferência.

---

## 5. Arquitetura e Decisões de Projeto

1. **Modelagem Orientada a Dados (`@dataclass`):**
* Substituição de listas aninhadas e índices numéricos mágicos (`ag[0]`, `ag[1]`) pela estrutura tipada `Agendamento`, provendo semântica e checagem estática de tipos.


2. **Programação Defensiva (*Fail-Fast*):**
* Eliminação de retornos silenciosos e blocos de captura cega (`except: pass`). Entradas inválidas (máscara de data divergente de `AAAA-MM-DD`, durações fora da faixa $[15, 120]$ ou não múltiplas de 15, e horários além do expediente comercial) disparam imediatamente exceções semânticas dedicadas (`DataInvalidaError`, `DuracaoInvalidaError`, `HorarioInvalidoError`, `AgendamentoNaoEncontradoError`).


3. **Desacoplamento de Responsabilidades (SRP):**
* Separação estrita entre funções de negócio (`agendar`, `validar_expediente`, `horario_ocupado`), que operam apenas transformações lógicas em memória sem efeitos colaterais visuais, e funções de interface CLI (`adicionar_consulta`, `remarcar_consulta`, `lista`), responsáveis pela formatação na saída padrão.


4. **Cálculo Preciso de Expediente Comercial:**
* O término do atendimento é projetado numericamente em fração decimal de hora ($\text{hora} + \frac{\text{duracao}}{60.0}$), impedindo que atendimentos iniciados dentro do expediente encerrem após o fechamento da clínica (18h).

---
