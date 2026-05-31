PROMPT_TEMPLATE = """
Create a high quality Christian illustration.

Topic:
{topic}

Style:
{style}

Requirements:
- respectful
- historically appropriate
- detailed
- realistic lighting
- educational
"""


def build_prompt(
    topic,
    style="realistic"
):

    return PROMPT_TEMPLATE.format(
        topic=topic,
        style=style
    )