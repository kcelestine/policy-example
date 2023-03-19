Setup virtual environment for the specific Python version (3.10):
```shell
pyenv local 3.10
virtualenv venv -p python3.10
source venv/bin/activate
```

Install the dependencies:
```shell
pip install fastapi
pip install redis
pip install uvicorn
pip freeze > requirements.txt
```

Test the API:
```shell
curl -iX 'GET' 'http://localhost:8055/api/quiz-topics'
```

Setup Git repository in the current project folder:
```shell
git init .
git remote add origin git@github.com:<username>/quizless.git
```
