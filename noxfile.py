import tempfile

import nox


@nox.session(python=["3.10"])
def shared_venv(session):
    session.install("poetry")
    session.run("poetry", "install")
    session.install("-r", "requirements.txt")

    if session.posargs:
        match session.posargs[0]:
            case 'tests':
                session.run("python", "-m", "coverage", "run", "-m", "pytest")
                session.run("coverage", "report")
            case 'lint':
                session.run("black", "--check", ".")
                session.run("flake8", ".")
            case 'typing':
                session.run("mypy", "--config-file", "mypy.ini", ".")
            case _:
                pass


@nox.session
def tests(session):
    session.notify('shared_venv', posargs=['tests'])


@nox.session
def lint(session):
    session.notify('shared_venv', posargs=['lint'])


@nox.session
def typing(session):
    session.notify('shared_venv', posargs=['typing'])


@nox.session
def safety(session):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install("safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")
