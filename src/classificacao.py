def classificar_fator_seguranca(fator_seguranca):
    """
    Classifica o resultado preliminar com base no fator de seguranca.
    """

    if fator_seguranca >= 2:
        return "Baixo risco preliminar"

    if 1 <= fator_seguranca < 2:
        return "Atencao: condicao proxima do limite"

    return "Critico: falha por fadiga pode ocorrer"
