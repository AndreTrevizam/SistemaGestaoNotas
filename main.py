from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator, Field
from typing import Dict, Optional
import json
import os
from statistics import mean, median, stdev

app = FastAPI()

# Estrutura de dados
alunos = []

class Aluno(BaseModel):
    id: int
    nome: str
    notas: Optional[Dict[str, float]] = Field(default_factory=dict)

    @field_validator("notas")
    def validar_notas(cls, v):
        for disciplina, nota in v.items():
            if not (0 <= nota <= 10):
                raise ValueError(f"A nota para {disciplina} deve estar entre 0 e 10.")
            v[disciplina] = round(nota, 1)
        return v

# Função para salvar dados em arquivo
def salvar_dados():
    with open("alunos.json", "w") as file:
        json.dump(alunos, file, indent=4)

# Função para carregar dados de arquivo
def carregar_dados():
    if os.path.exists("alunos.json"):
        with open("alunos.json", "r") as file:
            global alunos
            alunos = json.load(file)

# Função para adicionar aluno
def adicionar_aluno(aluno: Aluno):
    alunos.append(aluno.__dict__)
    salvar_dados()

# Função para remover alunos sem notas
def remover_alunos_sem_notas():
    global alunos
    alunos = [aluno for aluno in alunos if aluno.get('notas')]
    salvar_dados()
    return {"mensagem": "Alunos sem notas removidos com sucesso"}

# Função para recuperar notas de um aluno específico pelo ID
def recuperar_notas_aluno(id: int):
    for aluno in alunos:
        if aluno['id'] == id:
            return aluno['notas']
    raise HTTPException(status_code=404, detail="Aluno não encontrado")

# Função para recuperar notas de uma disciplina específica em ordem crescente
def recuperar_notas_disciplina(disciplina: str):
    notas_disciplina = []
    for aluno in alunos:
        if disciplina in aluno['notas']:
            notas_disciplina.append({'nome': aluno['nome'], 'nota': aluno['notas'][disciplina]})
    notas_disciplina.sort(key=lambda x: x['nota'])
    return notas_disciplina

# Função para calcular estatísticas de uma disciplina
def calcular_estatisticas(disciplina: str):
    notas = [aluno['notas'][disciplina] for aluno in alunos if disciplina in aluno['notas']]
    if not notas:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada ou sem notas registradas")
    
    estatisticas = {
        "media": round(mean(notas), 2),
        "mediana": round(median(notas), 2),
        "desvio_padrao": round(stdev(notas), 2) if len(notas) > 1 else 0.0
    }
    return estatisticas

# Função para identificar alunos com desempenho abaixo de 6,0 em uma disciplina específica
def alunos_desempenho_baixo(disciplina: str):
    alunos_baixo_desempenho = []
    for aluno in alunos:
        if disciplina in aluno['notas'] and aluno['notas'][disciplina] < 6.0:
            alunos_baixo_desempenho.append({'nome': aluno['nome'], 'nota': aluno['notas'][disciplina]})
    return alunos_baixo_desempenho

# Endpoint para adicionar aluno e suas notas
@app.post("/alunos")
def criar_aluno(aluno: Aluno):
    adicionar_aluno(aluno)
    return {"mensagem": "Aluno adicionado com sucesso"}

# Endpoint para recuperar notas de um aluno específico pelo ID
@app.get("/alunos/{id}")
def obter_notas_aluno(id: int):
    return recuperar_notas_aluno(id)

# Endpoint para recuperar notas de uma disciplina específica em ordem crescente
@app.get("/disciplinas/{disciplina}/notas")
def obter_notas_disciplina(disciplina: str):
    return recuperar_notas_disciplina(disciplina)

# Endpoint para recuperar estatísticas de uma disciplina específica
@app.get("/disciplinas/{disciplina}/estatisticas")
def obter_estatisticas_disciplina(disciplina: str):
    return calcular_estatisticas(disciplina)

# Endpoint para recuperar alunos com desempenho abaixo de 6,0 em uma disciplina específica
@app.get("/disciplinas/{disciplina}/desempenho_baixo")
def obter_alunos_desempenho_baixo(disciplina: str):
    return alunos_desempenho_baixo(disciplina)

# Endpoint para remover alunos sem notas
@app.delete("/alunos/sem_notas")
def remover_alunos_sem_notas_endpoint():
    return remover_alunos_sem_notas()