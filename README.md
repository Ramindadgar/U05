# BB-api-u05-doe21

- [Getting started](#Getting-started)
- [Introduction - the project's aim](#Introduction-the-projects-aim)
- [Technologies](#Technologies)
- [Test and Deploy](#TestandDeploy)
- [Scope of functionalities](#Scopeoffunctionalities)
- [Examples of use](#Examplesofuse)
- [Illustrations](#Illustrations)
- [Agile methods and tools](#Agile methods and tools)
- [Contributors](#Contributors)


# Getting started
Since this is a python and Docker based project, we assume that the programs is already installed on your computer. if not, install them on your computer.
    
### To download app:
- Git clone https://gitlab.com/arashafazeli/bb-api-u05-doe21.git

### To access FastAPI
- Docker-compose up -d --build
- localhost:8008

### To launch tests
- Docker-compose exec web pytest . -vvv

### Virtual enviroment
- Ask Arash

## Introduction - the project's aim
Build an MVP (Minimum Viable Product), and focus on creating a functioning DevOps environment containing at least two pipelines, one for testing and for production. 


## Technologies
- Docker
- Postgres
- PGAdmin
- FastAPI
- Python



## Test and Deploy
Tool to compare the python code against some of the style conventions and searching for potential bugs and errors.
- PEP8
- flake8

Pytest
- Following statuscodes and format are tested in Pytest
- status_code == 200
- status_code == 404
- status_code == 422 
- response.json

Tool to contain and deploy app
- Docker

 ## Scope of functionalities 
- Public GitLab repository has to be initialized.
- Any requirement regarding endpoint includes not only the endpoint itself but also thorough and relevant tests.
- The API has to be ready for deployment and execution using Docker at the very beginning.
- The repository has to contain a file which describes all of the libraries that has to been installed to be able to execute both the API and the tests.
- The code has to be written accordingly to PEP8 (This does not apply to the maximum line length of 80 characters or less)



## Examples of use
- https://github.com/arashafazeli/Breakingbad-api-doe21/releases


## Illustrations
- Our trello bord over the sprints.  
    https://trello.com/b/izrugjI9/breakingbadu05


## Agile methods and tools
- We have worked agile with KANBAN methods.
- We used Trelloboard to plan the sprints.
- GitHub
- Gitlab
- Trelloboard
- Planing Poker
- Jam board



## Contributors
- Kjell Bovin
- Alva Thunberg
- Arash Afazeli
- Ramin Dadgar
- Ludvig Ravelin


