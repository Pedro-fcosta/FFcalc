import argparse

from src.analise_fadiga import calcular_analise_fadiga, formatar_fator
from src.analise_fluencia import (
    calcular_analise_fluencia,
    formatar_cientifico,
    obter_preset_fluencia,
)
from src.materiais import carregar_materiais, listar_materiais, selecionar_material


def ler_float(mensagem):
    while True:
        entrada = input(mensagem).strip().replace(",", ".")

        try:
            return float(entrada)
        except ValueError:
            print("Entrada invalida. Digite um numero, por exemplo: 250 ou 250,5.")


def ler_float_padrao(mensagem, valor_padrao):
    entrada = input(f"{mensagem} [{valor_padrao}]: ").strip().replace(",", ".")

    if not entrada:
        return float(valor_padrao)

    try:
        return float(entrada)
    except ValueError:
        print("Entrada invalida. Usando valor padrao.")
        return float(valor_padrao)


def main_cli_fadiga():
    print("=" * 60)
    print("FFCalc - Modulo de Fadiga")
    print("=" * 60)

    sigma_max = ler_float("\nDigite a tensao maxima sigma_max [MPa]: ")
    sigma_min = ler_float("Digite a tensao minima sigma_min [MPa]: ")

    materiais = carregar_materiais()

    if materiais is None:
        return 1

    listar_materiais(materiais)
    material = selecionar_material(materiais)

    try:
        resultado = calcular_analise_fadiga(sigma_max, sigma_min, material)
    except ValueError as erro:
        print(f"Erro: {erro}")
        return 1

    ciclo = resultado["ciclo"]
    limites = resultado["limites"]
    fatores = resultado["fatores"]
    classificacoes = resultado["classificacoes"]

    print("\nMaterial selecionado:")
    print(f"Material: {resultado['material']['material']}")
    print(f"Limite de fadiga Se: {limites['limite_fadiga_mpa']:.2f} MPa")
    print(f"Limite de resistencia Sut: {limites['limite_resistencia_mpa']:.2f} MPa")
    print(f"Limite de escoamento Sy: {limites['limite_escoamento_mpa']:.2f} MPa")

    print("\n" + "=" * 60)
    print("RESULTADOS - FADIGA")
    print("=" * 60)

    print(f"Tensao maxima sigma_max: {ciclo['sigma_max']:.2f} MPa")
    print(f"Tensao minima sigma_min: {ciclo['sigma_min']:.2f} MPa")
    print(f"Tensao alternada sigma_a: {ciclo['sigma_a']:.2f} MPa")
    print(f"Tensao media sigma_m: {ciclo['sigma_m']:.2f} MPa")

    if ciclo["razao_r"] is not None:
        print(f"Razao de carregamento R: {ciclo['razao_r']:.3f}")
    else:
        print("Razao de carregamento R: indefinida")

    print("\nFatores de seguranca:")

    for criterio, fator in fatores.items():
        print(f"{criterio}: {formatar_fator(fator)}")

    print("\nClassificacao preliminar:")

    for criterio, classificacao in classificacoes.items():
        print(f"{criterio}: {classificacao}")

    print_observacao()
    return 0


def main_cli_fluencia():
    print("=" * 60)
    print("FFCalc - Modulo de Fluencia")
    print("=" * 60)

    materiais = carregar_materiais()

    if materiais is None:
        return 1

    listar_materiais(materiais)
    material = selecionar_material(materiais)
    preset = obter_preset_fluencia(material["material"])

    print("\nEntradas de fluencia:")
    tensao_mpa = ler_float_padrao("Tensao aplicada sigma [MPa]", 120)
    temperatura_operacao_c = ler_float_padrao("Temperatura de operacao [C]", 550)
    temperatura_fusao_c = ler_float_padrao(
        "Temperatura de fusao [C]",
        preset["temperatura_fusao_c"],
    )
    tempo_operacao_h = ler_float_padrao("Tempo de operacao [h]", 10000)
    coeficiente_a = ler_float_padrao("Coeficiente Norton A", preset["coeficiente_a"])
    expoente_n = ler_float_padrao("Expoente Norton n", preset["expoente_n"])
    energia_ativacao_kj_mol = ler_float_padrao(
        "Energia de ativacao Q [kJ/mol]",
        preset["energia_ativacao_kj_mol"],
    )
    deformacao_limite_percentual = ler_float_padrao("Deformacao limite [%]", 1)

    try:
        resultado = calcular_analise_fluencia(
            tensao_mpa=tensao_mpa,
            temperatura_operacao_c=temperatura_operacao_c,
            temperatura_fusao_c=temperatura_fusao_c,
            tempo_operacao_h=tempo_operacao_h,
            coeficiente_a=coeficiente_a,
            expoente_n=expoente_n,
            energia_ativacao_kj_mol=energia_ativacao_kj_mol,
            deformacao_limite_percentual=deformacao_limite_percentual,
            material=material,
        )
    except ValueError as erro:
        print(f"Erro: {erro}")
        return 1

    valores = resultado["resultados"]

    print("\n" + "=" * 60)
    print("RESULTADOS - FLUENCIA")
    print("=" * 60)
    print(f"Temperatura homologa T/Tf: {valores['temperatura_homologa']:.3f}")
    print(f"Taxa de fluencia estimada: {formatar_cientifico(valores['taxa_fluencia_h'])} 1/h")
    print(f"Deformacao acumulada: {valores['deformacao_percentual']:.4f}%")
    print(f"Tempo ate limite: {formatar_horas(valores['tempo_limite_h'])}")
    print(f"Consumo do limite: {valores['consumo_limite_percentual']:.2f}%")

    print("\nClassificacao preliminar:")

    for criterio, dados in resultado["criterios"].items():
        print(f"{criterio}: {dados['classificacao']}")

    print_observacao()
    return 0


def formatar_horas(horas):
    if horas == float("inf"):
        return "infinito"

    if horas >= 8760:
        return f"{horas / 8760:.2f} anos"

    return f"{horas:.0f} h"


def print_observacao():
    print("\nObservacao:")
    print(
        "Esta analise e preliminar e educacional. "
        "Nao substitui normas, ensaios ou avaliacao profissional."
    )


def main_gui():
    try:
        from src.gui import FFCalcApp
    except ModuleNotFoundError as erro:
        if erro.name == "customtkinter":
            print(
                "Erro: customtkinter nao esta instalado. "
                "Instale as dependencias com: pip install -r requirements.txt"
            )
            return 1

        raise

    app = FFCalcApp()
    app.mainloop()
    return 0


def main():
    parser = argparse.ArgumentParser(description="FFCalc")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Executa a versao de terminal em vez da interface grafica.",
    )
    parser.add_argument(
        "--modulo",
        choices=["fadiga", "fluencia"],
        default="fadiga",
        help="Modulo usado no modo terminal.",
    )
    args = parser.parse_args()

    if not args.cli:
        return main_gui()

    if args.modulo == "fluencia":
        return main_cli_fluencia()

    return main_cli_fadiga()


if __name__ == "__main__":
    raise SystemExit(main())
