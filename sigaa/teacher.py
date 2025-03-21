import os
import pandas as pd


def remove_older(sub):
    result = []
    for x in sub:
        result.append(x) if x in nomes_materias else ()

    return result


nomes_materias = [
    "ESPAÇOS MÉTRICOS",
    "MÉTODOS DE ELEMENTOS FINITOS",
    "REDE DE COMPUTADORES",
    "PROGRAMAÇÃO INTEIRA",
    "FISICA II",
    "COMPUTACAO GRAFICA",
    "BANCO DE DADOS",
    "ANALISE I",
    "INTRODUÇÃO DA TEORIA DOS GRAFOS",
    "FÍSICA I",
    "INTRODUÇÃO ÀS EQUAÇÕES DIFERENCIAIS PARCIAIS",
    "ANÁLISE DE ALGORITMOS",
    "ESTRUTURA DE DADOS",
    "ANÁLISE NUMÉRICA",
    "PROGRAMAÇÃO NÃO-LINEAR",
    "INTRODUÇÃO À MATEMÁTICA COMBINATÓRIA",
    "CALCULO IV",
    "ÁLGEBRA LINEAR COMPUTACIONAL",
]

input = "output.csv"
output = "../professores.csv"
if os.getcwd().find("sigaa") == -1:
    input = "sigaa/" + input
    output = output[3:]

df = pd.read_csv(input)
df = df[df["Professores"] != "A DEFIN"]
grouped = (
    df.groupby("Professores")["Matéria"].apply(lambda x: list(set(x))).reset_index()
)
grouped["Matéria"] = grouped["Matéria"].apply(remove_older)
grouped = grouped[grouped["Matéria"].apply(lambda x: len(x) > 0)]
grouped.to_csv(output)
