from ast import literal_eval
from itertools import chain
from collections import defaultdict
import csv
import os
import random
import pandas as pd
import networkx as nx
from pulp import LpProblem, LpVariable, LpMaximize, lpSum, LpBinary, value
from materias import nomes_materias, periodos

# Parâmetros
num_alunos = 40
num_materias = len(nomes_materias)
num_optativas = 5  # Número de matérias optativas disponíveis
capacidade_max = 10  # Máximo de alunos por matéria
horarios_disponiveis = ["18h-20h", "20h-22h"]  # Dois horários possíveis por dia
dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex"]  # Dias disponíveis
total_materias = num_materias + num_optativas

# uso de dataframes
# dataframe de alunos dummy
alunos_set = pd.read_csv("alunos.csv")
alunos = alunos_set["Aluno"].tolist()
alunos_periodos = alunos_set["Período"].tolist()
interesses = (
    alunos_set["Preferência"]
    .apply(lambda x: x.split(", ") if isinstance(x, str) else [])
    .tolist()
)
periodos_materias = (
    alunos_set["Periodos_Matérias"]
    .apply(lambda x: x.split(", ") if isinstance(x, str) else [])
    .tolist()
)
alunos_preferências = list(set(materia for lista in interesses for materia in lista))

# dataframe de professores e suas materias lecionadas em semestres anteriores
professores_set = pd.read_csv("professores.csv")
professores_set["Matéria"] = professores_set["Matéria"].apply(
    lambda x: literal_eval(x) if "[" in x else x
)
num_professores = len(professores_set)
materias_dadas = {
    row["Professores"]: row["Matéria"] for _, row in professores_set.iterrows()
}

ids = {p: i for i, p in enumerate(materias_dadas.keys())}

# Lista com nomes das matérias
# Criar dicionário associando cada matéria ao seu período
periodos_materias = {}
for periodo, materias in periodos.items():
    for materia in materias:
        periodos_materias[materia] = periodo

professores_por_materia = {}
for prof, materias in materias_dadas.items():
    for m in nomes_materias:
        if m in materias:
            if m not in professores_por_materia:
                professores_por_materia[m] = []
            professores_por_materia[m].append(prof)

materias_por_professor = {p: [] for p in list(materias_dadas.keys())}
materias_ocupadas = {m: False for m in nomes_materias}
for materia, professores in professores_por_materia.items():
    if len(professores) == 1:
        materias_por_professor[professores[0]].append(materia)
        materias_ocupadas[materia] = True
        continue

    prof_escolhido = professores[random.randint(0, len(professores) - 1)]
    if len(materias_por_professor[prof_escolhido]) >= 1:
        alternativa = ""
        for prof, m in materias_dadas.items():
            if prof == prof_escolhido:
                continue
            elif materia not in m:
                continue

            if len(materias_por_professor[prof]) >= 2:
                continue

            alternativa = prof
            break

        if len(alternativa) == 0:
            materias_por_professor[prof_escolhido].append(materia)
            materias_ocupadas[materia] = True
    else:
        materias_por_professor[prof_escolhido].append(materia)
        materias_ocupadas[materia] = True


remaining = [m for m in materias_ocupadas if materias_ocupadas[m] == False]
for materia in remaining:
    for professor, materias in materias_dadas.items():
        if materia in materias:
            materias_ocupadas[materia] = True
            materias_por_professor[professor].append(materia)
            break

# TODO: adicionar optativas
professores_ids = []
for professor, materias in materias_por_professor.items():
    for m in materias:
        professores_ids.append(ids[professor])

# Criar o modelo de otimização
model = LpProblem("Alocacao_Alunos", LpMaximize)

# Variáveis de decisão
x = [
    [LpVariable(f"x_{i}_{j}", 0, 1, LpBinary) for j in range(num_materias)]
    for i in range(num_alunos)
]

optativas = [
    [LpVariable(f"opt_{i}_{j}", 0, 1, LpBinary) for j in range(num_optativas)]
    for i in range(num_alunos)
]

horarios = [
    [
        [
            LpVariable(f"horario_{j}_{d}_{h}", 0, 1, LpBinary)
            for h in range(len(horarios_disponiveis))
        ]
        for d in range(len(dias_semana))
    ]
    for j in range(num_materias + num_optativas)
]

# Preferências aleatórias dos alunos
preferencias = {
    i: random.sample(range(num_materias), random.randint(5, 7))
    for i in range(num_alunos)
}

# Restrições de alocação
for i in range(num_alunos):
    model += (
        lpSum(x[i][j] for j in preferencias[i])
        + lpSum(optativas[i][j] for j in range(num_optativas))
        >= 5,
        f"Minimo_Materias_Aluno_{i}",
    )
    model += (
        lpSum(x[i][j] for j in preferencias[i])
        + lpSum(optativas[i][j] for j in range(num_optativas))
        <= 7,
        f"Maximo_Materias_Aluno_{i}",
    )
    model += (
        lpSum(optativas[i][j] for j in range(num_optativas)) <= 2,
        f"Max_Optativas_Aluno_{i}",
    )

for j in range(num_materias):
    model += (
        lpSum(x[i][j] for i in range(num_alunos)) <= capacidade_max,
        f"Capacidade_Materia_{j}",
    )

for j in range(num_materias + num_optativas):
    model += (
        lpSum(
            horarios[j][d][h]
            for d in range(len(dias_semana))
            for h in range(len(horarios_disponiveis))
        )
        == 2,
        f"Dois_Horarios_Por_Materia_{j}",
    )

for j in range(num_materias + num_optativas):
    for d in range(len(dias_semana)):
        model += (
            lpSum(horarios[j][d][h] for h in range(len(horarios_disponiveis))) <= 1,
            f"Uma_Vez_Por_Dia_{j}_{d}",
        )

# TODO: adicionar optativas na conta
for p in range(num_professores):
    materias_do_professor = [j for j in range(num_materias) if professores_ids[j] == p]
    for d in range(len(dias_semana)):
        for h in range(len(horarios_disponiveis)):
            model += (
                lpSum(horarios[j][d][h] for j in materias_do_professor) <= 1,
                f"Professor {p} não pode dar aula em dois lugares {d} {h}",
            )

# 🔹 Restrição 2: Prioridade para alunos do período correto
for i in range(num_alunos):
    print(f"aluno {i}")
    for materia in interesses[i]:
        if materia in ids:
            j = ids[materia]
            prioridade = (
                2 if str(periodos[i]) in periodos_materias[i] else 1
            )  # Alunos do período certo têm peso maior
            print(f"prioridade: {prioridade} na matéria {materia}")
            model += x[i][j] * prioridade, f"Prioridade_Aluno_{i}_Materia_{j}"
    print()

# Função objetivo
model += (
    lpSum(x[i][j] for i in range(num_alunos) for j in preferencias[i]),
    "Max_Inscricoes",
)

# Resolver o modelo
model.solve()

# Criar pasta para salvar os CSVs
pasta = "resultados"
os.makedirs(pasta, exist_ok=True)

# Salvar alocação de matérias com seus períodos
with open(
    os.path.join(pasta, "materias_periodos.csv"), mode="w", newline="", encoding="utf-8"
) as file:
    writer = csv.writer(file)
    writer.writerow(["Matéria", "Período"])
    for materia in nomes_materias:
        writer.writerow([materia, periodos_materias.get(materia, "Desconhecido")])

# Salvar horários das matérias
with open(
    os.path.join(pasta, "horarios_materias.csv"), mode="w", newline="", encoding="utf-8"
) as file:
    writer = csv.writer(file)
    writer.writerow(["Matéria", "Período", "Dia", "Horário"])

    for j in range(num_materias):
        materia_nome = nomes_materias[j]
        periodo = periodos_materias.get(materia_nome, "Desconhecido")

        for d in range(len(dias_semana)):
            for h in range(len(horarios_disponiveis)):
                if value(horarios[j][d][h]) == 1:
                    writer.writerow(
                        [materia_nome, periodo, dias_semana[d], horarios_disponiveis[h]]
                    )

# Salvar alocação de alunos
with open(
    os.path.join(pasta, "Alocacao_alunos.csv"), mode="w", newline="", encoding="utf-8"
) as file:
    writer = csv.writer(file)
    writer.writerow(["Aluno", "Periodo", "Materias Alocadas"])
    for i in range(num_alunos):
        materias_alocadas = [
            alunos_preferências[j] for j in range(num_materias) if value(x[i][j]) == 1
        ]
        print(materias_alocadas)
        writer.writerow([alunos[i], alunos_periodos[i], ", ".join(materias_alocadas)])

print(f"CSVs salvos na pasta: {pasta}")
