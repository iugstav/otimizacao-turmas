import csv
import time
import random
from materias import nomes_materias, periodos

random.seed(time.time())
# queria usar bash, mas tem gente que usa windows

periodos_materias = {}
for periodo, materias in periodos.items():
    for materia in materias:
        periodos_materias[materia] = periodo


def set_semester(materias: list[str]):
    result = []
    for m in materias:
        result.append(str(periodos_materias[m]))

    return ", ".join(result)


num_alunos = 40
alunos = []
for i in range(num_alunos):
    materias = [
        nomes_materias[i]
        for i in random.sample(range(0, len(nomes_materias)), random.randint(5, 7))
    ]
    aluno = {
        "nome": f"Aluno {i+1}",
        "periodo": random.randint(5, 8),
        "preferência": ", ".join(materias),
        "períodos_matérias": set_semester(materias),
    }
    alunos.append(aluno)

csv_titles = ["Aluno", "Período", "Preferência", "Periodos_Matérias"]

with open("alunos.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(csv_titles)
    for a in alunos:
        writer.writerow(a.values())

print("finished seeding students table")
