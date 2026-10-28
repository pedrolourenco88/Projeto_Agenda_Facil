**DIM0501 — Boas Práticas de Programação**

**Relatório do Projeto da Unidade 1 — AgendaFácil**

Modelo de entrega — serve para Python, Java e C++

Prof. Marcus Terra   ·   DIMAp/UFRN   ·   Semestre 2026.1   ·   Entrega: 25/10/2026

| Integrantes (nome e matrícula) | Linguagem |
| :---- | :---- |
| Pedro Murilo Matias Lourenço \- 20250043694 | Python |
| **Repositório ou arquivo entregue** |  |
| https\://github.com/pedrolourenco88/Projeto\_Agenda\_Facil |  |

**1\. Diagnóstico do código-base**

| \# | Categoria | Anomalia e onde está | Por que é um problema |
| :---- | :---- | :---- | :---- |
| 1  | Organização e estética. | Nomes confusos de variáveis e funções. Em todo o código. | Dificulta a identificação de funções e variáveis. |
| 2   | Manutenibilidade.  | Muitos if’s aninhados. Na função que  adiciona um paciente a lista. | Aumento desnecessário de complexidade. |
| 3  | Manutenibilidade.  | Código morto solto no meio do programa. |  Poluição visual. |
| 4 | Organização e estética. | Comentários redundantes após a declaração de cada função. | Poluição visual, não agrega para o código. Apenas me diz o que ele faz. |
| 5  | Adequação lógica. | Função rem ao pesquisar o paciente/horário original. | Se o agendamento a remarcar não existir na lista,  a função  não está preparada para isso. |
| 6 | Programação defensiva e segurança. |  Bloco except: pass silencioso na função add. | Ocultação de bugs e dificuldade no debug. |
| 7 | Programação defensiva e segurança.  | Ausência de validação de formato da data e duração. | A data pode entrar  errada e causar um erro na consulta, quanto a duração se não for colocada em minutos, também ocorre erros. |
| 8 | Desempenho e recursos. | Uso de variável global mutável (ag \= \[\]) com varreduras completa. | Buscas lineares em lista global aumentam o tempo de resposta conforme o histórico de agendamentos cresce.  |
| 9 | Manutenibilidade  | Valores literais soltos(8 , 18). | Caso queira mudar os valores tenho que procurá-los no código dificultando a manutenção |
| 10 | Adequação lógica.  | Função lst, O comentário declara que  lista os atendimentos do mês, mas na implementação é filtrado apenas um dia específico.  | Isso induz o usuário ou outro desenvolvedor a erro quanto ao escopo da consulta. |

**2\. O que foi resolvido e o que ficou como dívida**

| \# | Situação | Como foi resolvida, ou por que ficou |
| :---- | :---- | :---- |
| 1 | Resolvida  | Variáveis e funções crípticas (ag, add, rem, lst, p, d, h) foram renomeadas para identificadores semânticos (agendamentos, adicionar\_consulta, remarcar\_consulta, lista, paciente, data, hora). |
| 2 | Resolvida | Os ifs aninhados foram substituídos por cláusulas de guarda (fail-fast) com extração das regras de validação para funções puras dedicadas (validar\_formato\_data, validar\_duracao, validar\_expediente). |
| 3 | Resolvida | Código morto (\# def desmarcar...) e comentários de tarefas obsoletas (\# TODO: rever isso depois...) foram completamente removidos do módulo. |
| 4 | Resolvida | Comentários redundantes foram apagados e substituídos por contratos formais de documentação no padrão Sphinx/Google Style (Args, Returns, Raises). |
| 5 | Resolvida | A ausência do agendamento passou a ser tratada com a cláusula defensiva if agendamento is None:, disparando imediatamente a exceção semântica AgendamentoNaoEncontradoError. |
| 6 | Resolvida | O bloco except: pass foi eliminado. As validações agora atuam ativamente (fail-fast) lançando exceções específicas herdadas de ClinicaError com mensagens descritivas do valor rejeitado. |
| 7 | Resolvida | Implementaram-se validar\_formato\_data (via datetime.strptime(..., "%Y-%m-%d")) e validar\_duracao (exigindo inteiros no intervalo \[15, 120\] e múltiplos de 15), disparando DataInvalidaError e DuracaoInvalidaError. |
| 8 | Dívida assumida | A lista global agendamentos \= \[\] foi mantida no escopo modular para preservar estritamente a assinatura e o script procedural do exercício. A dívida foi mitigada encapsulando seu acesso por meio de funções de domínio puras (agendar, buscar\_agendamento). |
| 9 | Resolvida | Os literais soltos foram transformados em constantes explícitas em caixa-alta no topo do arquivo (HORA\_MINIMA, HORA\_MAXIMA, HORA\_INICIO\_EXPEDIENTE, HORA\_FIM\_EXPEDIENTE, DURACAO\_MINIMA\_MINUTOS, etc.). |
| 10 | Resolvida | O comentário enganoso sobre listagem mensal foi substituído por uma docstring que detalha que a função filtra e exibe exclusivamente os atendimentos da data (dia) informada. |

**3\. Decisões de projeto**

| Decisão tomada | Alternativa descartada | Por que decidimos assim |
| :---- | :---- | :---- |
| Modelagem do agendamento com @dataclass nominal. | Manter tuplas ou listas de listas (ag\[i\]\[0\]), ou usar dicionários com chaves em string. | Garante integridade estrutural, verificação estática de tipos, documentação via Attributes e elimina o risco de erros silenciosos por inversão posicional de índices. |
| Cálculo do término de atendimento em fração decimal de hora (hora \+ duracao / 60.0) | Importar e instanciar múltiplos objetos datetime.timedelta e manipular horas parciais como texto. | Permite comparação numérica direta contra HORA\_FIM\_EXPEDIENTE de forma rápida e matematicamente exata, sem adicionar overhead de conversões temporais extras. |
| Separação em camada de domínio (agendar) e camada de console (adicionar\_consulta). | Misturar regras com print() internamente ou obrigar o script principal a manipular condicionais para cada agendamento. | Cumpre o Princípio da Responsabilidade Única (SRP): quem agenda opera em memória sem efeitos colaterais visuais; quem formata a saída gerencia o console mantendo a demonstração idêntica. |

**4\. Mudanças de comportamento**

| Entrada ou situação | O que acontecia antes | O que acontece agora |
| :---- | :---- | :---- |
| Data fora do padrão AAAA-MM-DD (ex.: "05/10/2026" ou "2026-02-30"). | A string era inserida na lista sem verificação, gerando corrupção silenciosa da base e falhas em buscas posteriores. | Dispara imediatamente DataInvalidaError indicando a máscara exigida e barrando a gravação. |
| Duração arbitrária ou não múltipla de 15 (ex.: 40 min). | Era aceita e gravada na lista porque o código antigo apenas conferia se duracao \> 0 . | Dispara DuracaoInvalidaError exigindo que o procedimento seja múltiplo estrito de 15 minutos. |
| Duração fora da faixa operacional (ex.: 150 min). | O procedimento era agendado sem qualquer restrição de tempo máximo. | Dispara DuracaoInvalidaError informando que o limite permitido está entre 15 e 120 minutos.   |
| Consulta iniciando às 17h com 120 minutos de duração. | Era marcada normalmente porque 17 \< 18, invadindo o horário pós-fechamento (término às 19h). | Dispara HorarioInvalidoError ao constatar que o término projetado 19h ultrapassa as 18h |
| Remarcação de paciente ou horário inexistente. | A função varria a lista, não encontrava o registro e finalizava sem aviso nem retorno (falha silenciosa). | Interrompe o fluxo e dispara AgendamentoNaoEncontradoError detalhando o paciente, data e hora ausentes. |

**5\. Como executar e gerar a documentação**

| Item | Resposta |
| :---- | :---- |
| Comando para compilar e executar | python agenda\_base.py |
| Comando para gerar a documentação de API | python \-m pdoc \-o docs agenda\_base |
| Onde a documentação gerada ficou no repositório | Na pasta docs/ na raiz do projeto (arquivos docs/agenda\_base.html, docs/index.html e docs/search.js). |
| Saída do programa de demonstração (cole aqui) | Atendimento marcado para Ana Horario ocupado Atendimento marcado para Carla Remarcado 14 Carla Dra. Souza MARCADO |

**6\. Uso de ferramentas de IA**

| Pergunta | Resposta |
| :---- | :---- |
| Foram usadas ferramentas de IA neste trabalho? | (   ) Não        (**X**) Sim |
| Em quais etapas, e para quê? | Utilizada como ferramenta de suporte nas Etapas 2, 3 e 4: para projetar a separação arquitetural entre funções de negócio e funções de apresentação CLI (preservando a saída da demonstração), modelar o padrão de docstrings Google-Style com suporte ao pdoc e formular os casos de teste da programação defensiva (fail-fast). |

