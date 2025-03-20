import os
import pandas as pd

input = "output.csv"
output = "../professores.csv"
if os.getcwd().find("sigaa") == -1:
    input = "sigaa/" + input
    output = output[3:]

df = pd.read_csv(input)
df = df[df["Professores"] != "A DEFIN"]
grouped = df.groupby("Professores")["Matéria"].apply(lambda x: list(set(x))).reset_index()

grouped.to_csv(output)
