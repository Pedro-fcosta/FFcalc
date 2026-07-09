from math import exp


CONSTANTE_GASES = 8.314462618


def celsius_para_kelvin(temperatura_c):
    return temperatura_c + 273.15


def calcular_temperatura_homologa(temperatura_operacao_c, temperatura_fusao_c):
    temperatura_operacao_k = celsius_para_kelvin(temperatura_operacao_c)
    temperatura_fusao_k = celsius_para_kelvin(temperatura_fusao_c)

    if temperatura_operacao_k <= 0:
        raise ValueError("A temperatura de operacao deve ser maior que -273,15 C.")

    if temperatura_fusao_k <= 0:
        raise ValueError("A temperatura de fusao deve ser maior que -273,15 C.")

    return temperatura_operacao_k / temperatura_fusao_k


def calcular_taxa_norton_arrhenius(
    tensao_mpa,
    temperatura_operacao_c,
    coeficiente_a,
    expoente_n,
    energia_ativacao_kj_mol,
):
    if tensao_mpa <= 0:
        raise ValueError("A tensao aplicada deve ser maior que zero.")

    if coeficiente_a <= 0:
        raise ValueError("O coeficiente A deve ser maior que zero.")

    if expoente_n <= 0:
        raise ValueError("O expoente n deve ser maior que zero.")

    if energia_ativacao_kj_mol < 0:
        raise ValueError("A energia de ativacao nao pode ser negativa.")

    temperatura_k = celsius_para_kelvin(temperatura_operacao_c)

    if temperatura_k <= 0:
        raise ValueError("A temperatura de operacao deve ser maior que -273,15 C.")

    energia_ativacao_j_mol = energia_ativacao_kj_mol * 1000
    fator_termico = exp(
        -energia_ativacao_j_mol / (CONSTANTE_GASES * temperatura_k)
    )

    return coeficiente_a * (tensao_mpa ** expoente_n) * fator_termico


def estimar_deformacao(taxa_fluencia_h, tempo_operacao_h):
    if tempo_operacao_h < 0:
        raise ValueError("O tempo de operacao nao pode ser negativo.")

    return taxa_fluencia_h * tempo_operacao_h


def estimar_tempo_para_deformacao(taxa_fluencia_h, deformacao_limite):
    if deformacao_limite <= 0:
        raise ValueError("A deformacao limite deve ser maior que zero.")

    if taxa_fluencia_h <= 0:
        return float("inf")

    return deformacao_limite / taxa_fluencia_h
