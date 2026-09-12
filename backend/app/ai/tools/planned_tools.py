from collections.abc import Mapping
from typing import Any


def search_creators(criteria: Mapping[str, Any]) -> list[dict[str, Any]]:
    raise NotImplementedError("Creator search will be implemented in a later phase.")


def get_creator_profile(creator_id: str) -> dict[str, Any]:
    raise NotImplementedError("Creator profile lookup will be implemented in a later phase.")


def get_youtube_statistics(creator_id: str) -> dict[str, Any]:
    raise NotImplementedError("YouTube statistics retrieval will be implemented in a later phase.")


def get_instagram_statistics(creator_id: str) -> dict[str, Any]:
    raise NotImplementedError(
        "Instagram statistics retrieval will be implemented in a later phase."
    )


def calculate_ml_match(features: Mapping[str, float]) -> float:
    raise NotImplementedError("ML match scoring will be implemented in a later phase.")


def calculate_semantic_similarity(left_text: str, right_text: str) -> float:
    raise NotImplementedError("Semantic similarity will be implemented in a later phase.")


def retrieve_brand_guidelines(brand_id: str) -> list[dict[str, Any]]:
    raise NotImplementedError("Brand guideline retrieval will be implemented in a later phase.")


def generate_match_explanation(match_context: Mapping[str, Any]) -> str:
    raise NotImplementedError("Match explanation generation will be implemented in a later phase.")


def generate_collaboration_proposal(proposal_context: Mapping[str, Any]) -> str:
    raise NotImplementedError("Proposal generation will be implemented in a later phase.")
