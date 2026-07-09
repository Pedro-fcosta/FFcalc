from pathlib import Path

import pandas as pd


CAMINHO_MATERIAIS = Path("data") / "materiais.csv"


def carregar_materiais():
    """
    Carrega o banco de materiais a partir de um arquivo CSV separado por ponto e vírgula.
    """

    try:
        materiais = pd.read_csv(
            CAMINHO_MATERIAIS,
            sep=";",
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:
        materiais = pd.read_csv(
            CAMINHO_MATERIAIS,
            sep=";",
            encoding="latin1"
        )

    except FileNotFoundError:
        print("Erro: arquivo materiais.csv não encontrado.")
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
        "limite_escoamento_mpa"
    ]

    colunas_faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in materiais.columns
    ]

    if colunas_faltantes:
        print("Erro: o arquivo materiais.csv está com colunas faltando.")
        print(f"Colunas encontradas: {list(materiais.columns)}")
        print(f"Colunas faltantes: {colunas_faltantes}")
        return None

    return materiais


def listar_materiais(materiais):
    """
    Exibe os materiais cadastrados.
    """

    print("\nMateriais disponíveis:")
    print("-" * 60)

    for _, material in materiais.iterrows():
        print(f"{int(material['id'])} - {material['material']}")

    print("-" * 60)


def selecionar_material(materiais):
    """
    Permite ao usuário selecionar um material pelo ID.
    """

    while True:
        try:
            materiais = pd.read_csv(
                CAMINHO_MATERIAIS,
                sep=";",
                encoding="utf-8-sig"
            )

        except UnicodeDecodeError:
            materiais = pd.read_csv(
                CAMINHO_MATERIAIS,
                sep=";",
                encoding="cp1252"
            )

        except ValueError:
            print("Entrada inválida. Digite apenas o número do ID.")