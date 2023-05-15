from __future__ import annotations
import abc
from pathlib import Path
from typing import Dict, List, Tuple


class AudioLoaderRegistry:

    __audio_loaders : Dict[str, AudioLoader] = {}

    @staticmethod
    def register(class_: AudioLoader) -> None:
        """This decorator registers an audio loader in the registry.

        Args:
            class_ (AudioLoader): AudioLoader to register
        """
        name = class_.__name__
        if name in AudioLoaderRegistry.__audio_loaders:
            raise ValueError(f'AudioLoader {name} already registered')
        AudioLoaderRegistry.__audio_loaders[name] = class_

    @staticmethod
    def list_available() -> List[str]:
        """Return a list of available audio loaders.

        Returns:
            List[str]: List of available audio loaders
        """
        return list(AudioLoaderRegistry.__audio_loaders.keys())

    @staticmethod
    def build(name: str) -> AudioLoader:
        """Build an audio loader from the registry

        Args:
            name (str): Name of the audio loader to build

        Raises:
            ValueError: If audio loader is not registered

        Returns:
            AudioLoader: AudioLoader instance
        """
        if name not in AudioLoaderRegistry.__audio_loaders:
            raise ValueError(f'AudioLoader {name} not registered')
        return AudioLoaderRegistry.__audio_loaders[name]()



class AudioLoader(abc.ABC):
    """Base class for audio loaders
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

@AudioLoaderRegistry.register
class BasicAudioLoader(AudioLoader):
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
