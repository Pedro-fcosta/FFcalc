from src.fluencia import (
    calcular_taxa_norton_arrhenius,
    calcular_temperatura_homologa,
    estimar_deformacao,
    estimar_tempo_para_deformacao,
)


PRESETS_FLUENCIA = {
    "aco": {
        "temperatura_fusao_c": 1450.0,
        "coeficiente_a": 1e-2,
        "expoente_n": 4.0,
        "energia_ativacao_kj_mol": 220.0,
    },
    "aluminio": {
        "temperatura_fusao_c": 635.0,
        "coeficiente_a": 2e-4,
        "expoente_n": 4.5,
        "energia_ativacao_kj_mol": 142.0,
    },
    "inoxidavel": {
        "temperatura_fusao_c": 1400.0,
        "coeficiente_a": 5e-3,
        "expoente_n": 4.2,
        "energia_ativacao_kj_mol": 240.0,
    },
    "padrao": {
        "temperatura_fusao_c": 1450.0,
        "coeficiente_a": 1e-2,
        "expoente_n": 4.0,
        "energia_ativacao_kj_mol": 220.0,
    },
}


def obter_preset_fluencia(nome_material):
    nome = str(nome_material).lower()

    if "aluminio" in nome:
        return PRESETS_FLUENCIA["aluminio"].copy()

    if "inox" in nome:
        return PRESETS_FLUENCIA["inoxidavel"].copy()

    if "aco" in nome:
        return PRESETS_FLUENCIA["aco"].copy()

    return PRESETS_FLUENCIA["padrao"].copy()


def calcular_analise_fluencia(
    tensao_mpa,
    temperatura_operacao_c,
    temperatura_fusao_c,
    tempo_operacao_h,
    coeficiente_a,
    expoente_n,
    energia_ativacao_kj_mol,
    deformacao_limite_percentual,
    material=None,
):
    if temperatura_operacao_c >= temperatura_fusao_c:
        raise ValueError("A temperatura de operacao deve ser menor que a temperatura de fusao.")

    if deformacao_limite_percentual <= 0:
        raise ValueError("A deformacao limite deve ser maior que zero.")

    temperatura_homologa = calcular_temperatura_homologa(
        temperatura_operacao_c,
        temperatura_fusao_c,
    )
    taxa_fluencia_h = calcular_taxa_norton_arrhenius(
        tensao_mpa,
        temperatura_operacao_c,
        coeficiente_a,
        expoente_n,
        energia_ativacao_kj_mol,
    )
    deformacao = estimar_deformacao(taxa_fluencia_h, tempo_operacao_h)
    deformacao_limite = deformacao_limite_percentual / 100
    tempo_limite_h = estimar_tempo_para_deformacao(
        taxa_fluencia_h,
        deformacao_limite,
    )
    consumo_limite_percentual = (deformacao / deformacao_limite) * 100

    if hasattr(material, "to_dict"):
        material = material.to_dict()

    criterios = {
        "Temperatura homologa": {
            "valor": temperatura_homologa,
            "classificacao": classificar_temperatura_homologa(temperatura_homologa),
        },
        "Taxa estimada": {
            "valor": taxa_fluencia_h,
            "classificacao": classificar_taxa_fluencia(taxa_fluencia_h),
        },
        "Consumo do limite": {
            "valor": consumo_limite_percentual,
            "classificacao": classificar_consumo(consumo_limite_percentual),
        },
    }

    return {
        "material": material,
        "entradas": {
            "tensao_mpa": tensao_mpa,
            "temperatura_operacao_c": temperatura_operacao_c,
            "temperatura_fusao_c": temperatura_fusao_c,
            "tempo_operacao_h": tempo_operacao_h,
            "coeficiente_a": coeficiente_a,
            "expoente_n": expoente_n,
            "energia_ativacao_kj_mol": energia_ativacao_kj_mol,
            "deformacao_limite_percentual": deformacao_limite_percentual,
        },
        "resultados": {
            "temperatura_homologa": temperatura_homologa,
            "taxa_fluencia_h": taxa_fluencia_h,
            "deformacao": deformacao,
            "deformacao_percentual": deformacao * 100,
            "tempo_limite_h": tempo_limite_h,
            "consumo_limite_percentual": consumo_limite_percentual,
        },
        "criterios": criterios,
    }


def classificar_temperatura_homologa(temperatura_homologa):
    if temperatura_homologa < 0.30:
        return "Baixa tendencia preliminar a fluencia"

    if temperatura_homologa < 0.50:
        return "Atencao: faixa com potencial de fluencia"

    return "Critico: fluencia pode ser mecanismo relevante"


def classificar_taxa_fluencia(taxa_fluencia_h):
    if taxa_fluencia_h < 1e-10:
        return "Taxa estimada muito baixa"

    if taxa_fluencia_h < 1e-7:
        return "Taxa estimada moderada"

    return "Taxa estimada elevada"


def classificar_consumo(consumo_limite_percentual):
    if consumo_limite_percentual < 50:
        return "Baixo consumo preliminar do limite"

    if consumo_limite_percentual < 100:
        return "Atencao: consumo proximo do limite"

    return "Critico: limite de deformacao excedido"


def formatar_cientifico(valor):
    return f"{valor:.3e}"


def formatar_percentual(valor):
    return f"{valor:.3f}%"
