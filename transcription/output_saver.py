from __future__ import annotations
import abc
from enum import Enum
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from tools.registry_pattern import Registry
from tools.logging import setup_logging
from transcription.transcription import TranscriptionOutput, TranscriptionSegment


setup_logging()


class OutputSaver(abc.ABC):
    """Base class for output savers
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        logging.debug(f'Initializing {type(self)} output saver')

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


@OutputSaverRegistry.register
class CroquisOutputSaver(OutputSaver):
    """Save the transcription output to Croquis dataset format.

    Args:
        dataset_name (str): Dataset name, this is the speaker name.
        mode (Union[Mode, str], optional): Writing mode. Defaults to Mode.APPEND.
    """

    class Mode(str, Enum):
        """Mode of the output saver
        """
        WRITE = 'WRITE'
        APPEND = 'APPEND'

    DATASET_TRANSCRIPTIONS_FILENAME = 'metadata.txt'

    def __init__(self, dataset_name: str, mode: Union[Mode, str] = Mode.APPEND, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Dataset speaker name
        self.dataset_name = dataset_name

        # Writing mode
        if isinstance(mode, self.Mode):
            self.mode = mode
        elif isinstance(mode, str):
            self.mode = self.Mode(mode)
        else:
            raise ValueError(f'Invalid mode: {mode}')

    def _to_croquis_format(self, transcription: TranscriptionOutput) -> Dict[str, TranscriptionSegment]:
        """Convert the transcription output to Croquis format. This include selecting and merging
        the audio crops, and creating the transcription metadata.

        Args:
            transcription (TranscriptionOutput): Transcription output

        Returns:
            Dict[str, TranscriptionSegment]: Transcription crops, indexed by '{audio source}_{crop id}'
        """
        return {}

    def _save_audio_crops(self, audio_path: Union[Path, str], audios_crops: Dict[str, TranscriptionSegment], dataset_dir: Path) -> None:
        """Save the audio crops to the dataset folder as wav files.

        Args:
            audio_path (Union[Path, str]): Path to the source audio file
            audios_crops (Dict[str, TranscriptionSegment]): Transcription crops, indexed by '{audio source}_{crop id}'
            dataset_dir (Path): Path to the dataset folder
        """
        ...

    def _save_transcription(self, audios_crops: Dict[str, TranscriptionSegment], dataset_dir: Path) -> None:
        """Save the transcription metadata to the dataset folder.

        Args:
            audios_crops (Dict[str, TranscriptionSegment]): Transcription crops, indexed by '{audio source}_{crop id}'
            dataset_dir (Path): Path to the dataset folder
        """
        ...

    def save(self, transcription: TranscriptionOutput, output_dir: Optional[Path]) -> None:
        """Save the transcription output

        Args:
            transcription (TranscriptionOutput): Transcription output
            output_dir (Optional[Path]): Output directory
        """
        # Check if output folder exists, if not create it
        output_dir = output_dir or Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)

        # Check if dataset folder exists, if not create it
        dataset_dir = output_dir / self.dataset_name
        # if exists, and mode is WRITE, delete the folder and create it
        if self.mode == self.Mode.WRITE and dataset_dir.exists():
            logging.warning(f'Deleting dataset folder: {dataset_dir}')
            for f in dataset_dir.iterdir():
                f.unlink()
        # if exists, and mode is APPEND, do nothing
        logging.debug(f'Creating dataset folder: {dataset_dir}')
        dataset_dir.mkdir(parents=True, exist_ok=True)

        # Copy the audio file to the dataset folder if it doesn't exist
        audio_path = dataset_dir / transcription.audio_path.name
        if not audio_path.exists():
            logging.debug(f'Copying audio file to dataset folder: {audio_path}')
            transcription.audio_path.rename(audio_path)

        # Format the transcription to a Croquis dataset format
        audios_crops = self._to_croquis_format(transcription)

        # Create the audio crops
        self._save_audio_crops(transcription.audio_path, audios_crops, dataset_dir)

        # Create the transcription file if it doesn't exist
        self._save_transcription(audios_crops, dataset_dir)
