"""Migration graph and offline SQL checks that do not require a running database."""

from io import StringIO
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from alembic import command

BACKEND = Path(__file__).resolve().parents[2]


def test_linear_migration_chain_and_offline_sql(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")
    output = StringIO()
    cfg = Config(output_buffer=output)
    cfg.set_main_option("script_location", str(BACKEND / "alembic"))
    script = ScriptDirectory.from_config(cfg)
    assert script.get_heads() == ["0009_wall"]
    assert len(list(script.walk_revisions())) == 9
    command.upgrade(cfg, "head", sql=True)
    sql = output.getvalue()
    assert "CREATE EXTENSION IF NOT EXISTS vector" in sql
    assert "USING hnsw" in sql
    assert "VECTOR(384)" in sql
    assert "CREATE TABLE user_roles" in sql
    assert "CREATE TABLE wall_follows" in sql
    assert "fk_proposals_match_score_id" in sql
    output.truncate(0)
    output.seek(0)
    command.downgrade(cfg, "0009_wall:base", sql=True)
    assert "DROP TABLE users" in output.getvalue()
    assert "DROP EXTENSION" not in output.getvalue()
