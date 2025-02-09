# 🧩 Desafio Prático

Esta página contém as instruções necessárias para utilizar o projeto, que realiza o deploy de um modelo de previsão de demanda de vendas. A implementação foi desenvolvida utilizando o conjunto de ferramentas disponíveis na Google Cloud Platform (GCP).

### 1. Requisitos 📋

✅ Permissões na GCP: É necessário ter perfil de administrador na conta da Google Cloud Platform (GCP) da sua empresa.

🛠️ Ferramentas utilizadas:

- [Python](https://www.python.org/) para desenvolvimento do modelo.
- [Terraform](https://www.terraform.io/) gerenciamento de infraestrutura.
- [Poetry](https://python-poetry.org/) gerenciamento de dependências do projeto.
- [gcloud CLI](https://cloud.google.com/) ferramenta de linha de comando da Google Cloud. 
- [Git](https://git-scm.com/) ferramenta para controle de controle de versão de código.

💻 Ambiente de desenvolvimento: O projeto foi desenvolvido e testado em uma máquina com [Linux Ubuntu](https://ubuntu.com/) *24.04*.

### 2. Google Cloud

Efetue o login na Google Cloud com o comando:

```bash
gcloud auth login
```

É preciso abilitar as APIs na GCP. Para isso, use o comando:

```bash
gcloud services enable \
    composer.googleapis.com \
    compute.googleapis.com \
    aiplatform.googleapis.com \
    storage.googleapis.com \
    pubsub.googleapis.com \
    cloudfunctions.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com
```

Adicione permissão para seu o usuario poder executar o *Composer*, verifique no *IAM* a sua conta ou crie uma
de serviço:

```bash
gcloud projects add-iam-policy-binding SEU-PROJECTO-NA-GCP \
  --member="serviceAccount:service-XXX11@cloudcomposer-accounts.iam.gserviceaccount.com" \
  --role="roles/composer.ServiceAgentV2Ext"
```

### 3. Projeto 🚀

Siga os passos abaixo para configurar e executar o projeto na sua estação de trabalho:

1. **Baixe o projeto**:

Faça o download do projeto para o seu ambiente local.

2. **Navegue até o diretório do projeto e configure o ambiente**

Execute os seguintes comandos no terminal: 

```bash
cd ml-sales-model && poetry shell && poetry update
```

- cd ml-sales-model: Acessa o diretório do projeto.
- poetry shell: Ativa o ambiente virtual do Poetry.
- poetry update: Atualiza / instala as dependências do projeto.

3. **Treine e teste o modelo localmente**

Para treinar o modelo de teste, execute:

```bash
python3.11 experiments/model.py
```

- Esse comando irá treinar o modelo e salvar o arquivo pickle na pasta **data/**.

4. **Sobre o dataset**

Foi utilizado um dataset de testes exclusivamente para validar o fluxo de criação do modelo. Ele não representa dados **reais**, mas sim um exemplo para garantir que o pipeline funcione corretamente.

#### 3.1 Infraestrutura na GCP com Terraform 🌐

Agora, é necessário criar a infraestrutura na Google Cloud Platform (GCP) utilizando o Terraform. Siga os passos abaixo:

1. **Ajuste as variáveis do Terraform**

- Edite o arquivo *(terraform/terraform.tfvars*) para configurar as variáveis de acordo com o seu ambiente na GCP.
- Certifique-se de ajustar parâmetros como:
  - Project ID: O ID do seu projeto na GCP.
  - Region/Zone: A região e zona onde os recursos serão provisionados.
  - Credenciais da Conta: A conta de serviço que o Terraform utilizará para autenticação.

Exemplo de variáveis:

```hcl
GOOGLE_CREDENTIALS_PATH = "~/.config/gcloud/service@xxx.com.json"
GOOGLE_PROJECT_ID       = "meu-projeto-na-gcp"
GOOGLE_REGION           = "us-west-1"
```

Depois de ajustar as variaveis:

```hcl
terraform/terraform.tfvars 
```

2. **Terraform**

Execute o comando abaixo para inicializar o Terraform e baixar os providers necessários:

```bash
cd terraform && terraform init
```

3. **Valide a configuração**

Verifique se o arquivo de configuração está correto com o comando:

```bash
terraform validate
```

4. **Planeje a infraestrutura**

Use o comando terraform plan para visualizar as mudanças que serão aplicadas:

```bash
terraform plan
```

5. **Aplique a infraestrutura**

Para criar os recursos na GCP, execute:

```bash
terraform apply
```

Confirme a ação digitando **yes** quando solicitado.

**Observações importantes 🚨**

- Confirme se todos os recursos foram criados na GPC.
- Certifique-se de que a conta de serviço utilizada pelo Terraform tenha permissões suficientes para criar e gerenciar recursos na GCP.
- Mantenha o arquivo (*terraform.tfstate*) seguro, pois ele contém o estado atual da sua infraestrutura.

#### 3.2. Pipeline de Treino e Deploy 🚀📊

Agora, é necessário ajustar as variáveis no script de treino do modelo e registrá-lo no Vertex AI. 🛠️🤖

1. **Terminal**

Primeiro, defina a variável de ambiente no terminal:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="caminho/para/sua/chave.json"
```

2. **Treino**

Edite o script Python *(pipelines/train_model.py)* 🖋️🐍 e ajuste as variáveis: 🔧📝

```hcl
project_id = ""
region = ""
bucket_name = ""
```

3. **Bucket**

Copie os arquivos para o bucket da GCP:

```bash
gsutil cp data/sales_dataset.csv gs://mlops-models15/
gsutil cp data/sales_forecast_model.pkl gs://mlops-models15/models
```

4. **Teste**

Você pode nesse momento executar o script:

```bash
python3.11 pipelines/train_model.py
```

Verifique no Vertex AI a pipeline de treino sendo executada.

#### 3.3. Monitoramento

Agora precisamos garantir o monitoramento do modelo.

1. **Variáveis**

Ajuste as variáveis no script de deploy *(pipelines/deploy_model.py)*: 🔧📝

```hcl
project_id = ""
region = "us-west1"
```

2. **Cloud Function**

Crie uma Cloud Function para monitorar o deploy:

```bash
gcloud functions deploy deploy_model \
  --runtime python311 \
  --trigger-event google.storage.object.finalize \
  --trigger-resource seu_projeto_gcp-ml-bucket \
  --entry-point deploy_model
```

3. **Logs e Monitoramento**

Configuração de Logging:

```bash
gcloud logging sinks create ml_logs \
  storage.googleapis.com/seu_projeto_gcp-ml-bucket
```

4. **Criando Alerta no Cloud Monitoring**

Criamos um alerta que notifica via Pub/Sub caso a latência da inferência ultrapasse *500ms*.

```bash
gcloud pubsub topics create ml_alerts
```

Agora crie o alerta:

```bash
gcloud monitoring policies create \
  --notification-channels=ml_alerts \
  --display-name="Alerta de Latência no Modelo de Vendas" \
  --condition-threshold-value=500 \
  --condition-threshold-comparison=COMPARISON_GT \
  --condition-threshold-aggregations=alignment_period=60s,per_series_aligner=ALIGN_PERCENTILE_99 \
  --condition-threshold-filter='metric.type="serving_latency"' \
  --duration=60s
```

#### 4. Conclusão

Resumo do que foi feito:

- ✅ Infraestrutura como Código (IaC)

Terraform provisiona Cloud Storage, Cloud Composer (Airflow) e Vertex AI Training Job.

- ✅ Pipeline de Treinamento e Deploy

Script Python para treinar o modelo, salvar no Cloud Storage e registrar no Vertex AI.

- ✅ Monitoramento e Logging

Voltar ao [README](./README.md) 👈 inicial.
Cloud Logging armazena logs do treinamento e inferência. 
Cloud Monitoring cria um alerta via Pub/Sub caso a latência ultrapasse 500ms.

Com isso, temos um pipeline completo para treino, deplo e monitoramento do modelo na GCP. 🚀
