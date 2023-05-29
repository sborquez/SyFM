# SyFM

This project is a collection of pipelines for the SyFM project. It contains pipelines for the generation of synthetic voices.

## Getting Started

### Prerequisites

The prerequisites are listed in the requirements.txt file. You can install them by:

```bash
pip install -r requirements.txt
```

You can also running a container with the dockerfile. To build the image, run:

```bash
docker build -t syfm:latest .
```

To run the container with a volume, run:

```bash
docker run -it -v /path/to/audio:/audio syfm:latest transcription-pipeline
```

To run the container with a volume and GPU, run:

```bash
docker run -it --gpus all -v /path/to/audio:/audio syfm:latest transcription-pipeline
```

## Generate a Transcription Dataset

This transcription pipeline is for the voice transcription task. It define the Transcription Pipeline
class, to transcribe the audio file into text, and generate a Croquis dataset for training a new AI voice.

### Usage

To use the Transcription Pipeline, you can run the following command:

```bash
python -m scripts.generate_transcription_dataset --audio_path /path/to/audio --engine_name StableWhisperEngine --output_dir path/to/output --model medium --language es --dataset_name voice_name
```

The output will be saved in the same directory as the audio file, with the same name
as the audio file, but with a .json extension.

### Output format

The default output format is the Croquis Dataset format. Described in the next section.

#### CroquisOutputSaver

The Croquis output dataset is the default output format. It will write a output file will be formated as follows:

```json
# metadata.txt

audio1|This is my sentence.
audio2|This is maybe my sentence.
audio3|This is certainly my sentence.
audio4|Let this be your sentence.
...
```

with the audio files and transcription files in the same directory. As the following:

```bash
/Output/Dir/DatasetName
      |
      | -> metadata.txt
      | -> /wavs
              | -> audio1.wav
              | -> audio2.wav
              | ...
```

For more information about the Croquis Dataset format, please refer to the [Croquis](https://tts.readthedocs.io/en/latest/formatting_your_dataset.htmlf) repository.

#### BasicOutputSaver

The BasicOutputSaver will write a output file will be formated as follows:

```json
[
    {
        "audio_path": "/path/to/audio",
        "engine": "whisper",
        "language": "en",
        "transcription": [
          {
            "start_ms": 0,
            "end_ms": 2000,
            "text": "This is the transcription of the audio file"
          }
        ]
    }
]
```

## TODO

- [ ] General
  - [ ] Add container
  - [ ] Add tests
- [x] Transcription Pipeline
  - [x] Define Transcription Pipeline class
  - [x] Implement with Whisper
  - [x] Implement with Stable Whisper
  - [x] Add Croquis dataset generation output
- [ ] Trainer
  - [ ] TBA
- [ ] Synthetizer
  - [ ] TBA

## Authors

Sebastián Ignacio Bórquez González

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file

## Built With

- [pydub](https://github.com/jiaaro/pydub)
- [Croquis](https://)
- [OpenAI](https://openai.com/blog/openai-api/)
- [Whisper](https://github.com/openai/whisper)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)