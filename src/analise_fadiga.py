from src.classificacao import classificar_fator_seguranca
from src.fadiga import (
    calcular_parametros_ciclo,
    fator_seguranca_gerber,
    fator_seguranca_goodman,
    fator_seguranca_soderberg,
)


def calcular_analise_fadiga(sigma_max, sigma_min, material):
    if sigma_max < sigma_min:
        raise ValueError("A tensao maxima deve ser maior ou igual a tensao minima.")

    limite_fadiga = float(material["limite_fadiga_mpa"])
    limite_resistencia = float(material["limite_resistencia_mpa"])
    limite_escoamento = float(material["limite_escoamento_mpa"])

    ciclo = calcular_parametros_ciclo(sigma_max, sigma_min)

    fatores = {
        "Goodman": fator_seguranca_goodman(
            ciclo["sigma_a"],
            ciclo["sigma_m"],
            limite_fadiga,
            limite_resistencia,
        ),
        "Soderberg": fator_seguranca_soderberg(
            ciclo["sigma_a"],
            ciclo["sigma_m"],
            limite_fadiga,
            limite_escoamento,
        ),
        "Gerber": fator_seguranca_gerber(
            ciclo["sigma_a"],
            ciclo["sigma_m"],
            limite_fadiga,
            limite_resistencia,
        ),
    }

    if hasattr(material, "to_dict"):
        material = material.to_dict()

    return {
        "material": material,
        "limites": {
            "limite_fadiga_mpa": limite_fadiga,
            "limite_resistencia_mpa": limite_resistencia,
            "limite_escoamento_mpa": limite_escoamento,
        },
        "ciclo": ciclo,
        "fatores": fatores,
        "classificacoes": {
            criterio: classificar_fator_seguranca(fator)
            for criterio, fator in fatores.items()
        },
    }


def formatar_fator(valor):
    if valor == float("inf"):
        return "infinito"

    return f"{valor:.2f}"
