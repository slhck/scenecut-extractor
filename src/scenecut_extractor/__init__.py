import importlib.metadata

from ._scenecut_extractor import ScenecutExtractor, ScenecutInfo

__version__ = importlib.metadata.version("scenecut_extractor")

__all__ = ["ScenecutExtractor", "ScenecutInfo"]
