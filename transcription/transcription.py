import dataclasses
import json
from pathlib import Path
from typing import Union


@dataclasses.dataclass
class TranscriptionOutput:
    audio_path: Union[Path, str]
    engine: str
    language: str
    transcription: str

    def to_dict(self):
        return dataclasses.asdict(self)

    def to_json(self):
        data = self.to_dict()
        data['audio_path'] = str(data['audio_path'])
        return json.dumps(data)
