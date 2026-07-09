def calcular_parametros_ciclo(sigma_max, sigma_min):
    """
    Calcula os principais parâmetros de um ciclo de tensão.

    sigma_max: tensão máxima em MPa
    sigma_min: tensão mínima em MPa
    """

    sigma_a = (sigma_max - sigma_min) / 2
    sigma_m = (sigma_max + sigma_min) / 2

    if sigma_max != 0:
        razao_r = sigma_min / sigma_max
    else:
        razao_r = None

    return {
        "sigma_max": sigma_max,
        "sigma_min": sigma_min,
        "sigma_a": sigma_a,
        "sigma_m": sigma_m,
        "razao_r": razao_r
    }


def fator_seguranca_goodman(sigma_a, sigma_m, limite_fadiga, limite_resistencia):
    """
    Calcula o fator de segurança pelo critério de Goodman modificado.

    Fórmula simplificada:
    sigma_a/Se + sigma_m/Sut = 1/n
    """

    sigma_m_corrigida = max(sigma_m, 0)

    indice = (sigma_a / limite_fadiga) + (sigma_m_corrigida / limite_resistencia)

    if indice == 0:
        return float("inf")

    return 1 / indice


def fator_seguranca_soderberg(sigma_a, sigma_m, limite_fadiga, limite_escoamento):
    """
    Calcula o fator de segurança pelo critério de Soderberg.

    Fórmula simplificada:
    sigma_a/Se + sigma_m/Sy = 1/n
    """

    sigma_m_corrigida = max(sigma_m, 0)

    indice = (sigma_a / limite_fadiga) + (sigma_m_corrigida / limite_escoamento)

    if indice == 0:
        return float("inf")

    return 1 / indice


def fator_seguranca_gerber(sigma_a, sigma_m, limite_fadiga, limite_resistencia):
    """
    Calcula o fator de segurança pelo critério parabólico de Gerber.

    Modelo simplificado:
    sigma_a/Se + (sigma_m/Sut)^2 = 1/n
    """

    sigma_m_corrigida = max(sigma_m, 0)

    indice = (sigma_a / limite_fadiga) + (sigma_m_corrigida / limite_resistencia) ** 2

    if indice == 0:
        return float("inf")

    return 1 / indice