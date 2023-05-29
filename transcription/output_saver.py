from __future__ import annotations
import abc
from enum import Enum
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydub import AudioSegment

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

    class Strategy(str, Enum):
        """Strategy of the output saver
        """
        # Do nothing, and crop the audio as is
        NOTHING = 'NOTHING'
        # Try to merge the segments following a silence threshold
        THRESHOLD = 'THRESHOLD'
        # Try to merge the segments following the normal distribution for the
        # length of the segments
        NORMAL = 'NORMAL'

    # Dataset folder structure
    DATASET_TRANSCRIPTIONS_FILENAME = 'metadata.txt'

    # Add padding to the audio crops
    PAD_MS = 200

    # Silence threshold in milliseconds
    SILENCE_THRESHOLD_MS = 500

    # Crop template, fill with 5 digits
    CROP_TEMPLATE = '{audio_source}_{crop_id:05d}'

    def __init__(self, dataset_name: str, mode: Union[Mode, str] = Mode.APPEND,
                 strategy: Union[Strategy, str] = Strategy.NOTHING, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Dataset speaker name
        self.dataset_name = dataset_name

        # Writing mode
        if isinstance(mode, self.Mode):
            self.mode = mode
        elif isinstance(mode, str):
            self.mode = self.Mode(mode.upper())
        else:
            raise ValueError(f'Invalid mode: {mode}')

        # Merge strategy
        if isinstance(strategy, self.Strategy):
            self.strategy = strategy
        elif isinstance(strategy, str):
            self.strategy = self.Strategy(strategy.upper())
        else:
            raise ValueError(f'Invalid strategy: {strategy}')

    def _to_croquis_format(self, transcription: TranscriptionOutput) -> Dict[str, TranscriptionSegment]:
        """Convert the transcription output to Croquis format. This include
        selecting and merging the audio crops, and creating the transcription
        metadata.

        Args:
            transcription (TranscriptionOutput): Transcription output

        Returns:
            Dict[str, TranscriptionSegment]: Transcription crops, indexed by '{audio source}_{crop id}'

        Raises:
            NotADirectoryError: Invalid strategy
        """
        if self.strategy == self.Strategy.NOTHING:
            logging.debug('Using NOTHING strategy')
            return self._do_nothing_strategy(transcription)
        elif self.strategy == self.Strategy.THRESHOLD:
            logging.debug('Using THRESHOLD strategy')
            return self._threshold_strategy(transcription)
        elif self.strategy == self.Strategy.NORMAL:
            logging.debug('Using NORMAL strategy')
            return self._normal_distribution_strategy(transcription)
        else:
            raise NotADirectoryError(f'Invalid strategy: {self.strategy}')

    def _do_nothing_strategy(self, transcription: TranscriptionOutput) -> Dict[str, TranscriptionSegment]:
        """Do nothing, and crop the audio as is.

        Args:
            transcription (TranscriptionOutput): Transcription output

        Returns:
            Dict[str, TranscriptionSegment]: Transcription crops, indexed by '{audio_source}_{crop_id}'
        """
        crops = {}
        for idx, segment in enumerate(transcription):
            crop_idx = self.CROP_TEMPLATE.format(audio_source=transcription.audio_path.stem, crop_id=idx)
            crops[crop_idx] = segment
        return crops

    def _threshold_strategy(self, transcription: TranscriptionOutput) -> Dict[str, TranscriptionSegment]:
        """Try to merge the segments following a silence threshold.

        Args:
            transcription (TranscriptionOutput): Transcription output

        Returns:
            Dict[str, TranscriptionSegment]: Transcription crops, indexed by '{audio_source}_{crop_id}'
        """
        crops = {}
        idx = 0
        current_guesses = []
        for segment in transcription:
            if len(current_guesses) == 0:
                # No current guess, create a new one
                current_guesses.append(segment)
                continue
            # Compute silence duration between the current guess and the new segment
            silence_duration = segment.start_ms - current_guesses[-1].end_ms
            if silence_duration <= self.SILENCE_THRESHOLD_MS:
                # Add the segment to the current guess
                current_guesses.append(segment)
                continue
            # Silence duration is too long, save the current guess
            crop_idx = self.CROP_TEMPLATE.format(audio_source=transcription.audio_path.stem, crop_id=idx)
            idx += 1
            merged_segment = TranscriptionSegment.merge(current_guesses)
            crops[crop_idx] = merged_segment
            # and create a new one
            current_guesses = [segment]
        # Save the last guess
        crop_idx = self.CROP_TEMPLATE.format(audio_source=transcription.audio_path.stem, crop_id=idx)
        merged_segment = TranscriptionSegment.merge(current_guesses)
        crops[crop_idx] = merged_segment
        return crops

    def _normal_distribution_strategy(self, transcription: TranscriptionOutput) -> Dict[str, TranscriptionSegment]:
        raise NotImplementedError()

    def _save_audio_crops(self, audio_path: Union[Path, str], audios_crops: Dict[str, TranscriptionSegment], dataset_dir: Union[Path, str]) -> None:
        """Save the audio crops to the dataset folder as wav files.

        Args:
            audio_path (Union[Path, str]): Path to the source audio file
            audios_crops (Dict[str, TranscriptionSegment]): Transcription crops, indexed by '{audio source}_{crop id}'
            dataset_dir (Union[Path, str]): Path to the dataset folder
        """
        dataset_dir = Path(dataset_dir)
        logging.debug(f'Saving audio crops to {dataset_dir}')
        audio_path = Path(audio_path)
        extension = audio_path.suffix
        audio = AudioSegment.from_file(audio_path, extension[1:])
        for crop_idx, segment in audios_crops.items():
            crop_path = dataset_dir / f'{crop_idx}{extension}'
            start_ms = max(0, segment.start_ms - self.PAD_MS)
            end_ms = min(segment.end_ms + self.PAD_MS, len(audio))
            audio_segment = audio[start_ms:end_ms]
            audio_segment.export(crop_path, format=extension[1:])
            logging.debug(f'Saved {crop_path}')

    def _save_transcription(self, audios_crops: Dict[str, TranscriptionSegment], dataset_dir: Union[Path, str]) -> None:
        """Save the transcription metadata to the dataset folder.

        Args:
            audios_crops (Dict[str, TranscriptionSegment]): Transcription crops, indexed by '{audio source}_{crop id}'
            dataset_dir (Union[Path, str]): Path to the dataset folder
        """
        dataset_dir = Path(dataset_dir)
        logging.debug(f'Saving transcription metadata to {dataset_dir / self.DATASET_TRANSCRIPTIONS_FILENAME}')
        with open(dataset_dir / self.DATASET_TRANSCRIPTIONS_FILENAME, 'a') as f:
            for crop_idx, segment in audios_crops.items():
                f.write(f'{crop_idx}|{segment.text.strip()}\n')

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


if __name__ == '__main__':
    transcription_filepath = '/home/asuka/projects/youtube/fran_voice/output/transcription/chernobil.json'
    dataset_dir = '/home/asuka/projects/youtube/fran_voice/output/croquis'
    transcription = TranscriptionOutput.from_json(transcription_filepath)
    croquis = CroquisOutputSaver(dataset_name='chernobil', mode='append', strategy='nothing')
    # crops = croquis._do_nothing_strategy(transcription)
    crops = croquis._threshold_strategy(transcription)
    # crops = croquis._normal_distribution_strategy(transcription)
    croquis._save_audio_crops(transcription.audio_path, crops, dataset_dir)
    croquis._save_transcription(crops, dataset_dir)
