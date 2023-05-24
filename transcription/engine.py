from __future__ import annotations
import abc
from pathlib import Path
from typing import Dict, List

from tools.registry_pattern import Registry


class Engine(abc.ABC):
    """Base class for transcription engines
    """

    @staticmethod
    @abc.abstractmethod
    def get_name() -> str:
        """Return the name of the engine

        Returns:
            str: Name of the engine
        """
        ...

    @abc.abstractmethod
    def transcribe(self, audio_path: Path) -> str:
        """Transcribe an audio file

        Args:
            audio_path (Path): Path to audio file

        Returns:
            str: Transcription output
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

    @staticmethod
    def get_name() -> str:
        """Return the name of the engine

        Returns:
            str: Name of the engine
        """
        return 'dummy'

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe an audio file

        Args:
            audio_path (Path): Path to audio file

        Returns:
            str: Transcription output with dummy transcription
        """
        
        transcription='Hello world!'
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

    @staticmethod
    def get_name() -> str:
        """Return the name of the engine

        Returns:
            str: Name of the engine
        """
        return 'whisper'

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe an audio file

        Args:
            audio_path (Path): Path to audio file

        Returns:
            str: Transcription output with dummy transcription
        """
        
        transcription='Hello world!'
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
