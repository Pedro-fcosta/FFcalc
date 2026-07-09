def classificar_fator_seguranca(fator_seguranca):
    """
    Classifica o resultado preliminar com base no fator de segurança.
    """

    if fator_seguranca >= 2:
        return "Baixo risco preliminar"

    elif 1 <= fator_seguranca < 2:
        return "Atenção: condição próxima do limite"

    else:
        return "Crítico: falha por fadiga pode ocorrer"