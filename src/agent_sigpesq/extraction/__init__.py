"""
PDF -> structured JSON extraction for SIGPESQ project files, using the Mistral API.

Pipeline: Mistral OCR (mistral-ocr-latest) turns each project PDF into markdown,
then a chat model (mistral-large-latest, JSON mode) fills the project schema.

`ProjectExtractor` is imported lazily so that `schema` (pure pydantic) can be used
without pulling in the optional `mistralai` dependency.
"""
from .schema import Projeto

__all__ = ["Projeto", "ProjectExtractor", "BatchProjectExtractor"]


def __getattr__(name):
    if name == "ProjectExtractor":
        from .mistral_extractor import ProjectExtractor
        return ProjectExtractor
    if name == "BatchProjectExtractor":
        from .batch_extractor import BatchProjectExtractor
        return BatchProjectExtractor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
