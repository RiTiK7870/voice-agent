from app.config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT,
)


def mock_generate(question, context):
    if not context.strip():
        return {
            "answer": (
                "I don't have enough information in my knowledge base "
                "to answer that accurately. I can transfer you to a human agent."
            ),
            "escalated": True,
        }

    knowledge = []

    for block in context.split("\n\n---\n\n"):
        lines = block.splitlines()

        source = ""
        content_lines = []

        for line in lines:
            line = line.strip()

            if not line:
                continue

            if line.startswith("Source:"):
                source = line.replace("Source:", "").strip()

            elif line.startswith("Content:"):
                content = line.replace("Content:", "").strip()

                if content:
                    content_lines.append(content)

            else:
                content_lines.append(line)

        content = " ".join(content_lines).strip()

        # Remove document headings
        for heading in [
            "REFUND POLICY",
            "SUPPORT POLICY",
            "PRODUCT FAQ",
        ]:
            if content.upper().startswith(heading):
                content = content[len(heading):].strip()

        if content:
            knowledge.append({
                "source": source,
                "content": content,
            })

    if not knowledge:
        return {
            "answer": (
                "I found relevant information, but I could not "
                "reliably generate an answer from the knowledge base."
            ),
            "escalated": True,
        }

    question_lower = question.lower()

    # --------------------------------
    # Refund policy
    # --------------------------------
    if "refund" in question_lower:

        if "30 days" in " ".join(
            item["content"] for item in knowledge
        ):
            return {
                "answer": (
                    "Customers can request a refund within 30 days "
                    "of purchase, subject to eligibility. You will "
                    "need to provide your order or account reference."
                ),
                "escalated": False,
            }

    # --------------------------------
    # Human agent request
    # --------------------------------
    human_keywords = [
        "human",
        "agent",
        "representative",
        "person",
        "talk to someone",
        "speak to someone",
    ]

    if any(keyword in question_lower for keyword in human_keywords):
        return {
            "answer": (
                "Sure. I'll connect you with a human support agent."
            ),
            "escalated": True,
        }

    # --------------------------------
    # Fallback
    # --------------------------------
    return {
        "answer": (
            "I found relevant information in the knowledge base, "
            "but I don't have enough information to answer your "
            "question reliably. I can connect you with a human agent."
        ),
        "escalated": True,
    }


def generate(
    system_prompt: str,
    question: str,
    context: str,
):
    """
    LLM provider abstraction.

    mock:
        Local deterministic POC.

    openai:
        OpenAI API.

    azure_openai:
        Azure OpenAI / TCS-approved Azure deployment.
    """

    if LLM_PROVIDER == "mock":
        return mock_generate(question, context)

    if LLM_PROVIDER == "openai":
        return generate_openai(
            system_prompt,
            question,
            context,
        )

    if LLM_PROVIDER == "azure_openai":
        return generate_azure_openai(
            system_prompt,
            question,
            context,
        )

    raise RuntimeError(
        f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}"
    )


def generate_openai(
    system_prompt: str,
    question: str,
    context: str,
):
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    from openai import OpenAI

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": (
                    f"Knowledge base context:\n\n"
                    f"{context}\n\n"
                    f"Customer question:\n"
                    f"{question}"
                ),
            },
        ],
        temperature=0.1,
    )

    answer = response.choices[0].message.content.strip()

    return {
        "answer": answer,
        "escalated": False,
    }


def generate_azure_openai(
    system_prompt: str,
    question: str,
    context: str,
):
    if not AZURE_OPENAI_API_KEY:
        raise RuntimeError(
            "AZURE_OPENAI_API_KEY is not configured."
        )

    if not AZURE_OPENAI_ENDPOINT:
        raise RuntimeError(
            "AZURE_OPENAI_ENDPOINT is not configured."
        )

    if not AZURE_OPENAI_DEPLOYMENT:
        raise RuntimeError(
            "AZURE_OPENAI_DEPLOYMENT is not configured."
        )

    from openai import AzureOpenAI

    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
    )

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": (
                    f"Knowledge base context:\n\n"
                    f"{context}\n\n"
                    f"Customer question:\n"
                    f"{question}"
                ),
            },
        ],
        temperature=0.1,
    )

    answer = response.choices[0].message.content.strip()

    return {
        "answer": answer,
        "escalated": False,
    }