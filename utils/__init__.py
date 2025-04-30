from .date_utils import get_current_datetime
from .date_utils import datetime_iso4ptbr

# Exporta as funções para serem acessíveis via `utils.função`

__all__ = ["get_current_datetime", "datetime_iso4ptbr"]

"""
Em Python, `__all__` é uma variável especial usada
    para definir quais símbolos (funções, classes, variáveis)
    serão exportados quando alguém importar um módulo usando
   `from modulo import *.`

Ela é opcional, mas muito útil para controlar a
    interface pública do seu módulo ou pacote,
    evitando que funções internas ou auxiliares
    sejam acessadas acidentalmente.
"""
