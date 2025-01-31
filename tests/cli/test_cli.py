import shutil
import subprocess
from pathlib import Path


def _popen_in_shell(args: str) -> tuple[subprocess.Popen, str, str]:
    """Run command in shell."""
    # shell=True is needed for subprocess.Popen to
    # locate the installed aisle command.
    process = subprocess.Popen(  # noqa: S602 (insecure shell=True)
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True,
    )
    stdin, stdout = process.communicate()
    return process, stdin, stdout


def test_cli_plantuml(snapshot):  # noqa: WPS210
    """Test that command works and generates plantuml."""
    process, stdout, stderr = _popen_in_shell(
        "aisle generate "
        "--directory tests/__gen__ "
        "--fmt plantuml "
        "./tests/fixtures/test_1_a.aisle"
    )
    assert process.returncode == 0, (stdout, stderr)
    context = Path("./tests/__gen__/context.puml").read_text()
    containers = Path("./tests/__gen__/containers.puml").read_text()
    deployments = Path("./tests/__gen__/deployment.puml").read_text()
    shutil.rmtree("./tests/__gen__")
    assert context + containers + deployments == snapshot
    assert not stderr


def test_cli_mermaid(snapshot):  # noqa: WPS210
    """Test that command works and generates mermaid."""
    process, stdout, stderr = _popen_in_shell(
        "aisle generate "
        "--directory tests/__gen__ "
        "--fmt mermaid "
        "./tests/fixtures/test_1_a.aisle"
    )
    assert process.returncode == 0, (stdout, stderr)
    context = Path("./tests/__gen__/context.txt").read_text()
    containers = Path("./tests/__gen__/containers.txt").read_text()
    deployments = Path("./tests/__gen__/deployment.txt").read_text()
    shutil.rmtree("./tests/__gen__")
    assert context + containers + deployments == snapshot
    assert not stderr


def test_cli_lexer_error(snapshot):
    """Test that lexer errors are outputted."""
    process, stdout, stderr = _popen_in_shell(
        "aisle generate "
        "--directory tests/__gen__ "
        "./tests/fixtures/test_lexer_error.aisle"
    )
    assert process.returncode == 1, (stdout, stderr)
    assert not stdout
    assert stderr == snapshot


def test_cli_parser_error(snapshot):
    """Test that parser errors are outputted."""
    process, stdout, stderr = _popen_in_shell(
        "aisle generate "
        "--directory tests/__gen__ "
        "./tests/fixtures/test_parser_error.aisle"
    )
    assert process.returncode == 1, (stdout, stderr)
    assert not stdout
    assert stderr == snapshot


def test_cli_analyser_error(snapshot):
    """Test that analyser errors are outputted."""
    process, stdout, stderr = _popen_in_shell(
        "aisle generate "
        "--directory tests/__gen__ "
        "./tests/fixtures/test_analyser_error.aisle"
    )
    assert process.returncode == 1, (stdout, stderr)
    assert not stdout
    assert stderr == snapshot


def test_cli_wrong_format(snapshot):
    """Test that wrong format name is rejected."""
    process, stdout, stderr = _popen_in_shell(
        "aisle generate "
        "--directory tests/__gen__ "
        "--fmt wrongfmt "
        "./tests/fixtures/test_analyser_error.aisle"
    )
    assert process.returncode == 1, (stdout, stderr)
    assert not stdout
    assert stderr == snapshot
