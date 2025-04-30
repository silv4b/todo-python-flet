from datetime import datetime


def get_current_datetime() -> str:
    """Retorna a data e hora atual em formato ISO `%Y-%m-%d %H:%M:%S`"""
    data_atual_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data_atual_iso


def datetime_iso4ptbr(date: str) -> str:
    """Converte a data e hora atual em formato ISO para o padrao pt_BR `%d/%m/%Y %H:%M:%S`"""
    data_em_ptbr = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime(
        "%d/%m/%Y %H:%M:%S"
    )
    return data_em_ptbr
