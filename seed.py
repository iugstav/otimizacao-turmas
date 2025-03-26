import csv
from pathlib import Path
import time
import random
from materias import nomes_materias, periodos

random.seed(time.time())
# queria usar bash, mas tem gente que usa windows

prerequisitos = {
    "ANALISE I": ["CALCULO IV"],
    "ANALISE II": ["ANÁLISE I"],
    "ESPAÇOS MÉTRICOS": ["ANALISE I"],
    "PROGRAMAÇÃO NÃO-LINEAR": [],
    "INTRODUÇÃO À MATEMÁTICA COMBINATÓRIA": [],
    "INTRODUÇÃO DA TEORIA DOS GRAFOS": ["INTRODUÇÃO À MATEMÁTICA COMBINATÓRIA"],
    "PROGRAMAÇÃO INTEIRA": ["PROGRAMAÇÃO NÃO-LINEAR"],
    "FISICA II": ["FÍSICA I"],
    "ANÁLISE NUMÉRICA I": [],
    "INTRODUÇÃO ÀS EQUAÇÕES DIFERENCIAIS PARCIAIS": [],
    "COMPUTAÇÃO GRÁFICA": ["ESTRUTURA DE DADOS"],
    "ANÁLISE DE ALGORITMOS": ["ESTRUTURA DE DADOS"],
    "BANCO DE DADOS": ["ESTRUTURA DE DADOS"],
    "REDE DE COMPUTADORES": ["BANCO DE DADOS", "ESTRUTURA DE DADOS"],
    "MÉTODOS DE ELEMENTOS FINITOS": [
        "INTRODUÇÃO ÀS EQUAÇÕES DIFERENCIAIS PARCIAIS",
        "FISICA I",
    ],
}

periodos_materias = {}
for periodo, materias in periodos.items():
    for materia in materias:
        periodos_materias[materia] = periodo


def set_semester(materias: list[str]):
    result = []
    for m in materias:
        result.append(str(periodos_materias[m]))

    return ", ".join(result)


def find_schedule_clash(materias: list[str]):
    conflitos = []
    for materia in materias:
        # nem todas as matérias tem pré-requisitos a partir do 5 periodo
        if materia not in prerequisitos:
            continue
        for pre in prerequisitos[materia]:
            if pre in materias:
                print(f"adicionando a tupla ({materia}, {pre}) aos conflitos")
                conflitos.append((materia, pre))

    return conflitos


num_alunos = 40
alunos = []
for i in range(num_alunos):
    materias = [
        nomes_materias[i]
        for i in random.sample(range(0, len(nomes_materias)), random.randint(3, 5))
    ]

    print(f"Aluno {i+1} | Matérias: {materias}")
    conflitos = find_schedule_clash(materias)

    if len(conflitos) > 0:
        if len(conflitos) >= 2:
            # sorteia de novo as matérias, pois a maioria deu conflito
            print("sorteando de novo as matérias")
            materias = [
                nomes_materias[i]
                for i in random.sample(
                    range(0, len(nomes_materias)), random.randint(3, 5)
                )
            ]
            conflitos = find_schedule_clash(materias)

        print("\nRESOLUÇÃO DE CONFLITOS\n")
        possiveis_materias = set(prerequisitos.keys()) - set(materias)
        for materia, prereq in conflitos:
            print(materias, materia)
            for possivel_materia in possiveis_materias:
                if all(pre in materias for pre in prerequisitos[possivel_materia]):
                    materias.remove(materia)
                    materias.append(possivel_materia)
                    print(
                        f"substituindo {materia} por {possivel_materia} devido a conflito de pré-requisito"
                    )
                    i += 1
                    break
            i += 1

    aluno = {
        "nome": f"Aluno {i+1}",
        "periodo": random.randint(5, 8),
        "preferência": ", ".join(materias),
        "períodos_matérias": set_semester(materias),
    }
    alunos.append(aluno)

csv_titles = ["Aluno", "Período", "Preferência", "Periodos_Matérias"]

dir_path = Path.cwd() / "data/"
if not dir_path.exists():
    if dir_path.stem.find("sigaa"):
        dir_path = dir_path.parents[1] / "data/"
        dir_path.mkdir(exist_ok=True)
    else:
        dir_path.mkdir(exist_ok=True)

with open(dir_path / "alunos.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(csv_titles)
    for a in alunos:
        writer.writerow(a.values())

print("finished seeding students table")
