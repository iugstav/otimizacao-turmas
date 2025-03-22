import importlib
import os
import sys
import pandas as pd

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

materias = importlib.import_module("materias", package="otim-turmas")


def remove_older(sub):
    result = []
    for x in sub:
        result.append(x) if x in materias.nomes_materias else ()

    return result


# nomes dos arquivos de entrada e saída
input = "output.csv"
output = "../professores.csv"
if os.getcwd().find("sigaa") == -1:
    input = "sigaa/" + input
    output = output[3:]

df = pd.read_csv(input)
df = df[df["Professores"] != "A DEFIN"]

# juntando as duas disciplinas de analise numerica em uma
i = df[df["Matéria"] == "- ANÁLISE NUMÉRICA I - TEORICA"].index
df.drop(i, inplace=True)
i = df[df["Matéria"] == "- ANÁLISE NUMÉRICA I - PRATICA"].index
df.loc[i, "Matéria"] = "ANÁLISE NUMÉRICA I"

i = df[df["Professores"] == "ADILIO JORGE MARQUES"].index
df.drop(index=i, inplace=True)

# dataframe de matérias agrupadas por professor
grouped = (
    df.groupby("Professores")["Matéria"].apply(lambda x: list(set(x))).reset_index()
)

# removendo as matérias anteriores ao quinto período
grouped["Matéria"] = grouped["Matéria"].apply(remove_older)
grouped = grouped[grouped["Matéria"].apply(lambda x: len(x) > 0)]
grouped.to_csv(output, index=False)
