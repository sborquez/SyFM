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


@dataclasses.dataclass
class TranscriptionOutput:
    audio_path: Union[Path, str]
    engine: str
    language: str
    transcription: List[TranscriptionSegment]

    def to_dict(self):
        transcription_output = dataclasses.asdict(self)
        transcription_output['transcription'] = [
            segment._asdict() for segment in self.transcription
        ]
        return transcription_output

    def to_json(self):
        data = self.to_dict()
        data['audio_path'] = str(data['audio_path'])
        return json.dumps(data)

    def from_json(self, json_filepath: Union[Path, str]):
        data = json.load(json_filepath)
        data['audio_path'] = Path(data['audio_path'])
        data['transcription'] = [
            TranscriptionSegment(**segment) for segment in data['transcription']
        ]
        # Validate keys, remove unused keys
        transcription_data = {}
        for key in dataclasses.asdict(self).keys():
            if key not in data:
                raise ValueError(f'Key {key} is missing from the transcription output')
            transcription_data[key] = data[key]
        return TranscriptionOutput(**data)
