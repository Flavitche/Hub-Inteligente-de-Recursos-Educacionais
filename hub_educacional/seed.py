"""
Script de seed — popula o banco com dados de exemplo.

Como rodar:
    cd hub_educacional
    python seed.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal, engine
from app.models.resource import Resource, Base

# Cria as tabelas se não existirem
Base.metadata.create_all(bind=engine)

RECURSOS = [
    {
        "title": "Python para Iniciantes — Curso Completo",
        "description": (
            "Você quer aprender programação e não sabe por onde começar? Python é a linguagem "
            "ideal para quem está dando os primeiros passos. Neste curso você vai aprender desde "
            "variáveis e estruturas de controle até funções, listas e dicionários. O conteúdo é "
            "voltado para iniciantes absolutos e cada conceito é explicado com exemplos práticos "
            "do dia a dia. Ao final, você vai conseguir criar seus primeiros programas e entender "
            "a lógica por trás do código."
        ),
        "type": "Video",
        "url": "https://www.youtube.com/watch?v=exemplo-python",
        "tags": ["python", "iniciante", "programação", "lógica"],
    },
    {
        "title": "Estruturas de Dados e Algoritmos em Python",
        "description": (
            "Chegou a hora de levar seu Python para o próximo nível. Aqui você vai entender "
            "como funcionam listas ligadas, pilhas, filas, árvores e grafos — e quando usar "
            "cada uma delas. O conteúdo é voltado para quem já tem uma base em Python e quer "
            "se preparar para entrevistas técnicas e projetos mais complexos. Cada estrutura "
            "vem acompanhada de implementação do zero e análise de complexidade."
        ),
        "type": "PDF",
        "url": "https://exemplo.com/estruturas-dados.pdf",
        "tags": ["algoritmos", "estruturas de dados", "python", "intermediário"],
    },
    {
        "title": "Documentação Oficial do FastAPI",
        "description": (
            "A documentação oficial do FastAPI é um dos melhores recursos para aprender o "
            "framework. Ela cobre desde a instalação e primeiros endpoints até autenticação, "
            "dependências, testes e deploy. Tem exemplos interativos e explicações claras "
            "sobre como o FastAPI usa Python moderno com type hints. Ideal para quem quer "
            "construir APIs profissionais e rápidas com Python."
        ),
        "type": "Link",
        "url": "https://fastapi.tiangolo.com",
        "tags": ["fastapi", "python", "api", "backend", "documentação"],
    },
    {
        "title": "SQL para Análise de Dados — Do Zero ao Avançado",
        "description": (
            "SQL é uma das habilidades mais pedidas no mercado de dados. Neste curso você "
            "começa do absoluto zero — aprendendo SELECT, WHERE e JOIN — e vai até consultas "
            "avançadas com window functions, CTEs e otimização de queries. O conteúdo é "
            "voltado para quem quer trabalhar com análise de dados, engenharia de dados ou "
            "simplesmente entender melhor os bancos de dados que usa no dia a dia."
        ),
        "type": "Video",
        "url": "https://www.youtube.com/watch?v=exemplo-sql",
        "tags": ["sql", "banco de dados", "análise de dados", "iniciante"],
    },
    {
        "title": "React — Guia Completo com Hooks e Context API",
        "description": (
            "Aprenda React do jeito certo, com os padrões modernos que o mercado usa hoje. "
            "Neste material você vai entender como funcionam os hooks principais — useState, "
            "useEffect, useCallback e useMemo — e como gerenciar estado global com Context API. "
            "O conteúdo é voltado para quem já conhece JavaScript e quer construir interfaces "
            "modernas e escaláveis. Cada conceito vem acompanhado de um projeto prático."
        ),
        "type": "PDF",
        "url": "https://exemplo.com/react-guia.pdf",
        "tags": ["react", "javascript", "frontend", "hooks", "intermediário"],
    },
    {
        "title": "Docker — Containerização para Desenvolvedores",
        "description": (
            "Se você já se perguntou por que o código funciona na sua máquina mas não no "
            "servidor, Docker é a resposta. Neste curso você vai entender o que são containers, "
            "como criar Dockerfiles, trabalhar com volumes e redes, e orquestrar múltiplos "
            "serviços com Docker Compose. O conteúdo é voltado para desenvolvedores que querem "
            "profissionalizar o fluxo de desenvolvimento e deploy das suas aplicações."
        ),
        "type": "Video",
        "url": "https://www.youtube.com/watch?v=exemplo-docker",
        "tags": ["docker", "devops", "containers", "deploy", "intermediário"],
    },
    {
        "title": "Git e GitHub — O Guia de Sobrevivência",
        "description": (
            "Dominar o controle de versão é essencial para qualquer desenvolvedor. "
            "Neste guia prático, você aprenderá desde os comandos básicos como add, commit "
            "e push, até fluxos de trabalho colaborativos com Pull Requests e resolução "
            "de conflitos. O conteúdo foca no uso real do Git no dia a dia das empresas, "
            "ajudando você a manter seu histórico de código organizado e seguro."
        ),
        "type": "Video",
        "url": "https://www.youtube.com/watch?v=exemplo-git",
        "tags": ["git", "github", "versão", "colaboração", "iniciante"],
    },
    {
        "title": "Clean Code — Princípios de Código Limpo",
        "description": (
            "Não basta que o código funcione; ele precisa ser fácil de ler e manter. "
            "Este material resume os principais conceitos do livro Clean Code de Robert C. Martin. "
            "Aprenda a escolher bons nomes para variáveis, criar funções pequenas e com "
            "responsabilidade única, além de técnicas para reduzir o acoplamento no seu projeto. "
            "Indispensável para quem busca maturidade profissional no desenvolvimento de software."
        ),
        "type": "PDF",
        "url": "https://exemplo.com/clean-code-resumo.pdf",
        "tags": ["clean code", "boas práticas", "arquitetura", "intermediário"],
    },
    {
        "title": "TypeScript — O Guia Definitivo para Desenvolvedores JS",
        "description": (
            "TypeScript adiciona tipagem estática ao JavaScript, prevenindo erros comuns "
            "antes mesmo de rodar o código. Este recurso cobre desde os tipos básicos e "
            "interfaces até Generics e Decorators. Ideal para quem trabalha com React, "
            "Node.js ou Angular e quer aumentar a produtividade e a segurança das suas "
            "aplicações em larga escala."
        ),
        "type": "Link",
        "url": "https://www.typescriptlang.org/docs/",
        "tags": ["typescript", "javascript", "frontend", "backend", "documentação"],
    },
    {
        "title": "Introdução a Testes Automatizados com Pytest",
        "description": (
            "Dormir tranquilo sabendo que seu código funciona é possível com testes. "
            "Aprenda a usar o Pytest, o framework de testes mais popular do ecossistema Python. "
            "O conteúdo ensina como criar testes unitários, usar fixtures para reaproveitar "
            "código de configuração e como rodar seus testes de forma eficiente no terminal. "
            "Passo fundamental para implementar CI/CD no seu projeto."
        ),
        "type": "Video",
        "url": "https://www.youtube.com/watch?v=exemplo-pytest",
        "tags": ["python", "testes", "pytest", "qualidade", "intermediário"],
    },
    {
        "title": "Arquitetura de Microserviços — Conceitos e Desafios",
        "description": (
            "Entenda quando e por que quebrar um monólito em microserviços. Este material "
            "explora a comunicação entre serviços via REST e mensageria (RabbitMQ/Kafka), "
            "bancos de dados descentralizados e os desafios de manter a consistência e a "
            "observabilidade. Voltado para desenvolvedores seniores e arquitetos que "
            "precisam projetar sistemas altamente escaláveis e distribuídos."
        ),
        "type": "PDF",
        "url": "https://exemplo.com/microservicos-arquitetura.pdf",
        "tags": ["microserviços", "arquitetura", "backend", "escalabilidade", "avançado"],
    },
    {
        "title": "PostgreSQL — Otimização de Performance",
        "description": (
            "Seu banco de dados está lento? Aprenda técnicas avançadas para otimizar o "
            "PostgreSQL. O guia aborda criação de índices eficientes, análise de planos "
            "de execução com EXPLAIN ANALYZE, configuração de memória e técnicas de "
            "particionamento de tabelas. Ideal para DBAs e desenvolvedores backend que "
            "lidam com grandes volumes de dados."
        ),
        "type": "Link",
        "url": "https://www.postgresql.org/docs/current/performance-tips.html",
        "tags": ["postgresql", "sql", "performance", "banco de dados", "avançado"],
    },
]


def seed():
    db = SessionLocal()

    try:
        # Verifica se já tem dados
        total = db.query(Resource).count()
        if total > 0:
            print(f"⚠️  O banco já tem {total} recurso(s). Pulando seed para não duplicar.")
            print("   Se quiser recriar, delete o arquivo hub_educacional.db e rode novamente.")
            return

        print("🌱 Iniciando seed do banco de dados...\n")

        for dados in RECURSOS:
            recurso = Resource(
                title=dados["title"],
                description=dados["description"],
                type=dados["type"],
                url=dados["url"],
                tags=dados["tags"],
            )
            db.add(recurso)
            print(f"   ✅ {dados['type']:<6} — {dados['title']}")

        db.commit()
        print(f"\n🎉 Seed concluído! {len(RECURSOS)} recursos criados com sucesso.")
        print("   Acesse http://localhost:8000/docs para ver os dados.")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro durante o seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()