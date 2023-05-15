from __future__ import annotations
import abc
from pathlib import Path
from typing import Dict, List, Optional

from transcription.transcription import TranscriptionOutput


class OutputSaverRegistry:

    __output_saver : Dict[str, OutputSaver] = {}

    @staticmethod
    def register(class_: OutputSaver) -> None:
        """This decorator registers an output saver in the registry.

        Args:
            class_ (OutputSaver): OutputSaver to register
        """
        name = class_.__name__
        if name in OutputSaverRegistry.__output_saver:
            raise ValueError(f'OutputSaver {name} already registered')
        OutputSaverRegistry.__output_saver[name] = class_

    @staticmethod
    def list_available() -> List[str]:
        """Return a list of available output savers.

        Returns:
            List[str]: List of available output savers
        """
        return list(OutputSaverRegistry.__output_saver.keys())

    @staticmethod
    def build(name: str) -> OutputSaver:
        """Build an output saver from the registry

        Args:
            name (str): Name of the output saver to build

        Raises:
            ValueError: If output saver is not registered

        Returns:
            OutputSaver: OutputSaver instance
        """
        if name not in OutputSaverRegistry.__output_saver:
            raise ValueError(f'OutputSaver {name} not registered')
        return OutputSaverRegistry.__output_saver[name]()



class OutputSaver(abc.ABC):
    """Base class for output savers
    """

    @abc.abstractmethod
    def save(self, transcription: TranscriptionOutput, output_dir: Optional[Path]) -> None:
        """Save the transcription output

        Args:
            transcription (TranscriptionOutput): Transcription output
            output_dir (Optional[Path]): Output directory
        """
        ...


@OutputSaverRegistry.register
class BasicOutputSaver(OutputSaver):
    """Local Filesystem output 
    """

    def save(self, transcription: TranscriptionOutput, output_dir: Optional[Path]) -> None:
        """Save the transcription output

        Args:
            transcription (TranscriptionOutput): Transcription output
            output_dir (Optional[Path]): Output directory
        """
        output_dir = output_dir or Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f'{transcription.audio_path.stem}.json'
        with open(output_path, 'w') as f:
            f.write(transcription.to_json())
