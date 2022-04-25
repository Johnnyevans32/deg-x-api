# README

# *DEG X**

### What is this repository for?

- Quick summary
- Version
- [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### How do I get set up?

- Summary of set up

### How to run project?

First we install virtualenv by doing

- `pip install virtualenv`

after pip installing that next, do this depending on your python version

- `python3 -m virtualenv venv`

then activate the venv by so

- `source venv/bin/activate`

- `pip install -r requirements.txt` # install libraries to getting started

* Copy env file - `cp .env.example .env`

* and create a `logs.log` file to store the logs of the console

It's easy, you two options to run project.

- sh scripts/runserver.sh
- python main.py
- sh scripts/runserver-dev.sh

then navigate to the swagger documentation view on route to see the docs view
`htttp://localhost:8000/docs`

### Contribution guidelines

- Writing tests
- Code review
  
  NB: Pipeline tests and integration must pass before PRs can be considered to be merged
- Other guidelines

  Remember to lint and clean imports with this single bash command `sh scripts/cleancodebase.sh`

### Who do I talk to?

- Repo owner or admin
- Other community or team contact
