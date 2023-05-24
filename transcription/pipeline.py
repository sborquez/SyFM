from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional

from transcription.transcription import TranscriptionOutput
from transcription.engine import Engine, EngineRegistry
from transcription.audio_validator import AudioValidator, AudioValidatorRegistry
from transcription.output_saver import OutputSaver, OutputSaverRegistry


def build_transcription_pipeline(engine_name: str,
                                 engine_build_arguments: dict = {}, 
                                 audio_validator_name: str = 'BasicAudioValidator',
                                 audio_validator_arguments: dict = {}, 
                                 output_saver_name: str = 'BasicOutputSaver',
                                 output_saver_build_arguments: dict = {}, 
                                 ) -> TranscriptionPipeline:
    """Build an engine from the registry

    Args:
        engine_name (str): Engine name
        engine_build_arguments (dict, optional): Engine build arguments. Defaults to {}.
        audio_validator_name (str): Audio validator name
        audio_validator_arguments (dict, optional): Audio validator build arguments. Defaults to {}.
        output_saver_name (str): Output saver name
        output_saver_build_arguments (dict, optional): Output saver build arguments. Defaults to {}.

    Raises:
        ValueError: If transcription pipeline is not registered

    Returns:
        TranscriptionPipeline: Transcription pipeline instance
    """
    engine = EngineRegistry.build(engine_name, engine_build_arguments)
    audio_validator = AudioValidatorRegistry.build(audio_validator_name, audio_validator_arguments)
    output_saver = OutputSaverRegistry.build(output_saver_name, output_saver_build_arguments)
    pipeline = TranscriptionPipeline(
        audio_validator=audio_validator,
        engine=engine,
        output_saver=output_saver,
    )
    return pipeline


class TranscriptionPipeline:

    def __init__(self, audio_validator: AudioValidator, engine: Engine, output_saver: OutputSaver) -> None:
        super().__init__()
        self.audio_validator = audio_validator
        self.engine = engine
        self.output_saver = output_saver

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
        is_valid = self.load_audio(audio_path)
        if not is_valid:
            raise ValueError(f'Invalid audio file {audio_path}')
        output = self.process(audio_path)
        self.save_output(output, output_dir)
        return output


    def load_audio(self, audio_path: Path) -> bool:
        """Check if audio file is valid. This can include checking if the file exists, or if an url, etc.

        Args:
            audio_path (Path): Path to audio file

        Returns:
            bool: True if audio file is valid, False otherwise
        """
        logging.debug(f'Checking if audio file {audio_path} is valid')
        audio_path, is_valid = self.audio_validator.check(audio_path)
        if not is_valid:
            logging.error(f'Audio file {audio_path} does not exist')
            return audio_path, is_valid
        logging.debug(f'Audio file {audio_path} is valid')
        return audio_path, is_valid

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
        self.output_saver.save(transcription, output_dir)
