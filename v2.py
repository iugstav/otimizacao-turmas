from pulp import LpProblem, LpVariable, LpMaximize, lpSum, LpBinary, value
import random

# Parâmetros
num_alunos = 40
num_materias = 20
num_optativas = 5  # Número de matérias optativas disponíveis
capacidade_max = 40  # Máximo de alunos por matéria
num_professores = 11
horarios_disponiveis = ["18h-20h", "20h-22h"]  # Dois horários possíveis por dia
dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex"]  # Dias disponíveis

total_materias = num_materias + num_optativas
professores_por_materia = []

for p in range(num_professores):
    professores_por_materia.append(p)

remaining = total_materias - num_professores
for _ in range(remaining):
    contagem = {p: professores_por_materia.count(p) for p in range(num_professores)}
    prof_validos = [p for p, count in contagem.items() if count < 3]
    prof_escolhido = random.choice(prof_validos)
    professores_por_materia.append(prof_escolhido)

random.shuffle(professores_por_materia)

# Criar o modelo de otimização
model = LpProblem("Alocacao_Alunos", LpMaximize)

# Variáveis de decisão: x[i][j] = 1 se aluno i estiver na matéria j, 0 caso contrário
x = [
    [LpVariable(f"x_{i}_{j}", 0, 1, LpBinary) for j in range(num_materias)]
    for i in range(num_alunos)
]

# Variáveis para matérias optativas
optativas = [
    [LpVariable(f"opt_{i}_{j}", 0, 1, LpBinary) for j in range(num_optativas)]
    for i in range(num_alunos)
]

# Variáveis para alocar matérias nos horários disponíveis (cada matéria ocorre em 2 horários por semana)
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

# Preferências dos alunos (aleatórias para simulação)
preferencias = {
    i: random.sample(range(num_materias), random.randint(5, 7))
    for i in range(num_alunos)
}

# 🔹 Restrição 1: Cada aluno deve ter entre 5 e 7 matérias (incluindo até 2 optativas)
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

# 🔹 Restrição 2: Capacidade máxima por matéria
for j in range(num_materias):
    model += (
        lpSum(x[i][j] for i in range(num_alunos)) <= capacidade_max,
        f"Capacidade_Materia_{j}",
    )

# 🔹 Restrição 3: Cada matéria deve ter **exatamente 2 horários semanais** em dias diferentes
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

# 🔹 Restrição 4: Cada matéria só pode ser alocada uma vez por dia
for j in range(num_materias + num_optativas):
    for d in range(len(dias_semana)):
        model += (
            lpSum(horarios[j][d][h] for h in range(len(horarios_disponiveis))) <= 1,
            f"Uma_Vez_Por_Dia_{j}_{d}",
        )

# 🔹 Nova Restrição 5: Professores não podem ter conflitos de horário
for p in range(num_professores):
    materias_do_professor = [
        j
        for j in range(num_materias + num_optativas)
        if professores_por_materia[j] == p
    ]
    for d in range(len(dias_semana)):
        for h in range(len(horarios_disponiveis)):
            model += (
                lpSum(horarios[j][d][h] for j in materias_do_professor) <= 1,
                f"Professor {p} não pode dar aula em dois lugares {d} {h}",
            )


# 🔹 Função Objetivo: Maximizar alocação considerando preferências dos alunos
model += (
    lpSum(x[i][j] for i in range(num_alunos) for j in preferencias[i]),
    "Max_Inscricoes",
)

# Resolver o modelo
model.solve()

# 🔹 Exibir resultados
alunos_por_materia: dict[str, list[str]] = dict()
print("\nAlocação dos alunos:")
for i in range(num_alunos):
    materias = [f"Matéria {j + 1}" for j in preferencias[i] if value(x[i][j]) == 1]
    optativas_escolhidas = [
        f"Optativa {j+1}" for j in range(num_optativas) if value(optativas[i][j]) == 1
    ]

    # Se o aluno tiver menos de 5 matérias, adicionar optativas
    while len(materias) + len(optativas_escolhidas) < 5:
        optativa = f"Optativa {random.randint(1, num_optativas)}"
        if optativa not in optativas_escolhidas:
            optativas_escolhidas.append(optativa)

    for materia in (materias + optativas_escolhidas):
        if materia not in alunos_por_materia:
            alunos_por_materia[materia] = [f"Aluno {i+1}"]
        else:
            alunos_por_materia[materia].append(f"Aluno {i+1}")

    print(f"Aluno {i+1}: Matérias {materias + optativas_escolhidas}")

print("\nAlunos por matéria:")
for materias, alunos in alunos_por_materia.items():
    print(f"{materias}")
    for a in alunos:
        print(a)
    print()

# 🔹 Exibir horários das matérias
print("\nHorários das matérias:")
for j in range(num_materias + num_optativas):
    horarios_alocados = []
    for d in range(len(dias_semana)):
        for h in range(len(horarios_disponiveis)):
            if value(horarios[j][d][h]) == 1:
                horarios_alocados.append(f"{dias_semana[d]} {horarios_disponiveis[h]}")

    print(f"Matéria {j+1}: {horarios_alocados}")

# 🔹 Estatísticas finais
total_inscricoes = sum(
    value(x[i][j]) for i in range(num_alunos) for j in preferencias[i]
)
print(f"\nTotal de inscrições realizadas: {int(total_inscricoes)}")

print("\nDistribuição de matérias por professor:")
for p in range(num_professores):
    total = professores_por_materia.count(p)
    print(f"Professor {p+1}: {total} matérias")
