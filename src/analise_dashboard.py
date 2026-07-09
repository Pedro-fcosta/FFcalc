import math

import pandas as pd

from src.analise_fadiga import calcular_analise_fadiga
from src.analise_fluencia import (
    calcular_analise_fluencia,
    obter_preset_fluencia,
)


COLUNAS_FLUENCIA_OPCIONAIS = {
    "temperatura_fusao_c": "temperatura_fusao_c",
    "norton_a": "coeficiente_a",
    "norton_n": "expoente_n",
    "energia_ativacao_kj_mol": "energia_ativacao_kj_mol",
}


def analisar_dashboard(
    sigma_max,
    sigma_min,
    sigma_creep,
    temperatura_operacao_c,
    tempo_h,
    deformacao_limite_pct,
    materiais,
):
    if materiais is None or materiais.empty:
        raise ValueError("Nenhum material disponivel para comparar.")

    if sigma_max < sigma_min:
        raise ValueError("A tensao maxima deve ser maior ou igual a tensao minima.")

    if sigma_creep <= 0:
        raise ValueError("A tensao de fluencia deve ser maior que zero.")

    if tempo_h < 0:
        raise ValueError("O tempo de operacao nao pode ser negativo.")

    if deformacao_limite_pct <= 0:
        raise ValueError("A deformacao limite deve ser maior que zero.")

    resultados = []

    for _, material in materiais.iterrows():
        resultado_fadiga = calcular_analise_fadiga(sigma_max, sigma_min, material)
        ciclo = resultado_fadiga["ciclo"]
        fatores = resultado_fadiga["fatores"]
        criterio_critico, menor_fs = min(fatores.items(), key=lambda item: item[1])

        propriedades_fluencia = obter_propriedades_fluencia(material)
        resultado_fluencia = _calcular_fluencia_material(
            material=material,
            sigma_creep=sigma_creep,
            temperatura_operacao_c=temperatura_operacao_c,
            tempo_h=tempo_h,
            deformacao_limite_pct=deformacao_limite_pct,
            propriedades=propriedades_fluencia,
        )

        consumo_pct = resultado_fluencia["consumo_fluencia_pct"]
        temperatura_homologa = resultado_fluencia["temperatura_homologa"]
        score_total, scores = calcular_score_dashboard(
            menor_fs,
            consumo_pct,
            temperatura_homologa,
        )

        resultados.append(
            {
                "id": int(material["id"]),
                "material": material["material"],
                "sigma_a": ciclo["sigma_a"],
                "sigma_m": ciclo["sigma_m"],
                "razao_r": ciclo["razao_r"],
                "fs_goodman": fatores["Goodman"],
                "fs_soderberg": fatores["Soderberg"],
                "fs_gerber": fatores["Gerber"],
                "criterio_critico_fadiga": criterio_critico,
                "menor_fs_fadiga": menor_fs,
                "temperatura_homologa": temperatura_homologa,
                "taxa_fluencia_h": resultado_fluencia["taxa_fluencia_h"],
                "deformacao_percentual": resultado_fluencia["deformacao_percentual"],
                "consumo_fluencia_pct": consumo_pct,
                "classificacao_fadiga": classificar_fadiga_dashboard(menor_fs),
                "classificacao_fluencia": classificar_fluencia_dashboard(
                    consumo_pct,
                    temperatura_homologa,
                ),
                "score_fadiga": scores["score_fadiga"],
                "score_fluencia": scores["score_fluencia"],
                "score_temperatura": scores["score_temperatura"],
                "score_total": score_total,
                "classificacao_geral": classificar_score_dashboard(score_total),
            }
        )

    ranking = pd.DataFrame(resultados)
    ranking = ranking.sort_values(
        by=["score_total", "menor_fs_fadiga", "consumo_fluencia_pct"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    ranking.insert(0, "ranking", ranking.index + 1)

    return ranking


def obter_propriedades_fluencia(material):
    propriedades = obter_preset_fluencia(material["material"])

    for coluna_csv, chave in COLUNAS_FLUENCIA_OPCIONAIS.items():
        if coluna_csv in material.index and _valor_valido(material[coluna_csv]):
            propriedades[chave] = float(material[coluna_csv])

    return propriedades


def calcular_score_dashboard(menor_fs_fadiga, consumo_fluencia_pct, temperatura_homologa):
    if math.isinf(menor_fs_fadiga):
        score_fadiga = 1.0
    else:
        score_fadiga = _limitar(menor_fs_fadiga / 2, 0, 1)

    if math.isfinite(consumo_fluencia_pct):
        consumo_decimal = consumo_fluencia_pct / 100
        score_fluencia = _limitar(1 - consumo_decimal, 0, 1)
    else:
        score_fluencia = 0.0

    if math.isfinite(temperatura_homologa):
        penalizacao_temperatura = max(0, temperatura_homologa - 0.4)
        score_temperatura = _limitar(1 - penalizacao_temperatura, 0, 1)
    else:
        score_temperatura = 0.0

    score_total = (
        0.5 * score_fadiga
        + 0.3 * score_fluencia
        + 0.2 * score_temperatura
    )

    return score_total, {
        "score_fadiga": score_fadiga,
        "score_fluencia": score_fluencia,
        "score_temperatura": score_temperatura,
    }


def classificar_score_dashboard(score_total):
    if score_total >= 0.75:
        return "Mais adequado preliminarmente"

    if score_total >= 0.50:
        return "Atencao / avaliar com cautela"

    return "Pouco adequado preliminarmente"


def classificar_fadiga_dashboard(menor_fs):
    if menor_fs >= 2:
        return "Baixo risco preliminar por fadiga"

    if menor_fs >= 1:
        return "Atencao: margem de fadiga limitada"

    return "Critico: fator de fadiga abaixo de 1"


def classificar_fluencia_dashboard(consumo_pct, temperatura_homologa):
    if not math.isfinite(consumo_pct) or temperatura_homologa >= 1:
        return "Critico: condicao de fluencia invalida ou severa"

    if consumo_pct >= 100:
        return "Critico: limite de deformacao excedido"

    if consumo_pct >= 50 or temperatura_homologa >= 0.5:
        return "Atencao: avaliar fluencia com cautela"

    return "Baixo consumo preliminar por fluencia"


def _calcular_fluencia_material(
    material,
    sigma_creep,
    temperatura_operacao_c,
    tempo_h,
    deformacao_limite_pct,
    propriedades,
):
    try:
        resultado = calcular_analise_fluencia(
            tensao_mpa=sigma_creep,
            temperatura_operacao_c=temperatura_operacao_c,
            temperatura_fusao_c=propriedades["temperatura_fusao_c"],
            tempo_operacao_h=tempo_h,
            coeficiente_a=propriedades["coeficiente_a"],
            expoente_n=propriedades["expoente_n"],
            energia_ativacao_kj_mol=propriedades["energia_ativacao_kj_mol"],
            deformacao_limite_percentual=deformacao_limite_pct,
            material=material,
        )
        valores = resultado["resultados"]

        return {
            "temperatura_homologa": valores["temperatura_homologa"],
            "taxa_fluencia_h": valores["taxa_fluencia_h"],
            "deformacao_percentual": valores["deformacao_percentual"],
            "consumo_fluencia_pct": valores["consumo_limite_percentual"],
        }
    except ValueError:
        temperatura_fusao_k = propriedades["temperatura_fusao_c"] + 273.15
        temperatura_operacao_k = temperatura_operacao_c + 273.15
        temperatura_homologa = (
            temperatura_operacao_k / temperatura_fusao_k
            if temperatura_fusao_k > 0
            else float("inf")
        )

        return {
            "temperatura_homologa": temperatura_homologa,
            "taxa_fluencia_h": float("inf"),
            "deformacao_percentual": float("inf"),
            "consumo_fluencia_pct": float("inf"),
        }


def _valor_valido(valor):
    if valor is None:
        return False

    try:
        return math.isfinite(float(valor))
    except (TypeError, ValueError):
        return False


def _limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))
