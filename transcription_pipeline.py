from pathlib import Path
from typing import Optional

from transcription.pipeline import TranscriptionPipelineRegistry, TranscriptionOutput
from transcription.engine import EngineRegistry


def translation_pipeline(audio_path: Path, engine: str, output_dir: Optional[Path] = None) -> TranscriptionOutput:
    engine = EngineRegistry.build_engine(engine)
    pipeline = TranscriptionPipelineRegistry.build_transcription_pipeline('BasicTranscriptionPipeline', engine=engine)
    transcription = pipeline(audio_path, output_dir=output_dir)
    return transcription


if __name__ == '__main__':
    import argparse
    import logging

    available_engines = EngineRegistry.list_available_engines()

    arg_parser = argparse.ArgumentParser(description='Transcribe audio files')
    arg_parser.add_argument('--audio_path', type=str, metavar='path_to_audio',
                            help='Path to audio file or directory of audio files')
    arg_parser.add_argument('--engine', type=str, metavar='ENGINE',
                            help='Transcription engine to use',
                            choices=available_engines,
                            default=available_engines[0])
    arg_parser.add_argument('--output_dir', type=str, metavar='DIR', default=None,
                            help='Directory to write output files')
    arg_parser.add_argument('--level', type=str, metavar='LEVEL', default='INFO',
                            help='Logging level')
    args = arg_parser.parse_args()

    # Set logging level
    logging.basicConfig(level=args.level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Run pipeline
    logging.debug(f'Running transcription pipeline with engine {args.engine}')
    logging.debug(f'Writing output to {args.output_dir}')
    audio_path = Path(args.audio_path)
    engine = args.engine
    output_dir = Path(args.output_dir) if args.output_dir else None
    transcription = translation_pipeline(audio_path, engine, output_dir)
    logging.debug(f'Transcription complete')
    print(transcription.to_dict())

