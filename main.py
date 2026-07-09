from src.fadiga import (
    calcular_parametros_ciclo,
    fator_seguranca_goodman,
    fator_seguranca_soderberg,
    fator_seguranca_gerber
)

from src.classificacao import classificar_fator_seguranca

from src.materiais import (
    carregar_materiais,
    listar_materiais,
    selecionar_material
)


def main():
    print("=" * 60)
    print("FFCalc — Sistema de Análise de Fadiga e Fluência")
    print("=" * 60)

    print("\nMódulo inicial: Análise preliminar de fadiga\n")

    sigma_max = float(input("Digite a tensão máxima σmax [MPa]: "))
    sigma_min = float(input("Digite a tensão mínima σmin [MPa]: "))


    materiais = carregar_materiais()

    if materiais is None:
        return

    listar_materiais(materiais)
    material = selecionar_material(materiais)

    limite_fadiga = material["limite_fadiga_mpa"]
    limite_resistencia = material["limite_resistencia_mpa"]
    limite_escoamento = material["limite_escoamento_mpa"]

    print("\nMaterial selecionado:")
    print(f"Material: {material['material']}")
    print(f"Limite de fadiga Se: {limite_fadiga:.2f} MPa")
    print(f"Limite de resistência Sut: {limite_resistencia:.2f} MPa")
    print(f"Limite de escoamento Sy: {limite_escoamento:.2f} MPa")


    ciclo = calcular_parametros_ciclo(sigma_max, sigma_min)

    fs_goodman = fator_seguranca_goodman(
        ciclo["sigma_a"],
        ciclo["sigma_m"],
        limite_fadiga,
        limite_resistencia
    )

    fs_soderberg = fator_seguranca_soderberg(
        ciclo["sigma_a"],
        ciclo["sigma_m"],
        limite_fadiga,
        limite_escoamento
    )

    fs_gerber = fator_seguranca_gerber(
        ciclo["sigma_a"],
        ciclo["sigma_m"],
        limite_fadiga,
        limite_resistencia
    )

    print("\n" + "=" * 60)
    print("RESULTADOS")
    print("=" * 60)

    print(f"Tensão máxima σmax: {ciclo['sigma_max']:.2f} MPa")
    print(f"Tensão mínima σmin: {ciclo['sigma_min']:.2f} MPa")
    print(f"Tensão alternada σa: {ciclo['sigma_a']:.2f} MPa")
    print(f"Tensão média σm: {ciclo['sigma_m']:.2f} MPa")

    if ciclo["razao_r"] is not None:
        print(f"Razão de carregamento R: {ciclo['razao_r']:.3f}")
    else:
        print("Razão de carregamento R: indefinida")

    print("\nFatores de segurança:")

    print(f"Goodman: {fs_goodman:.2f}")
    print(f"Soderberg: {fs_soderberg:.2f}")
    print(f"Gerber: {fs_gerber:.2f}")

    print("\nClassificação preliminar:")

    print(f"Goodman: {classificar_fator_seguranca(fs_goodman)}")
    print(f"Soderberg: {classificar_fator_seguranca(fs_soderberg)}")
    print(f"Gerber: {classificar_fator_seguranca(fs_gerber)}")

    print("\nObservação:")
    print("Esta análise é preliminar e educacional. Não substitui normas, ensaios ou avaliação profissional.")


if __name__ == "__main__":
    main()