"""CloudflareCompatibleModel

A thin wrapper around any LangChain BaseChatModel that patches the outbound
HTTP payload so that message `content` is never `null` (None) — Cloudflare
Workers AI rejects `null` content even when `tool_calls` are present.

LangChain's OpenAI serializer explicitly sets `content` to `None` for
AIMessages that have tool calls (to match the OpenAI spec), but Cloudflare's
API gateway requires a string. This wrapper replaces `None` content with an
empty string `""` at the last possible point before the HTTP request is made.
"""
import logging
from typing import Any

from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


def _normalize_payload_messages(payload: dict) -> dict:
    """Replace None/null content with empty string in the messages payload."""
    messages = payload.get("messages")
    if not isinstance(messages, list):
        return payload
    patched = []
    for msg in messages:
        if isinstance(msg, dict) and msg.get("content") is None:
            msg = {**msg, "content": ""}
        patched.append(msg)
    payload = {**payload, "messages": patched}
    return payload


def make_cloudflare_compatible(model: BaseChatModel) -> BaseChatModel:
    """Wrap a chat model so its outbound payload has no null content fields.

    This patches `_get_request_payload` on the model instance (not the class)
    so only this specific instance is affected. It is safe to use alongside
    bind_tools / bind() because those return new bound models; the patch is
    applied to the base model before binding so subclasses also inherit it.

    Args:
        model: Any LangChain BaseChatModel instance.

    Returns:
        The same model instance with a patched `_get_request_payload` method.
    """
    if not hasattr(model, "_get_request_payload"):
        logger.warning(
            "Model %s does not have _get_request_payload; "
            "Cloudflare content-null patch skipped",
            type(model).__name__,
        )
        return model

    original_get_request_payload = model._get_request_payload

    def patched_get_request_payload(input_: Any, *, stop: Any = None, **kwargs: Any) -> dict:
        payload = original_get_request_payload(input_, stop=stop, **kwargs)
        payload = _normalize_payload_messages(payload)
        return payload

    model._get_request_payload = patched_get_request_payload
    logger.debug(
        "Applied Cloudflare content-null patch to model %s",
        type(model).__name__,
    )
    return model
