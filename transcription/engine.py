from __future__ import annotations
import abc
from pathlib import Path
from typing import Dict, List


class EngineRegistry:

    __engines : Dict[str, Engine] = {}

    @staticmethod
    def register(engine_class: Engine) -> None:
        """This decorator registers an engine in the registry.

        Args:
            engine (Engine): Engine to register
        """
        engine_name = engine_class.get_name()
        if engine_name in EngineRegistry.__engines:
            raise ValueError(f'Engine {engine_class.__name__} already registered')
        EngineRegistry.__engines[engine_name] = engine_class

    @staticmethod
    def list_available_engines() -> List[str]:
        """Return a list of available transcription engines

        Returns:
            List[str]: List of available transcription engines
        """
        return list(EngineRegistry.__engines.keys())

    @staticmethod
    def build_engine(engine_name: str) -> Engine:
        """Build an engine from the registry

        Args:
            engine_name (str): Name of the engine to build

        Raises:
            ValueError: If engine is not registered

        Returns:
            Engine: Engine instance
        """
        if engine_name not in EngineRegistry.__engines:
            raise ValueError(f'Engine {engine_name} not registered')
        return EngineRegistry.__engines[engine_name]()



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
        language = 'en',
        return language