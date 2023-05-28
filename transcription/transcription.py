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
