
# "If entity contains \" or \' use escape character marking!"
def extract_entities_prompt(text):
    prompt = (
        "Identify all entities in the following text."
        "These entities will serve as node labels in a knowledge graph."
        "Provide the entities as a comma-separated list, excluding articles such as 'the,' 'a,' or 'an.' "
        'Format the list as: "entity 1", "entity 2", etc. '
        f"Text: {text}"
    )
    return prompt


def extract_entities_and_relationships_prompt_level2(text, entities):
    prompt = (
        "Extract entity types and the relationships between entities from the following text to create a knowledge graph.\n\n"
        "Instructions:\n"
        "1. Entities:\n"
        f"  - Here is a list of entities you must focus on. Entity List: {entities}"
        "   - For each entity from the list assign a unique positive ID, starting from 0.\n"
        "   - Identify a broader category that aggregates similar entities\n"
        "   - you can slightly refine entities based on the text\n"
        "2. Relationships:\n"
        "   - Identify relationships between entities.\n"
        "   - Use a single, domain-specific word in active voice for the relationship\n"
        "   - Avoid passive terms like 'is employed by' in favor of 'employs'\n"
        "   - Source and target IDs should reflect the correct direction of the relationship, because we generate directional graph!\n"
        "   - Ensure correct source and target IDs.\n"
        "3. Output Format:\n"
        "   - Provide two CSV tables: one for nodes and one for edges.\n"
        "   - Do not include any text outside the CSV tables.\n"
        "   - Use proper CSV formatting with headers, commas, and quotation marks.\n\n"
        "Example Output (for text about Alice who works at Acme Corp located in Wonderland):\n"
        "# Entities CSV\n"
        "id,entity,category\n"
        "0,\"Alice\",\"Person\"\n"
        "1,\"Acme Corp\",\"Organization\"\n"
        "2,\"Wonderland\",\"Location\"\n\n"
        "# Relationships CSV\n"
        "source,target,relationship\n"
        "0,1,\"works_at\"\n"
        "1,2,\"located_in\"\n\n"
        "Text to Analyze:\n"
        f"```\n{text}\n```\n"
    )

    return prompt


def extract_entities_and_relationships_prompt_level0(text):
    prompt = (
        "Extract entity types and the relationships between entities from the following text to create a knowledge graph.\n\n"
        "Instructions:\n"
        "1. Entities:\n"
        f"  - Identify all entities in the following text.\n"
        "   - These entities will serve as node labels in a knowledge graph.\n"
        "   - Excluding articles such as 'the,' 'a,' or 'an.'\n"
        "   - For each entity from assign a unique positive ID, starting from 0.\n"
        "   - Identify a broader category that aggregates similar entities\n"
        "2. Relationships:\n"
        "   - Identify relationships between entities.\n"
        "   - Use a single, domain-specific word in active voice for the relationship\n"
        "   - Avoid passive terms like 'is employed by' in favor of 'employs'\n"
        "   - Source and target IDs should reflect the correct direction of the relationship, because we generate directional graph!\n"
        "   - Ensure correct source and target IDs.\n"
        "3. Output Format:\n"
        "   - Provide two CSV tables: one for nodes and one for edges.\n"
        "   - Do not include any text outside the CSV tables.\n"
        "   - Use proper CSV formatting with headers, commas, and quotation marks.\n\n"
        "Example Output (for text about Alice who works at Acme Corp located in Wonderland):\n"
        "# Entities CSV\n"
        "id,entity,category\n"
        "0,\"Alice\",\"Person\"\n"
        "1,\"Acme Corp\",\"Organization\"\n"
        "2,\"Wonderland\",\"Location\"\n\n"
        "# Relationships CSV\n"
        "source,target,relationship\n"
        "0,1,\"works_at\"\n"
        "1,2,\"located_in\"\n\n"
        "Text to Analyze:\n"
        f"```\n{text}\n```\n"
    )

    return prompt