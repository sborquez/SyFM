from __future__ import annotations
import abc
import logging
from pathlib import Path
from typing import Any, Tuple

from tools.registry_pattern import Registry
from tools.logging import setup_logging


setup_logging()


class AudioValidator(abc.ABC):
    """Check if the audio loader can load the given audio file
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        logging.debug(f'Initializing {type(self)} audio validator')

    @abc.abstractmethod
    def check(self, audio_path: Path) -> Tuple[Path, bool]:
        """Check if the audio loader can load the given audio file

        Args:
            audio_path (Path): Path to the audio file

        Returns:
            Tuple[Path, bool]: Tuple containing the path to the audio file and
                a boolean indicating if the audio file can be loaded.
        """
        ...


AudioValidatorRegistry = Registry(AudioValidator)


@AudioValidatorRegistry.register
class BasicAudioValidator(AudioValidator):
    """Local Filesystem audio loader
    """

    def check(self, audio_path: Path) -> Tuple[Path, bool]:
        """Check if the audio loader can load the given audio file

        Args:
            audio_path (Path): Path to the audio file

        Returns:
            Tuple[Path, bool]: Tuple containing the path to the audio file and
                a boolean indicating if the audio file can be loaded.
        """
        is_valid = audio_path.exists()
        return audio_path, is_valid
