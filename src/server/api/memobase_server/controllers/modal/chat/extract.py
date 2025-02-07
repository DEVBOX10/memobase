from ....env import CONFIG, LOG
from ....models.utils import Promise
from ....models.blob import Blob, BlobType
from ....models.response import AIUserProfiles, CODE
from ....llms import llm_complete
from ....prompts.utils import (
    tag_chat_blobs_in_order_xml,
    attribute_unify,
    parse_string_into_profiles,
)
from ....prompts.types import read_out_profile_config
from ...profile import get_user_profiles
from ...project import get_project_profile_config

# from ...project impor
from .types import FactResponse, PROMPTS


def merge_by_topic_sub_topics(new_facts: list[FactResponse]):
    topic_subtopic = {}
    for nf in new_facts:
        key = (nf["topic"], nf["sub_topic"])
        if key in topic_subtopic and isinstance(nf["memo"], str):
            topic_subtopic[key]["memo"] += f"; {nf['memo']}"
            continue
        topic_subtopic[key] = nf
    return list(topic_subtopic.values())


async def extract_topics(
    user_id: str, project_id: str, blob_ids: list[str], blobs: list[Blob]
) -> Promise[dict]:
    assert len(blob_ids) == len(blobs), "Length of blob_ids and blobs must be equal"
    assert all(b.type == BlobType.chat for b in blobs), "All blobs must be chat blobs"
    p = await get_user_profiles(user_id, project_id)
    if not p.ok():
        return p
    profiles = p.data().profiles
    p = await get_project_profile_config(project_id)
    if not p.ok():
        return p
    project_profiles = p.data()
    project_profiles_slots = read_out_profile_config(
        project_profiles, PROMPTS[CONFIG.language]["profile"].CANDIDATE_PROFILE_TOPICS
    )

    if len(profiles):
        already_topics_subtopics = sorted(
            set([(p.attributes["topic"], p.attributes["sub_topic"]) for p in profiles])
        )
        already_topics_prompt = "\n".join(
            [
                f"- {topic}{CONFIG.llm_tab_separator}{sub_topic}"
                for topic, sub_topic in already_topics_subtopics
            ]
        )
        LOG.info(
            f"User {user_id} already have {len(profiles)} profiles, {len(already_topics_subtopics)} topics"
        )
    else:
        already_topics_prompt = ""

    blob_strs = tag_chat_blobs_in_order_xml(blobs)
    p = await llm_complete(
        PROMPTS[CONFIG.language]["extract"].pack_input(
            already_topics_prompt,
            blob_strs,
            PROMPTS[CONFIG.language]["profile"].get_prompt(project_profiles_slots),
        ),
        system_prompt=PROMPTS[CONFIG.language]["extract"].get_prompt(),
        temperature=0.2,  # precise
        **PROMPTS[CONFIG.language]["extract"].get_kwargs(),
    )
    if not p.ok():
        return p
    results = p.data()
    parsed_facts: AIUserProfiles = parse_string_into_profiles(results)
    new_facts: list[FactResponse] = parsed_facts.model_dump()["facts"]
    if not len(new_facts):
        LOG.info(f"No new facts extracted {user_id}")
        return Promise.resolve(
            {
                "fact_contents": [],
                "fact_attributes": [],
                "profiles": profiles,
            }
        )

    for nf in new_facts:
        nf["topic"] = attribute_unify(nf["topic"])
        nf["sub_topic"] = attribute_unify(nf["sub_topic"])
    new_facts = merge_by_topic_sub_topics(new_facts)

    fact_contents = []
    fact_attributes = []

    for nf in new_facts:
        fact_contents.append(nf["memo"])
        fact_attributes.append(
            {
                "topic": nf["topic"],
                "sub_topic": nf["sub_topic"],
            }
        )
    return Promise.resolve(
        {
            "fact_contents": fact_contents,
            "fact_attributes": fact_attributes,
            "profiles": profiles,
        }
    )
