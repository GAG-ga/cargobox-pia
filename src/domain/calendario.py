"""Días hábiles (lunes a viernes). Los festivos quedan como mejora documentada."""
from datetime import date, timedelta


def es_habil(dia: date) -> bool:
    return dia.weekday() < 5


def sumar_dias_habiles(inicio: date, dias: int) -> date:
    actual = inicio
    restantes = dias
    while restantes > 0:
        actual += timedelta(days=1)
        if es_habil(actual):
            restantes -= 1
    return actual


def dias_habiles_transcurridos(inicio: date, fin: date) -> int:
    """Días hábiles después de `inicio` y hasta `fin` (incluido)."""
    total = 0
    actual = inicio
    while actual < fin:
        actual += timedelta(days=1)
        if es_habil(actual):
            total += 1
    return total
