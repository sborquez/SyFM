from __future__ import annotations
import abc
from pathlib import Path
from typing import Tuple

from tools.registry_pattern import Registry


class AudioValidator(abc.ABC):
    """Check if the audio loader can load the given audio file
    """

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
