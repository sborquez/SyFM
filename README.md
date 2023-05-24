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

## Transcription Pipeline

This pipeline is for the voice transcription task. It define the Transcription Pipeline
class, to transcribe the audio file into text. It can also be used to generate a Croquis dataset.

### Usage

To use the Transcription Pipeline, you can run the following command:

```bash
python transcription_pipeline.py --audio_path /path/to/audio  --engine whisper
```

The output will be saved in the same directory as the audio file, with the same name
as the audio file, but with a .json extension.

### Output format

The output file will be formated as follows:

```json
[
    {
        "audio_path": "/path/to/audio",
        "engine": "whisper",
        "language": "en",
        "transcription": "This is the transcription of the audio file"
    }
]
```

## TODO

- [ ] General
  - [ ] Add container
  - [ ] Add tests
- [ ] Transcription Pipeline
  - [x] Define Transcription Pipeline class
  - [ ] Implement with Whisper
  - [ ] Implement with Google Cloud Speech-to-Text API
  - [ ] Implement with OpenAI API
  - [ ] Add support for other languages
- [ ] Synthetizer Pipeline
  - [ ] TBA

## Authors

Sebastián Ignacio Bórquez González

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file

## Built With

- [Croquis](https://)
- [OpenAI](https://openai.com/blog/openai-api/)
- [Whisper](https://github.com/openai/whisper)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)