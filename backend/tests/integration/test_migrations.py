"""Exercise the migration contract on PostgreSQL with pgvector.

Set TEST_DATABASE_URL explicitly. Each test uses a unique schema and rolls back all
of its changes; the application's DATABASE_URL is never used by these tests.
"""

import os
from pathlib import Path
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session, configure_mappers

from alembic import command
from app.database.base import Base
from app.models import (
    BrandProfile,
    Campaign,
    CreatorProfile,
    Proposal,
    ProposalStatus,
    User,
    UserRole,
    UserRoleRow,
)

BACKEND = Path(__file__).resolve().parents[2]
FOUNDATION = "0001_initial_foundation"
HEAD = "0009_wall"
EXPECTED_TABLES = {
    "users",
    "user_roles",
    "creator_profiles",
    "brand_profiles",
    "campaigns",
    "proposals",
    "creator_preferences",
    "rate_card_items",
    "creator_availability",
    "social_accounts",
    "social_metric_snapshots",
    "creator_content_items",
    "integration_sync_logs",
    "brand_products",
    "campaign_requirements",
    "campaign_discovery_policy",
    "competitor_registry",
    "campaign_competitor_policies",
    "creator_representations",
    "creator_content_clusters",
    "model_versions",
    "match_scores",
    "match_evidence",
    "eligibility_exclusions",
    "pair_labels",
    "experiment_runs",
    "proposal_versions",
    "collaborations",
    "agreements",
    "messages",
    "collaboration_outcomes",
    "documents",
    "document_chunks",
    "ai_execution_logs",
    "wall_posts",
    "wall_comments",
    "wall_reactions",
    "wall_follows",
}


@pytest.fixture(scope="module")
def engine():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL migration tests")
    engine = sa.create_engine(url)
    with engine.begin() as connection:
        connection.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public"))
    yield engine
    engine.dispose()


@pytest.fixture
def db(engine):
    with engine.connect() as connection:
        transaction = connection.begin()
        schema = f"migration_test_{uuid4().hex}"
        default_schema = connection.dialect.default_schema_name
        connection.execute(sa.text(f'CREATE SCHEMA "{schema}"'))
        connection.execute(sa.text(f'SET LOCAL search_path TO "{schema}", public'))
        connection.dialect.default_schema_name = schema
        try:
            yield connection
        finally:
            transaction.rollback()
            connection.dialect.default_schema_name = default_schema


def config(db):
    cfg = Config()
    cfg.set_main_option("script_location", str(BACKEND / "alembic"))
    cfg.attributes["connection"] = db
    return cfg


def scalar(db, query, **params):
    return db.scalar(sa.text(query), params)


def seed_foundation(db):
    ids = {
        name: uuid4()
        for name in ("creator_user", "brand_user", "creator", "brand", "campaign", "proposal")
    }
    db.execute(
        sa.text("""
        INSERT INTO users (id, email, hashed_password, role, is_active)
        VALUES (:creator_user, 'creator@example.test', 'test-only', 'CREATOR', true),
               (:brand_user, 'brand@example.test', 'test-only', 'BRAND', false)
    """),
        ids,
    )
    db.execute(
        sa.text("""
        INSERT INTO creator_profiles (id, user_id, display_name, categories, audience_summary)
        VALUES (:creator, :creator_user, 'Creator', '["fitness"]', '{"country":"IN"}')
    """),
        ids,
    )
    db.execute(
        sa.text("""
        INSERT INTO brand_profiles (id, user_id, brand_name) VALUES (:brand, :brand_user, 'Brand')
    """),
        ids,
    )
    db.execute(
        sa.text("""
        INSERT INTO campaigns (id, brand_profile_id, title, brief, budget_amount)
        VALUES (:campaign, :brand, 'Campaign', 'Original brief', 18000)
    """),
        ids,
    )
    db.execute(
        sa.text("""
        INSERT INTO proposals (id, campaign_id, creator_profile_id, status, commercial_offer,
        message)
        VALUES (:proposal, :campaign, :creator, 'SUBMITTED', 12000, 'Original proposal')
    """),
        ids,
    )
    return ids


@pytest.fixture
def populated(db):
    command.upgrade(config(db), FOUNDATION)
    ids = seed_foundation(db)
    command.upgrade(config(db), "head")
    return db, ids


def test_fresh_upgrade_metadata_and_full_round_trip(db):
    cfg = config(db)
    command.upgrade(cfg, "head")
    assert set(sa.inspect(db).get_table_names()) == EXPECTED_TABLES | {"alembic_version"}
    assert scalar(db, "SELECT version_num FROM alembic_version") == HEAD
    configure_mappers()
    context = MigrationContext.configure(
        db, opts={"compare_type": True, "compare_server_default": True}
    )
    assert compare_metadata(context, Base.metadata) == []
    command.downgrade(cfg, "base")
    assert sa.inspect(db).get_table_names() == ["alembic_version"]
    command.upgrade(cfg, "head")
    assert set(sa.inspect(db).get_table_names()) == EXPECTED_TABLES | {"alembic_version"}


def test_existing_rows_survive_forward_and_backward_migration(populated):
    db, ids = populated
    assert scalar(db, "SELECT count(*) FROM user_roles") == 2
    assert scalar(db, "SELECT status FROM users WHERE id=:brand_user", **ids) == "INACTIVE"
    assert scalar(db, "SELECT raw_brief FROM campaigns") == "Original brief"
    assert scalar(db, "SELECT budget_max FROM campaigns") == 18000
    assert scalar(db, "SELECT count(*) FROM campaign_requirements") == 0
    version = db.execute(sa.text("SELECT * FROM proposal_versions")).mappings().one()
    assert (version["version_no"], version["amount"], version["created_by_user_id"]) == (
        1,
        12000,
        ids["creator_user"],
    )
    assert version["message"] == "Original proposal"
    assert scalar(db, "SELECT count(*) FROM collaborations") == 0
    assert scalar(db, "SELECT count(*) FROM creator_profiles WHERE categories ? 'fitness'") == 1
    command.downgrade(config(db), FOUNDATION)
    assert scalar(db, "SELECT role FROM users WHERE id=:creator_user", **ids) == "CREATOR"
    assert scalar(db, "SELECT is_active FROM users WHERE id=:brand_user", **ids) is False
    assert scalar(db, "SELECT commercial_offer FROM proposals") == 12000
    assert scalar(db, "SELECT brief FROM campaigns") == "Original brief"
    assert scalar(db, "SELECT categories FROM creator_profiles") == ["fitness"]
    command.upgrade(config(db), "head")
    assert scalar(db, "SELECT count(*) FROM proposal_versions") == 1


def test_dual_role_orm_and_lossy_downgrade_guard(populated):
    db, ids = populated
    with Session(bind=db, join_transaction_mode="create_savepoint") as session:
        user = session.get(User, ids["creator_user"])
        user.roles.append(UserRoleRow(role=UserRole.BRAND))
        session.flush()
        assert {r.role for r in user.roles} == {UserRole.CREATOR, UserRole.BRAND}
        assert user.creator_profile.display_name == "Creator"
        session.commit()
    with pytest.raises(DBAPIError, match="Cannot downgrade dual-role identity"), db.begin_nested():
        command.downgrade(config(db), FOUNDATION)
    assert scalar(db, "SELECT version_num FROM alembic_version") == HEAD
    assert scalar(db, "SELECT count(*) FROM user_roles WHERE user_id=:creator_user", **ids) == 2
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(
            sa.text("""
            INSERT INTO user_roles (id, user_id, role) VALUES (gen_random_uuid(), :creator_user,
            'BRAND')
        """),
            ids,
        )


@pytest.mark.parametrize("status", ["REVIEWING", "COUNTER_OFFER", "WITHDRAWN"])
def test_new_proposal_statuses_cannot_be_silently_downgraded(populated, status):
    db, _ = populated
    db.execute(sa.text("UPDATE proposals SET status=:status"), {"status": status})
    with pytest.raises(DBAPIError, match="Cannot downgrade proposals"), db.begin_nested():
        command.downgrade(config(db), "0007_matching_and_labels")
    assert scalar(db, "SELECT status FROM proposals") == status
    assert scalar(db, "SELECT version_num FROM alembic_version") == HEAD


def test_historical_rates_allow_only_one_live_price(populated):
    db, ids = populated
    query = sa.text("""
        INSERT INTO rate_card_items (id, creator_id, platform, content_type, rate_amount, active)
        VALUES (gen_random_uuid(), :creator, 'INSTAGRAM', 'REEL', :amount, :active)
    """)
    db.execute(query, {**ids, "amount": 7000, "active": True})
    db.execute(query, {**ids, "amount": 5000, "active": False})
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(query, {**ids, "amount": 8000, "active": True})
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(query, {**ids, "amount": -1, "active": False})
    assert scalar(db, "SELECT count(*) FROM rate_card_items") == 2


def test_vectors_current_version_and_hnsw_indexes(populated):
    db, ids = populated
    vector = "[" + ",".join(["1"] + ["0"] * 383) + "]"
    query = sa.text("""
        INSERT INTO creator_representations
        (id, creator_id, representation_version, encoder_name, overall_embedding, is_current)
        VALUES (gen_random_uuid(), :creator, :version, 'test-encoder', CAST(:vector AS vector),
        :current)
    """)
    db.execute(query, {**ids, "version": "v1", "vector": vector, "current": True})
    db.execute(query, {**ids, "version": "v0", "vector": vector, "current": False})
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(query, {**ids, "version": "v2", "vector": vector, "current": True})
    with pytest.raises(DBAPIError, match="dimensions"), db.begin_nested():
        db.execute(query, {**ids, "version": "bad", "vector": "[1,0]", "current": False})
    assert (
        scalar(db, "SELECT vector_dims(overall_embedding) FROM creator_representations LIMIT 1")
        == 384
    )
    indexes = (
        db.execute(
            sa.text("""
        SELECT indexdef FROM pg_indexes WHERE schemaname=current_schema() AND indexname IN
        ('ix_repr_vec', 'ix_cluster_vec', 'ix_chunk_vec')
    """)
        )
        .scalars()
        .all()
    )
    assert len(indexes) == 3
    assert all("USING hnsw" in sql and "vector_cosine_ops" in sql for sql in indexes)


def test_reciprocal_directions_and_proposal_evidence_foreign_key(populated):
    db, ids = populated
    query = sa.text("""
        INSERT INTO match_scores
        (id, campaign_id, creator_id, direction, eligibility_status, feature_version,
         model_version, scoring_profile)
        VALUES (gen_random_uuid(), :campaign, :creator, :direction, 'PASS', 'feat-v1',
        'rules-v1', 'UGC')
    """)
    for direction in ("BRAND_TO_CREATOR", "CREATOR_TO_BRAND"):
        db.execute(query, {**ids, "direction": direction})
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(query, {**ids, "direction": "CREATOR_TO_BRAND"})
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(sa.text("UPDATE proposals SET match_score_id=gen_random_uuid()"))
    assert scalar(db, "SELECT count(*) FROM match_scores") == 2


def test_pair_labels_compute_mutual_relevance(populated):
    db, ids = populated
    query = sa.text("""
        INSERT INTO pair_labels
        (id, campaign_id, creator_id, rater_id, brand_rating, creator_rating, label_source,
        rubric_version)
        VALUES (gen_random_uuid(), :campaign, :creator, :rater, :brand, :creator_rating,
        'HUMAN', 'v1')
        RETURNING mutually_relevant
    """)
    assert db.scalar(query, {**ids, "rater": "a", "brand": 3, "creator_rating": 2}) is True
    assert db.scalar(query, {**ids, "rater": "b", "brand": 3, "creator_rating": 1}) is False
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(query, {**ids, "rater": "c", "brand": 4, "creator_rating": 2})


def test_proposal_versions_and_single_collaboration(populated):
    db, ids = populated
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(
            sa.text("""
            INSERT INTO proposal_versions
            (id, proposal_id, version_no, created_by_user_id, created_by_role)
            VALUES (gen_random_uuid(), :proposal, 1, :creator_user, 'CREATOR')
        """),
            ids,
        )
    query = sa.text("""
        INSERT INTO collaborations (id, accepted_proposal_id, campaign_id, creator_id, brand_id)
        VALUES (gen_random_uuid(), :proposal, :campaign, :creator, :brand)
    """)
    db.execute(query, ids)
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(query, ids)
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(
            sa.text("""
            INSERT INTO messages (id, sender_user_id, body)
            VALUES (gen_random_uuid(), :creator_user, 'Missing proposal or collaboration')
        """),
            ids,
        )


def test_wall_reactions_are_unique_and_children_cascade(populated):
    db, ids = populated
    post_id = uuid4()
    params = {**ids, "post": post_id}
    db.execute(
        sa.text("""
        INSERT INTO wall_posts (id, author_user_id, author_role, author_profile_id, body)
        VALUES (:post, :creator_user, 'CREATOR', :creator, 'An idea')
    """),
        params,
    )
    reaction = sa.text("INSERT INTO wall_reactions (post_id, user_id) VALUES (:post, :brand_user)")
    db.execute(reaction, params)
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(reaction, params)
    db.execute(
        sa.text("""
        INSERT INTO wall_comments (id, post_id, author_user_id, author_role, body)
        VALUES (gen_random_uuid(), :post, :brand_user, 'BRAND', 'A reply')
    """),
        params,
    )
    db.execute(sa.text("DELETE FROM wall_posts WHERE id=:post"), params)
    assert scalar(db, "SELECT count(*) FROM wall_comments") == 0
    assert scalar(db, "SELECT count(*) FROM wall_reactions") == 0


def test_existing_models_can_insert_and_read_at_head(db):
    command.upgrade(config(db), "head")
    with Session(bind=db, join_transaction_mode="create_savepoint") as session:
        user = User(
            email="dual@example.test",
            hashed_password="test-only",
            roles=[UserRoleRow(role=UserRole.CREATOR), UserRoleRow(role=UserRole.BRAND)],
        )
        creator = CreatorProfile(user=user, display_name="Creator")
        brand = BrandProfile(user=user, brand_name="Brand")
        campaign = Campaign(brand_profile=brand, title="Campaign")
        proposal = Proposal(
            campaign=campaign, creator_profile=creator, status=ProposalStatus.COUNTER_OFFER
        )
        session.add_all([user, creator, brand, campaign, proposal])
        session.flush()
        session.expire_all()
        assert proposal.status == ProposalStatus.COUNTER_OFFER
        assert creator.categories == []
        assert creator.audience_summary == {}
        assert user.status == "ACTIVE"
        assert campaign.status == "DRAFT"
