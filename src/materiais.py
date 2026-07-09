from pathlib import Path

import pandas as pd


CAMINHO_MATERIAIS = Path(__file__).resolve().parent.parent / "data" / "materiais.csv"


def carregar_materiais():
    """
    Carrega o banco de materiais a partir de um arquivo CSV separado por ponto e virgula.
    """

    try:
        materiais = pd.read_csv(
            CAMINHO_MATERIAIS,
            sep=";",
            encoding="utf-8-sig",
        )
    except UnicodeDecodeError:
        materiais = pd.read_csv(
            CAMINHO_MATERIAIS,
            sep=";",
            encoding="latin1",
        )
    except FileNotFoundError:
        print("Erro: arquivo materiais.csv nao encontrado.")
        return None

    materiais.columns = (
        materiais.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    colunas_obrigatorias = [
        "id",
        "material",
        "limite_fadiga_mpa",
        "limite_resistencia_mpa",
        "limite_escoamento_mpa",
    ]

    colunas_faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in materiais.columns
    ]

    if colunas_faltantes:
        print("Erro: o arquivo materiais.csv esta com colunas faltando.")
        print(f"Colunas encontradas: {list(materiais.columns)}")
        print(f"Colunas faltantes: {colunas_faltantes}")
        return None

    for coluna in [
        "id",
        "limite_fadiga_mpa",
        "limite_resistencia_mpa",
        "limite_escoamento_mpa",
    ]:
        materiais[coluna] = pd.to_numeric(materiais[coluna], errors="coerce")

    if materiais[colunas_obrigatorias].isnull().any().any():
        print("Erro: o arquivo materiais.csv possui valores invalidos ou vazios.")
        return None

    materiais["id"] = materiais["id"].astype(int)

    return materiais


def listar_materiais(materiais):
    """
    Exibe os materiais cadastrados.
    """

    print("\nMateriais disponiveis:")
    print("-" * 60)

    for _, material in materiais.iterrows():
        print(f"{int(material['id'])} - {material['material']}")

    print("-" * 60)


def selecionar_material(materiais):
    """
    Permite ao usuario selecionar um material pelo ID.
    """

    while True:
        try:
            id_material = int(input("Digite o ID do material: "))
        except ValueError:
            print("Entrada invalida. Digite apenas o numero do ID.")
            continue

        material = materiais.loc[materiais["id"] == id_material]

        if material.empty:
            print("ID nao encontrado. Escolha um dos materiais listados.")
            continue

        return material.iloc[0]
