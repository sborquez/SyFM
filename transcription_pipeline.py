from pathlib import Path
from typing import Optional

from transcription.pipeline import build_transcription_pipeline, TranscriptionOutput
from transcription.engine import EngineRegistry


def translation_pipeline(audio_path: Path,
                         engine_name: str,
                         audio_language: Optional[str] = None,
                         output_dir: Optional[Path] = None) -> TranscriptionOutput:
    pipeline = build_transcription_pipeline(engine_name=engine_name, engine_build_arguments={'language': audio_language})
    transcription = pipeline(audio_path, output_dir=output_dir)
    return transcription


if __name__ == '__main__':
    import argparse
    import logging
    from tools.logging import setup_logging
    setup_logging()

    available_engines = EngineRegistry.list_availables()

    arg_parser = argparse.ArgumentParser(description='Transcribe audio files')
    arg_parser.add_argument('--audio_path', type=str, metavar='path_to_audio',
                            help='Path to audio file or directory of audio files')
    arg_parser.add_argument('--audio_language', type=str, metavar='language_code',
                            help='The language of the audio file(s)', default=None)
    arg_parser.add_argument('--engine', type=str, metavar='ENGINE',
                            help='Transcription engine to use',
                            choices=available_engines,
                            default=available_engines[0])
    arg_parser.add_argument('--output_dir', type=str, metavar='DIR', default=None,
                            help='Directory to write output files')
    arg_parser.add_argument('--level', type=str, metavar='LEVEL', default='INFO',
                            help='Logging level')
    args = arg_parser.parse_args()

    # Run pipeline
    logging.debug(f'Running transcription pipeline with engine {args.engine}')
    logging.debug(f'Writing output to {args.output_dir}')
    audio_path = Path(args.audio_path)
    engine = args.engine
    output_dir = Path(args.output_dir) if args.output_dir else None
    transcription = translation_pipeline(audio_path, engine, output_dir=output_dir, audio_language=args.audio_language)
    logging.debug('Transcription complete')
    print(transcription.to_dict())
