import pytest


@pytest.mark.vcr
def test_chat(exporter, openai_client, vcr):
    openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Tell me a joke about opentelemetry"}],
    )

    spans = exporter.get_finished_spans()

    assert [span.name for span in spans] == [
        "openai.chat",
    ]
    open_ai_span = spans[0]
    assert (
        open_ai_span.attributes["llm.prompts.0.content"]
        == "Tell me a joke about opentelemetry"
    )
    assert open_ai_span.attributes.get("llm.completions.0.content")
    assert (
        open_ai_span.attributes.get("openai.api_base") == "https://api.openai.com/v1/"
    )
    assert open_ai_span.attributes.get("llm.is_streaming") is False


@pytest.mark.vcr
def test_chat_streaming(exporter, openai_client, vcr):
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Tell me a joke about opentelemetry"}],
        stream=True,
    )

    chunk_count = 0
    for _ in response:
        chunk_count += 1

    spans = exporter.get_finished_spans()

    assert [span.name for span in spans] == [
        "openai.chat",
    ]
    open_ai_span = spans[0]
    assert (
        open_ai_span.attributes["llm.prompts.0.content"]
        == "Tell me a joke about opentelemetry"
    )
    assert open_ai_span.attributes.get("llm.completions.0.content")
    assert (
        open_ai_span.attributes.get("openai.api_base") == "https://api.openai.com/v1/"
    )
    assert open_ai_span.attributes.get("llm.is_streaming") is True

    events = open_ai_span.events
    assert len(events) == chunk_count
