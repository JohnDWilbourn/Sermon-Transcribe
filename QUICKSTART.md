# Quick Start Guide

Get started with Sermon-Transcribe in 3 simple steps:

## Step 1: Install

```bash
# Clone the repository
git clone https://github.com/JohnDWilbourn/Sermon-Transcribe.git
cd Sermon-Transcribe

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Prepare Your Files

Create an `input` directory and place your segmented transcription files:

```
input/
├── sermon_001.txt
├── sermon_002.txt
└── sermon_003.txt
```

Supported formats: `.txt`, `.srt`, `.vtt`, `.tsv`, `.json`

## Step 3: Run

```bash
# Process all segment files once
python sermon_transcribe.py

# Or specify custom directories
python sermon_transcribe.py -i ./my_segments -o ./my_output
```

Output files appear in the `output` directory with `_merged` in the filename.

## That's it! 🎉

### Need More Control?

```bash
# Keep input files after processing (for testing)
python sermon_transcribe.py --no-delete

# Enable debug logging
python sermon_transcribe.py --log-level DEBUG

# Monitor a log file continuously
python sermon_transcribe.py --mode monitor -m processing.log
```

### Get Help

```bash
python sermon_transcribe.py --help
```

### Learn More

- See [README.md](README.md) for full documentation
- See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for detailed examples
