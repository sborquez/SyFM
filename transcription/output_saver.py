from __future__ import annotations
import abc
from pathlib import Path
from typing import Optional

from tools.registry_pattern import Registry
from transcription.transcription import TranscriptionOutput


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


OutputSaverRegistry = Registry(OutputSaver)

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
