from pathlib import Path
from typing import Any, Optional

from transcription.audio_validator import AudioValidatorRegistry
from transcription.engine import EngineRegistry
from transcription.output_saver import OutputSaverRegistry
from transcription.pipeline import build_transcription_pipeline, TranscriptionOutput


def translation_pipeline(audio_path: Path,
                         audio_validator_name: str = 'BasicAudioValidator',
                         engine_name: str = 'StableWhisperEngine',
                         output_saver_name: str = 'CroquisOutputSaver',
                         output_dir: Optional[Path] = None,
                         **kwargs: Any) -> TranscriptionOutput:
    pipeline = build_transcription_pipeline(
        engine_name=engine_name, engine_build_arguments=kwargs,
        audio_validator_name=audio_validator_name, audio_validator_arguments=kwargs,
        output_saver_name=output_saver_name, output_saver_build_arguments=kwargs,
    )
    transcription = pipeline(audio_path, output_dir=output_dir)
    return transcription


if __name__ == '__main__':
    import argparse
    import logging
    from tools.logging import setup_logging

    available_engines = EngineRegistry.list_availables()
    available_audio_validators = AudioValidatorRegistry.list_availables()
    available_output_savers = OutputSaverRegistry.list_availables()

    arg_parser = argparse.ArgumentParser(description='Transcribe audio files')
    arg_parser.add_argument('--audio_path', type=str, metavar='path_to_audio',
                            help='Path to audio file or directory of audio files')
    arg_parser.add_argument('--audio_validator_name', type=str, metavar='AUDIO_VALIDATOR',
                            help='Audio validator to use',
                            choices=available_audio_validators,
                            default=available_audio_validators[0])
    arg_parser.add_argument('--engine_name', type=str, metavar='ENGINE',
                            help='Transcription engine to use',
                            choices=available_engines,
                            default=available_engines[0])
    arg_parser.add_argument('--output_saver_name', type=str, metavar='OUTPUT_SAVER',
                            help='Output saver to use',
                            choices=available_output_savers,
                            default=available_output_savers[-1])
    arg_parser.add_argument('--output_dir', type=str, metavar='DIR', default=None,
                            help='Directory to write output files')
    arg_parser.add_argument('--level', type=str, metavar='LEVEL', default='INFO',
                            help='Logging level')
    # Capture kwargs
    arg_parser.add_argument('kwargs', nargs='*')

    # Parse arguments
    args = arg_parser.parse_args()

    # Setup logging
    setup_logging(level=args.level)

    audio_path = Path(args.audio_path)
    logging.debug(f'Audio path: {args.audio_path}')
    output_dir = Path(args.output_dir) if args.output_dir else None
    logging.debug(f'Writing output to {args.output_dir}')
    # Parse kwargs
    kwargs = {}
    for kwarg in args.kwargs:
        key, value = kwarg.split('=')
        kwargs[key] = value
    logging.debug(f'Running transcription pipeline with kwargs {kwargs}')

    # Pipeline arguments
    audio_validator_name = args.audio_validator_name
    logging.debug(f'Running transcription pipeline with audio validator {audio_validator_name}')
    engine_name = args.engine_name
    logging.debug(f'Running transcription pipeline with engine {engine_name}')
    output_saver_name = args.output_saver_name
    logging.debug(f'Running transcription pipeline with output saver {output_saver_name}')

    # Run pipeline
    transcription = translation_pipeline(audio_path, audio_validator_name, engine_name, output_saver_name, output_dir, **kwargs)
    logging.debug('Transcription complete')
    print(transcription.to_dict())
