from __future__ import annotations
import dataclasses
import json
from pathlib import Path
from typing import List, NamedTuple, Union


class TranscriptionSegment(NamedTuple):
    """A segment of a transcription
    """
    start_ms: int
    end_ms: int
    text: str

    @classmethod
    def merge(cls, segments: List[TranscriptionSegment]) -> TranscriptionSegment:
        """Merge multiple segments into one. The segments must be from the same
        audio. And the segments must be in order.

        Args:
            segments (List[TranscriptionSegment]): List of segments to merge
                from the same audio

        Raises:
            ValueError: The list of segments is empty

        Returns:
            TranscriptionSegment: Merged segment
        """
        if len(segments) == 0:
            raise ValueError('Cannot merge zero segments')

        start_ms = segments[0].start_ms
        end_ms = segments[-1].end_ms
        merged_text = ''
        for segment in segments:
            merged_text += ' ' + segment.text
        return TranscriptionSegment(start_ms, end_ms, merged_text)


@dataclasses.dataclass
class TranscriptionOutput:
    audio_path: Union[Path, str]
    engine: str
    language: str
    transcription: List[TranscriptionSegment]

    def to_dict(self) -> dict:
        transcription_output = dataclasses.asdict(self)
        transcription_output['transcription'] = [
            segment._asdict() for segment in self.transcription
        ]
        return transcription_output

    def to_json(self) -> str:
        data = self.to_dict()
        data['audio_path'] = str(data['audio_path'])
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_filepath: Union[Path, str]) -> TranscriptionOutput:
        with open(json_filepath, 'r') as f:
            data = json.load(f)
        data['audio_path'] = Path(data['audio_path'])
        data['transcription'] = [
            TranscriptionSegment(**segment) for segment in data['transcription']
        ]
        # Validate keys, remove unused keys
        transcription_data = {}

        # Get the fields of the class
        for field in dataclasses.fields(cls):
            if field.name not in data:
                raise ValueError(f'Key {field.name} is missing from the transcription output')
            transcription_data[field.name] = data[field.name]
        return TranscriptionOutput(**data)

    def __len__(self) -> int:
        return len(self.transcription)

    def __iter__(self):
        return iter(self.transcription)
