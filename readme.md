## Pré-requisitos

Antes de começar, certifique-se de ter instalado o Python na versão 3.9.13. Você pode verificar a versão do Python com o seguinte comando:

python --version

Se você não tem o Python instalado, pode baixá-lo aqui: https://www.python.org/downloads/release/python-3913/

## Configuração do Ambiente

Siga os passos abaixo para configurar seu ambiente de desenvolvimento:

### 1. Ativar a Virtual Environment

Para criar e ativar uma virtual environment, execute:

python -m venv venv
source venv/bin/activate  # No Windows use venv\Scripts\activate

### 2. Instalar Dependências

Instale todas as dependências necessárias executando:

pip install -r requirements.txt

### 3. Configurar Variáveis de Ambiente

Crie um arquivo .env na raiz do projeto e adicione a seguinte linha:

DATABASE_URL="sua_string_de_conexão_aqui"

### 4. Iniciar o Servidor Local

Para iniciar o servidor local, utilize o seguinte comando:

uvicorn app.main:app --reload