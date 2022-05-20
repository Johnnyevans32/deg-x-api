import tempfile

import nox


@nox.session(python=["3.10"], reuse_venv=True)
def tests(session):
    session.install("poetry")
    session.run("poetry", "install")
    session.install("-r", "requirements.txt")
    session.run("python", "-m", "coverage", "run", "-m", "pytest")
    session.run("coverage", "report")


@nox.session(reuse_venv=True)
def lint(session):
    # session.install("poetry")
    # session.run("poetry", "install")
    session.run("black", "--check", ".")
    session.run("flake8", ".")


@nox.session(reuse_venv=True)
def typing(session):
    # session.install("poetry")
    # session.run("poetry", "install")
    session.run("mypy", "--config-file", "mypy.ini", ".")


@nox.session(reuse_venv=True)
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
