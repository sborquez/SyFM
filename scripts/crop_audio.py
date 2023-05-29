from pathlib import Path
import logging
from typing import Any, Optional

from pydub import AudioSegment

from tools.logging import setup_logging

setup_logging()


def crop_audio(audio_filepath: Path, start_ms: int = 0, end_ms: Optional[int] = None,
               output_dir: Optional[Path] = None, output_name: Optional[str] = None) -> None:
    """Crop an audio file, and save the cropped audio file to the output directory. If the
    output directory is not specified, the cropped audio file will be saved to the same
    directory as the input audio file. If the output name is not specified, the cropped
    audio file will have a name with the following format:
        {input_audio_file_name}_{start_ms}_{end_ms}.{input_audio_file_extension}

    Args:
        audio_filepath (Path): Filepath to the audio file to be cropped.
        start_ms (Optional[int]): Start time in milliseconds.
        end_ms (Optional[int]): End time in milliseconds.
        output_dir (Optional[Path], optional): Output directory to save the cropped audio
            file. Defaults to None.
        output_name (Optional[str], optional): Output name of the cropped audio file.
            Defaults to None.
    """
    audio = AudioSegment.from_file(audio_filepath)
    if end_ms is None:
        end_ms = len(audio)
    logging.info(f'Cropping audio file {audio_filepath} from {start_ms}ms to {end_ms}ms')
    cropped_audio = audio[start_ms:end_ms]
    if output_dir is None:
        output_dir = audio_filepath.parent
    if output_name is None:
        output_name = f'{audio_filepath.stem}_{start_ms}_{end_ms}{audio_filepath.suffix}'
    else:
        output_name = f'{output_name}{audio_filepath.suffix}'
    output_filepath = output_dir / output_name
    cropped_audio.export(output_filepath)


if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(description='Crop audio files')
    arg_parser.add_argument('--audio_filepath', type=str, metavar='path_to_audio', required=True,
                            help='Path to audio file or directory of audio files')
    arg_parser.add_argument('--start_ms', type=int, metavar='START_MS', default=0,
                            help='Start time in milliseconds')
    arg_parser.add_argument('--end_ms', type=int, metavar='END_MS', default=None,
                            help='End time in milliseconds')
    arg_parser.add_argument('--output_dir', type=str, metavar='DIR', default=None,
                            help='Directory to write output files')
    arg_parser.add_argument('--output_name', type=str, metavar='NAME', default=None,
                            help='Name of the output file')
    args = arg_parser.parse_args()

    crop_audio(Path(args.audio_filepath), args.start_ms, args.end_ms, args.output_dir,
                args.output_name)


