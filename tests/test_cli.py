import json

from typer.testing import CliRunner

from docgraph.cli import app


def test_cli_init_build_validate_and_stats(tmp_path) -> None:
    runner = CliRunner()
    project = tmp_path / "project"

    init_result = runner.invoke(app, ["init", str(project)])
    assert init_result.exit_code == 0
    assert (project / "docgraph.yaml").exists()
    assert (project / "ontology.yaml").exists()

    config_path = project / "docgraph.yaml"
    build_result = runner.invoke(app, ["build", "--config", str(config_path)])
    assert build_result.exit_code == 0

    output = project / "output" / "graph.json"
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["entities"]
    assert payload["relationships"]

    validate_result = runner.invoke(app, ["validate", "--config", str(config_path)])
    assert validate_result.exit_code == 0

    stats_result = runner.invoke(app, ["stats", "--config", str(config_path)])
    assert stats_result.exit_code == 0
    assert "Knowledge Graph Statistics" in stats_result.output
