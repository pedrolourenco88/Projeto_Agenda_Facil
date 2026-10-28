from dataclasses import dataclass
from datetime import datetime

agendamentos = []
HORA_MINIMA = 8
HORA_MAXIMA = 18
DURACAO_MINIMA_MINUTOS = 15
DURACAO_MAXIMA_MINUTOS = 120
INCREMENTO_MINUTOS = 15
HORA_INICIO_EXPEDIENTE = 8
HORA_LIMITE_INICIO = 17
HORA_FIM_EXPEDIENTE = 18

class ClinicaError(Exception):
    """Classe base para todas as exceções de domínio do AgendaFácil."""
    pass

class DataInvalidaError(ClinicaError, ValueError):
    """Lançada quando a string de data viola o formato AAAA-MM-DD ou calendário."""
    pass

class DuracaoInvalidaError(ClinicaError, ValueError):
    """Lançada quando a duração não atende à faixa [15, 120] ou não é múltipla de 15."""
    pass

class HorarioInvalidoError(ClinicaError, ValueError):
    """Lançada quando o início ou término da consulta viola o expediente comercial."""
    pass

class AgendamentoNaoEncontradoError(ClinicaError, LookupError):
    """Lançada ao tentar operar sobre um agendamento inexistente."""
    pass

@dataclass
class Agendamento:
    """Representa um atendimento clínico agendado na clínica.

    Attributes:
        paciente (str): Nome do paciente atendido.
        profissional (str): Nome ou identificação do profissional de saúde.
        data (str): Data da consulta no formato estrito AAAA-MM-DD.
        hora (int): Hora cheia de início do atendimento (8 às 17).
        duracao (int): Duração estimada em minutos (15 a 120, múltipla de 15).
        status (str): Situação cadastral do atendimento (padrão: "MARCADO").
    """
    paciente: str
    profissional: str
    data: str
    hora: int
    duracao: int
    status: str = "MARCADO"

def validar_formato_data(data_texto: str) -> None:
    """Valida se uma representação textual de data atende ao padrão AAAA-MM-DD.

    Garante que a string segue o formato exigido pelo sistema e que representa
    uma data válida no calendário gregoriano (evitando dias inexistentes como 30 de fevereiro).

    Args:
        data_texto (str): Texto contendo a data a ser verificada.

    Returns:
        None: Apenas retorna se a validação for bem-sucedida.

    Raises:
        DataInvalidaError: Se a string não corresponder à máscara AAAA-MM-DD ou se
            for uma data inexistente no calendário.
    """

    try:
        data_convertida = datetime.strptime(data_texto, "%Y-%m-%d")
        # Garante que não houve truncamento ou formatos variantes aceitos pelo C-parser
        if data_convertida.strftime("%Y-%m-%d") != data_texto:
            raise ValueError
    except (ValueError, TypeError):
        raise DataInvalidaError(
            f"Data '{data_texto}' inválida. O formato obrigatório é AAAA-MM-DD."
        )

def validar_duracao(duracao: int) -> None:
    """Verifica se a duração em minutos cumpre as regras de agendamento da clínica.

    A duração deve ser estritamente um valor inteiro compreendido no intervalo
    de 15 a 120 minutos e múltipla de 15 minutos.

    Args:
        duracao (int): Duração da consulta em minutos.

    Returns:
        None: Retorna caso o valor seja válido.

    Raises:
        DuracaoInvalidaError: Se o tipo for inválido, se o valor estiver fora da
            faixa [15, 120] ou se não for múltiplo de 15.
    """
    
    if not isinstance(duracao, int) or isinstance(duracao, bool):
        raise DuracaoInvalidaError(f"Duração deve ser um número inteiro, recebido: {type(duracao).__name__}.")
        
    if duracao < DURACAO_MINIMA_MINUTOS or duracao > DURACAO_MAXIMA_MINUTOS:
        raise DuracaoInvalidaError(
            f"Duração de {duracao} min fora da faixa permitida "
            f"({DURACAO_MINIMA_MINUTOS} a {DURACAO_MAXIMA_MINUTOS} minutos)."
        )
        
    if duracao % INCREMENTO_MINUTOS != 0:
        raise DuracaoInvalidaError(
            f"Duração de {duracao} min inválida. Deve ser múltipla de {INCREMENTO_MINUTOS} minutos."
        )

def validar_expediente(hora_inicio: int, duracao_minutos: int) -> None:
    """Valida se o início e a conclusão da consulta respeitam o horário comercial.

    Verifica se a hora de início está compreendida entre as 8h e 17h e se a projeção
    de término do procedimento não ultrapassa o fechamento da clínica às 18h.

    Args:
        hora_inicio (int): Hora inteira de início do atendimento.
        duracao_minutos (int): Duração prevista em minutos.

    Returns:
        None: Retorna caso os horários respeitem os limites comerciais.

    Raises:
        HorarioInvalidoError: Se a hora de início for anterior às 8h, posterior às 17h
            ou se a soma da duração projetar término após as 18h.
    """
    if not isinstance(hora_inicio, int) or isinstance(hora_inicio, bool):
        raise HorarioInvalidoError(f"Horário de início inválido: {hora_inicio}.")

    if hora_inicio < HORA_INICIO_EXPEDIENTE or hora_inicio > HORA_LIMITE_INICIO:
        raise HorarioInvalidoError(
            f"Horário de início {hora_inicio}h fora do expediente permitido "
            f"({HORA_INICIO_EXPEDIENTE}h às {HORA_LIMITE_INICIO}h)."
        )

    termino_horas = hora_inicio + (duracao_minutos / 60.0)
    if termino_horas > HORA_FIM_EXPEDIENTE:
        raise HorarioInvalidoError(
            f"Atendimento iniciando às {hora_inicio}h com {duracao_minutos} min "
            f"terminaria às {termino_horas:.2f}h, ultrapassando o encerramento da clínica ({HORA_FIM_EXPEDIENTE}h)."
        )

def horario_ocupado(profissional: str, data: str, hora: int):
    """Informa se determinado profissional já possui consulta agendada no horário.

    Args:
        profissional (str): Nome do profissional avaliado.
        data (str): Data da consulta (AAAA-MM-DD).
        hora (int): Hora de início do atendimento.

    Returns:
        bool: True se já houver registro conflitante para o profissional na data/hora;
            False se o horário estiver livre.
    """

    for agendamento in agendamentos:
        if agendamento.data == data and agendamento.hora == hora and agendamento.profissional == profissional:
            return True #horario ocupado
    return False

def validar_horario(hora: int, duracao: int):
    """Verifica de forma preliminar se a hora e a duração cumprem os limites operacionais básicos.

    Atua como um predicado booleano que avalia se a hora inicial se encontra dentro
    do intervalo de funcionamento padrão e se a duração informada é estritamente positiva.

    Args:
        hora (int): Hora inteira de início do atendimento clínico.
        duracao (int): Duração estimada para o atendimento em minutos.

    Returns:
        bool: True se a hora estiver no intervalo [HORA_MINIMA, HORA_MAXIMA) e
            a duração for maior que zero; False caso contrário.

    Raises:
        None: Esta função opera como predicado booleano puro e não dispara exceções.
    """
    
    if hora < HORA_MINIMA or hora >= HORA_MAXIMA:
        return False
    if duracao <= 0:
        return False
    return True

def buscar_agendamento(paciente: str, data: str, hora: int):
    """Localiza um agendamento existente na base de dados em memória.

    Args:
        paciente (str): Nome do paciente vinculado à consulta.
        data (str): Data do agendamento (AAAA-MM-DD).
        hora (int): Hora de início do agendamento.

    Returns:
        Agendamento | None: Instância do agendamento correspondente ou None caso
            nenhum registro seja encontrado com os filtros informados.
    """
    
    for agendamento in agendamentos:
        if agendamento.paciente == paciente and agendamento.data == data and agendamento.hora == hora:
            return agendamento
    return None

def agendar(paciente: str, profissional: str, data: str, hora: int, duracao: int) -> bool:
    """Registra uma nova consulta clínica no sistema caso haja disponibilidade.

    Realiza a validação defensiva dos parâmetros de data, duração e expediente
    comercial antes de verificar eventuais colisões na agenda do profissional.

    Args:
        paciente (str): Nome do paciente atendido.
        profissional (str): Nome completo ou identificador do profissional de saúde.
        data (str): Data da consulta no formato estrito AAAA-MM-DD.
        hora (int): Hora inteira de início do atendimento (entre 8 e 17).
        duracao (int): Duração da consulta em minutos (15 a 120, múltipla de 15).

    Returns:
        bool: True se a consulta foi agendada com sucesso; False caso o horário
            já esteja ocupado para o profissional indicado.

    Raises:
        DataInvalidaError: Se a data estiver fora do formato AAAA-MM-DD ou não
            existir no calendário.
        DuracaoInvalidaError: Se a duração for inferior a 15, superior a 120 ou
            não for múltipla de 15 minutos.
        HorarioInvalidoError: Se o início estiver fora de 8h às 17h ou se o término
            ultrapassar o horário de encerramento da clínica (18h).
    """
    
    validar_formato_data(data)
    validar_duracao(duracao)
    validar_expediente(hora, duracao)
    
    if not validar_horario(hora, duracao) or horario_ocupado(profissional, data, hora):
        return False
    agendamentos.append(Agendamento(paciente, profissional, data, hora, duracao))
    return True

def adicionar_consulta(paciente: str, profissional: str, data: str, hora: int, duracao: int):
    """Ponto de entrada de interface para solicitação de agendamento de consulta.

    Executa o processo de validação e inserção na agenda, exibindo a respectiva
    mensagem de confirmação ou indisponibilidade no terminal.

    Args:
        paciente (str): Nome do paciente atendido.
        profissional (str): Profissional de saúde responsável.
        data (str): Data pretendida (AAAA-MM-DD).
        hora (int): Hora de início pretendida.
        duracao (int): Duração em minutos.

    Returns:
        None: Não possui retorno de dados; exibe o status diretamente na saída padrão.

    Raises:
        DataInvalidaError: Se a data fornecida for malformada.
        DuracaoInvalidaError: Se a duração violar as regras de faixa e incremento.
        HorarioInvalidoError: Se os horários ultrapassarem o expediente da clínica.
    """

    if agendar(paciente, profissional, data, hora, duracao):
        print("Atendimento marcado para", paciente)
    else:
        print("Horario ocupado")

def remarcar_consulta(paciente: str, data: str, hora: int, nova_data: str, nova_hora: int):
    """Altera a data e a hora de um agendamento existente.

    Localiza a consulta original, valida as novas entradas de horário/expediente
    e efetiva a alteração caso não ocorra sobreposição com a agenda do profissional.

    Args:
        paciente (str): Nome do paciente cadastrado.
        data (str): Data atual da consulta (AAAA-MM-DD).
        hora (int): Hora atual do agendamento.
        nova_data (str): Nova data solicitada (AAAA-MM-DD).
        nova_hora (int): Nova hora pretendida.

    Returns:
        None: Não possui retorno de dados; imprime o status na saída padrão.

    Raises:
        DataInvalidaError: Se `data` ou `nova_data` violarem o formato AAAA-MM-DD.
        AgendamentoNaoEncontradoError: Se não existir agendamento prévio com os dados originais.
        HorarioInvalidoError: Se a nova hora projetar término além do expediente comercial.
    """ 
    validar_formato_data(data)
    validar_formato_data(nova_data)
    agendamento = buscar_agendamento(paciente, data, hora)

    if agendamento is None:
        raise AgendamentoNaoEncontradoError(
            f"Agendamento não encontrado para o paciente '{paciente}' em {data} às {hora}h."
        )

    validar_expediente(nova_hora, agendamento.duracao)

    if agendamento:
        if not horario_ocupado(agendamento.profissional, nova_data, nova_hora):
            agendamento.data = nova_data
            agendamento.hora = nova_hora
            print("Remarcado")
        else:
            print("Horario ocupado")

def lista(dia):
    """Exibe na saída padrão os atendimentos marcados para determinada data.

    Percorre os agendamentos registrados e imprime ordenadamente as informações
    de hora, paciente, profissional e status para o dia consultado.

    Args:
        dia (str): Data de filtragem no formato AAAA-MM-DD.

    Returns:
        None: Envia as linhas correspondentes diretamente ao terminal.
    """
    for agendamento in agendamentos:
        if agendamento.data == dia:
            print(agendamento.hora, agendamento.paciente, agendamento.profissional, agendamento.status)


adicionar_consulta("Ana", "Dr. Silva", "2026-10-05", 9, 30)
adicionar_consulta("Bruno", "Dr. Silva", "2026-10-05", 9, 30)
adicionar_consulta("Carla", "Dra. Souza", "2026-10-05", 14, 60)
remarcar_consulta("Ana", "2026-10-05", 9, "2026-10-06", 10)
lista("2026-10-05")