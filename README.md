☁️ IsCoolGPT - Assistente Inteligente de Estudos em Cloud

O IsCoolGPT é um assistente educacional inteligente projetado para auxiliar estudantes na disciplina de Cloud Computing. O projeto utiliza uma arquitetura moderna baseada em microsserviços, containerização e um pipeline robusto de DevOps na AWS.

🏗️ Arquitetura e Fluxo de DevOps

O projeto segue o Princípio do Menor Privilégio e utiliza Infraestrutura como Código indireta via definições de tarefa ECS.

graph LR
    A[Desenvolvedor] -->|Push| B[GitHub Repo]
    B -->|Trigger| C{GitHub Actions}
    C -->|1. Test & Lint| D[PyTest]
    C -->|2. Espelhamento| E[AWS CodeCommit]
    C -->|3. Build Docker| F[AWS ECR]
    F -->|Deploy| G[AWS ECS Fargate]
    G -->|Executa| H[IsCoolGPT Container]
    H -->|Consome| I[Google Gemini AI]
    User[Estudante] -->|HTTP/8000| H


Componentes da Infraestrutura

GitHub: Repositório principal para versionamento e gestão de Pull Requests.

GitHub Actions: Orquestrador de CI/CD que executa testes, build e deploy.

AWS CodeCommit: Espelho (Mirror) do repositório para compliance e backup dentro da AWS.

AWS ECR: Registro privado para armazenamento seguro das imagens Docker.

AWS ECS (Fargate): Orquestrador de containers Serverless para alta disponibilidade e escalabilidade.

Google Gemini 2.5 Flash: Motor de IA generativa para respostas rápidas e precisas.

🚀 Como Rodar Localmente

Pré-requisitos

Docker instalado

Python 3.10+

Chave de API do Google AI Studio

Passo a Passo

Clone o repositório:

git clone [https://github.com/SEU_USUARIO/isCoolGPT.git](https://github.com/SEU_USUARIO/isCoolGPT.git)
cd isCoolGPT


Configure a variável de ambiente:
Crie um arquivo .env na raiz (não commite este arquivo!):

GOOGLE_API_KEY=sua_chave_aqui


Execute via Docker (Recomendado):

docker build -t iscoolgpt .
docker run -p 8000:8000 --env-file .env iscoolgpt


Acesse:

Chat Web: Abra http://localhost:8000 no navegador.

Documentação API: Abra http://localhost:8000/docs.

📖 Documentação da API (Swagger/OpenAPI)

O projeto utiliza o FastAPI, que gera documentação automática e interativa seguindo o padrão OpenAPI.

Endpoints Principais

Método

Endpoint

Descrição

GET

/

Interface Web do Chat (Frontend).

GET

/docs

Swagger UI - Documentação interativa para testes.

GET

/redoc

ReDoc - Documentação alternativa em formato de leitura.

POST

/ask

Endpoint principal que recebe a pergunta e retorna a resposta da IA.

Exemplo de Payload (/ask):

{
  "question": "O que é um Load Balancer?",
  "subject": "Cloud Computing"
}


🛡️ Segurança e Decisões Técnicas

IAM Least Privilege:

O usuário de CI/CD (github-actions) possui permissão PowerUser no CodeCommit, impedindo a deleção acidental de repositórios.

A Role de Execução do ECS (ecsTaskExecutionRole) permite acesso estrito apenas ao ECR e CloudWatch.

Networking:

Security Group configurado para liberar apenas a porta TCP/8000.

Acesso SSH (Porta 22) bloqueado por padrão (arquitetura imutável).

Segredos:

As credenciais AWS são injetadas via GitHub Secrets.

A GOOGLE_API_KEY é injetada como variável de ambiente na Task Definition, sem exposição no código-fonte.

🔧 Guia de Troubleshooting

Se encontrar problemas, siga este guia rápido:

1. Erro: "404 Model Not Found" ao perguntar algo

Causa: A versão do modelo Gemini configurada no código foi descontinuada ou está incorreta.

Solução: Verifique no app/main.py se o modelo é gemini-1.5-flash ou gemini-2.5-flash. Atualize o requirements.txt para google-generativeai>=0.8.0.

2. Erro: "Erro de Configuração: A chave da API... não foi encontrada"

Causa: O container subiu, mas a variável de ambiente não chegou nele.

Solução:

Vá no AWS ECS -> Task Definitions.

Crie uma nova revisão da Task.

Confirme se a chave GOOGLE_API_KEY está na seção "Environment Variables" do container.

Atualize o Serviço forçando uma nova implantação (--force-new-deployment).

3. Pipeline falha no passo "Mirror to AWS CodeCommit"

Causa: Problema de permissão no usuário IAM ou o repositório não existe.

Solução:

Confirme se o repositório iscoolgpt-repo existe no CodeCommit na região us-east-1.

Confirme se o usuário IAM github-actions tem a política AWSCodeCommitPowerUser.

4. Site não carrega (Timeout)

Causa: Bloqueio de Firewall/Rede.

Solução: Verifique o Security Group no ECS/EC2. Garanta que há uma regra de entrada (Inbound) permitindo TCP 8000 para 0.0.0.0/0.

👥 Autor

Projeto desenvolvido individualmente para a avaliação AV2 da disciplina de Cloud Computing.
