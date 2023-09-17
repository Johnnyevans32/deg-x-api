import tempfile

import nox

# @nox.session(python=["3.10"])
# def shared_venv(session: nox.Session):
#     session.install("poetry")
#     session.run("poetry", "install")
#     session.install("-r", "requirements.txt")

#     if session.posargs:
#         match session.posargs[0]:
#             case 'tests':
#                 session.run("python", "-m", "coverage", "run", "-m", "pytest")
#                 session.run("coverage", "report")
#             case 'lint':
#                 session.run("black", "--target-version", "py310")
#                 session.run("flake8", ".")
#             case 'typing':
#                 session.run("mypy", "--config-file", "mypy.ini", ".", "--show-traceback")
#             case _:
#                 pass


def setup(session: nox.Session) -> None:
    session.install("poetry")
    session.run("poetry", "lock", "--no-update")
    session.run("poetry", "--no-ansi", "install")


@nox.session(python=["3.10"])
def test_build(session: nox.Session) -> None:
    setup(session)
    session.install("-r", "requirements.txt")
    session.run("python", "-m", "pip", "uninstall", "bson", "--yes")
    session.run("python", "-m", "pip", "uninstall", "pymongo", "--yes")
    session.install("pymongo")
    session.run("python", "-m", "coverage", "run", "-m", "pytest")
    session.run("coverage", "report")
    # session.notify('shared_venv', posargs=['tests'])


@nox.session
def lint_build(session: nox.Session) -> None:
    setup(session)
    session.run("black", "--check", ".", "--extend-exclude=libsodium")
    session.run("flake8", "--import-order-style", "google", ".")
    # session.notify('shared_venv', posargs=['lint'])


@nox.session
def typing_build(session: nox.Session) -> None:
    setup(session)
    session.run("mypy", "--config-file", "mypy.ini", ".")
    # session.notify('shared_venv', posargs=['typing'])


@nox.session
def safety_build(session: nox.Session) -> None:
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
