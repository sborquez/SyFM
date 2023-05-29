from __future__ import annotations
import abc
import logging
from pathlib import Path
from typing import Any, List, Optional, Tuple

import whisper
import stable_whisper

from tools.registry_pattern import Registry
from tools.logging import setup_logging
from transcription.transcription import TranscriptionSegment


setup_logging()


class Engine(abc.ABC):
    """Base class for transcription engines
    """

    name = 'base'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        logging.debug(f'Initializing {self.get_name()} engine')

    @classmethod
    def get_name(cls) -> str:
        """Return the name of the engine

        Returns:
            str: Name of the engine
        """
        return cls.name

    @abc.abstractmethod
    def transcribe(self, audio_path: Path) -> List[TranscriptionSegment]:
        """Transcribe an audio file

        Args:
            audio_path (Path): Path to audio file

        Returns:
            List[TranscriptionSegment]: Transcription output
        """
        ...

    @abc.abstractmethod
    def language(self, audio_path: Path) -> str:
        """Detect the language of an audio file

        Args:
            audio_path (Path): Path to audio file

        Returns:
            str: Language code
        """
        ...


EngineRegistry: Registry = Registry(Engine)


@EngineRegistry.register
class GreetingsEngine(Engine):
    """Greetings engine, for testing the transcription pipeline
    """

    name = 'dummy'

    def transcribe(self, audio_path: Path) -> List[TranscriptionSegment]:
        """Transcribe an audio file

        Args:
            audio_path (Path): Path to audio file

        Returns:
            List[TranscriptionSegment]: Transcription output with dummy transcription
        """
        transcription_text = 'Hello world!'
        transcription = [
            TranscriptionSegment(
                start_ms=0,
                end_ms=-1,
                text=transcription_text
            )
        ]
        return transcription

    def language(self, audio_path: Path) -> str:
        """Detect the language of an audio file

        Args:
            audio_path (Path): Path to audio file

        Returns:
            str: Language code
        """
        language = 'en'
        return language


@EngineRegistry.register
class WhisperEngine(Engine):
    """Whisper engine, for transcribing with the OpenAI whispers model,
    running locally
    """

    name = 'whisper'

    def __init__(self, model: str = 'medium', language: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._model = self._load_model(model)
        self._language = language

    def _load_model(self, model: str = 'medium') -> Any:
        """Load the model

        Args:
            model (str, optional): Model name. Defaults to 'medium'.

        Returns:
            Any: Model
        """
        return whisper.load_model(model)

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe an audio file

        Args:
            audio_path (Path): Path to audio file

        Returns:
            str: Transcription output with dummy transcription
        """
        audio_path = str(audio_path)
        models_transcription = self._model.transcribe(audio_path, language=self._language)
        transcription, language = self._postprocess(models_transcription)
        return transcription

    def _postprocess(self, models_transcription: Any) -> Tuple[List[TranscriptionSegment], str]:
        """Generate a transcription output from the model output

        Args:
            models_transcription (Any): Model output

        Returns:
            List[TranscriptionSegment]: A formatted transcription output
            str: Language code
        """
        transcription = []
        for segment in models_transcription['segments']:
            transcription.append(
                TranscriptionSegment(
                    start_ms=int(segment['start'] * 1000),
                    end_ms=int(segment['end'] * 1000),
                    text=segment['text']
                )
            )
        if self._language is None:
            self._language = models_transcription['language']
        language = self._language
        return transcription, language

    def language(self, audio_path: Path) -> str:
        """Detect the language of an audio file

        Args:
            audio_path (Path): Path to audio file

        Returns:
            str: Language code
        """
        if self._language is None:
            self._language = self.model.language(audio_path)
        return self._language


@EngineRegistry.register
class StableWhisperEngine(WhisperEngine):
    """Stable Whisper engine, for transcribing with the OpenAI whispers model,
    improved with more accurated timestamps, it runs locally.
    """

    name = 'stable_whisper'

    def _load_model(self, model: str = 'medium') -> Any:
        """Load the model

        Args:
            model (str, optional): Model name. Defaults to 'medium'.

        Returns:
            Any: Model
        """
        return stable_whisper.load_model(model)

    def _postprocess(self, models_transcription: Any) -> Tuple[List[TranscriptionSegment], str]:
        """Generate a transcription output from the model output

        Args:
            models_transcription (Any): Model output

        Returns:
            List[TranscriptionSegment]: A formatted transcription output
            str: Language code
        """
        transcription = []
        for segment in models_transcription.segments:
            transcription.append(
                TranscriptionSegment(
                    start_ms=int(segment.start * 1000),
                    end_ms=int(segment.end * 1000),
                    text=segment.text
                )
            )
        if self._language is None:
            self._language = models_transcription.language
        language = self._language
        return transcription, language
