from __future__ import annotations
import abc
import dataclasses
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from transcription.engine import Engine


@dataclasses.dataclass
class TranscriptionOutput:
    audio_path: Union[Path, str]
    engine: str
    language: str
    transcription: str

    def to_dict(self):
        return dataclasses.asdict(self)

    def to_json(self):
        data = self.to_dict()
        data['audio_path'] = str(data['audio_path'])
        return json.dumps(data)


class TranscriptionPipelineRegistry:

    __pipelines : Dict[str, Engine] = {}

    @staticmethod
    def register(transcription_pipeline_class: Engine) -> None:
        """This decorator registers an transcription pipeline in the registry.

        Args:
            transcription_pipeline_class (TranscriptionPipeline): Transcription pipeline to register
        """
        name = transcription_pipeline_class.__name__
        if name in TranscriptionPipelineRegistry.__pipelines:
            raise ValueError(f'Transcription Pipelien {transcription_pipeline_class.__name__} already registered')
        TranscriptionPipelineRegistry.__pipelines[name] = transcription_pipeline_class

    @staticmethod
    def list_available_transcription_pipelines() -> List[str]:
        """Return a list of available transcription pipelines

        Returns:
            List[str]: List of available transcription pipelines
        """
        return list(TranscriptionPipelineRegistry.__pipelines.keys())

    @staticmethod
    def build_transcription_pipeline(transcription_pipeline_name: str, engine: Engine) -> TranscriptionPipeline:
        """Build an engine from the registry

        Args:
            transcription_pipeline_name (str): Name of the transcription pipeline to build

        Raises:
            ValueError: If transcription pipeline is not registered

        Returns:
            TranscriptionPipeline: Transcription pipeline instance
        """
        if transcription_pipeline_name not in TranscriptionPipelineRegistry.__pipelines:
            raise ValueError(f'Transcription Pipeline {transcription_pipeline_name} not registered')
        return TranscriptionPipelineRegistry.__pipelines[transcription_pipeline_name](engine=engine)


class TranscriptionPipeline(abc.ABC):

    def __init__(self, engine: Engine) -> None:
        super().__init__()
        self.engine = engine

    @abc.abstractmethod
    def check_audio(self, audio_path: Path) -> bool:
        """Check if audio file is valid.

        Args:
            audio_path (Path): Path to audio file

        Returns:
            bool: True if audio file is valid, False otherwise
        """
        ...

    @abc.abstractmethod
    def process(self, audio_path: Path) -> TranscriptionOutput:
        """Process the audio file and return the transcription output

        Args:
            audio_path (Path): Path to audio file

        Returns:
            TranscriptionOutput: Transcription output
        """
        ...

    @abc.abstractmethod
    def save_output(self, transcription: TranscriptionOutput, output_dir: Optional[Path] = None) -> None:
        """Save the output to a file. 

        Args:
            transcription (TranscriptionOutput): Transcription output
            output_dir (Optional[Path], optional): Output directory. Defaults to None, which won't save it.
        """
        ...

    def __call__(self, audio_path: Path, output_dir: Optional[Path] = None) -> TranscriptionOutput:
        """Process the audio file and return the transcription output

        Args:
            audio_path (Path): Path to audio file
            output_dir (Optional[Path], optional): Output directory. Defaults to None, which won't save it.

        Raises:
            ValueError: If audio file is invalid

        Returns:
            TranscriptionOutput: Transcription output
        """
        is_valid = self.check_audio(audio_path)
        if not is_valid:
            raise ValueError(f'Invalid audio file {audio_path}')
        output = self.process(audio_path)
        self.save_output(output, output_dir)
        return output


@TranscriptionPipelineRegistry.register
class BasicTranscriptionPipeline(TranscriptionPipeline):

    def check_audio(self, audio_path: Path) -> bool:
        """Check if audio file is valid. This can include checking if the file exists, or if an url, etc.

        Args:
            audio_path (Path): Path to audio file

        Returns:
            bool: True if audio file is valid, False otherwise
        """
        logging.debug(f'Checking if audio file {audio_path} is valid')
        if not audio_path.exists():
            logging.error(f'Audio file {audio_path} does not exist')
            return False
        logging.debug(f'Audio file {audio_path} is valid')
        return True

    def process(self, audio_path: Path) -> TranscriptionOutput:
        """Process the audio file and return the transcription output

        Args:
            audio_path (Path): Path to audio file

        Returns:
            TranscriptionOutput: Transcription output
        """
        logging.debug(f'Processing audio file {audio_path}')
        transcription = TranscriptionOutput(
            audio_path=audio_path,
            engine=self.engine.get_name(),
            transcription=self.engine.transcribe(audio_path),
            language=self.engine.language(audio_path) 
        )
        return transcription

    def save_output(self, transcription: TranscriptionOutput, output_dir: Optional[Path] = None) -> None:
        """Save the output to a file. 

        Args:
            transcription (TranscriptionOutput): Transcription output.
            output_dir (Optional[Path], optional): Output directory. Defaults to None, which won't save it.
        """
        logging.debug(f'Saving output for audio file {transcription.audio_path}')
        if output_dir is None:
            logging.debug('No output directory specified, not saving output')
            return
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f'{transcription.audio_path.stem}.json'
        with open(output_path, 'w') as f:
            f.write(transcription.to_json())
