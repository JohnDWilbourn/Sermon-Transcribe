# Sermon-Transcribe

A Python workflow automation tool for Robert B. Thieme, Jr sermon transcription operations.

## Overview

Sermon-Transcribe automates the workflow of processing segmented transcription files. It monitors for processing completion, merges segmented files into unified outputs, logs all operations, and cleans up processed files.

## Features

- 📁 **Multi-format Support**: Handles .txt, .srt, .vtt, .tsv, and .json transcription formats
- 👁️ **Log Monitoring**: Watches log files for processing completion signals
- 🔄 **Intelligent Merging**: Combines segmented files with format-specific handling
- 📝 **Comprehensive Logging**: Records all operations for audit and debugging
- 🧹 **Automatic Cleanup**: Removes processed input files after successful merging
- ⚙️ **Flexible Modes**: Single-run or continuous monitoring modes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JohnDWilbourn/Sermon-Transcribe.git
cd Sermon-Transcribe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage (Single Run)

Process all segment files in the input directory once:

```bash
python sermon_transcribe.py -i ./input -o ./output
```

### Monitor Mode

Continuously monitor a log file and process files when completion is detected:

```bash
python sermon_transcribe.py -i ./input -o ./output --mode monitor -m processing.log
```

### Command Line Options

```
-i, --input-dir PATH          Input directory containing segment files (default: ./input)
-o, --output-dir PATH         Output directory for merged files (default: ./output)
-l, --log-file PATH          Log file path (default: workflow_automation.log)
-m, --monitor-log PATH       Log file to monitor for completion signals
--mode {single,monitor}      Execution mode (default: single)
--check-interval SECONDS     Interval for checking log in monitor mode (default: 5)
--no-delete                  Keep input files after processing
--log-level LEVEL           Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
--completion-pattern REGEX  Regex pattern to detect completion in monitored log
```

### Examples

1. **Process files with custom output directory:**
```bash
python sermon_transcribe.py -i ./transcripts/segments -o ./transcripts/merged
```

2. **Monitor mode with custom check interval:**
```bash
python sermon_transcribe.py --mode monitor -m ./logs/processing.log --check-interval 10
```

3. **Debug mode without deleting source files:**
```bash
python sermon_transcribe.py --log-level DEBUG --no-delete
```

4. **Custom completion pattern:**
```bash
python sermon_transcribe.py --mode monitor -m process.log --completion-pattern "SEGMENT_COMPLETE|DONE"
```

## File Format Support

### Text Files (.txt)
Plain text transcriptions are merged with double line breaks between segments.

### SRT Subtitles (.srt)
SubRip subtitle files are merged with renumbered sequential indices.

### WebVTT Subtitles (.vtt)
WebVTT files are combined with a single header and concatenated cues.

### TSV Files (.tsv)
Tab-separated value files are merged with a single header row.

### JSON Files (.json)
JSON transcriptions are merged into a structured format with metadata:
```json
{
  "segments": [...],
  "text": "...",
  "metadata": {
    "merged_from": [...],
    "merge_timestamp": "...",
    "total_segments": 0
  }
}
```

## File Organization

The tool expects segmented files with naming patterns like:
- `sermon_001.txt`, `sermon_002.txt`, `sermon_003.txt`
- `lecture_01.srt`, `lecture_02.srt`

Output files are named with `_merged` suffix:
- `sermon_merged.txt`
- `lecture_merged.srt`

## Logging

All operations are logged to both the console and a log file. Log entries include:
- File discovery and scanning
- Merge operations and progress
- File deletions
- Errors and warnings

Example log output:
```
2026-02-11 10:15:23,456 - SermonTranscribe - INFO - Workflow automation initialized
2026-02-11 10:15:23,457 - SermonTranscribe - INFO - Starting file processing
2026-02-11 10:15:23,458 - SermonTranscribe - INFO - Found 5 segment files for sermon.txt
2026-02-11 10:15:23,459 - SermonTranscribe - INFO - Merging 5 text files into output/sermon_merged.txt
2026-02-11 10:15:23,512 - SermonTranscribe - INFO - Successfully merged text files
```

## Requirements

- Python 3.7+
- No external dependencies required (uses only Python standard library)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

John D. Wilbourn

## Acknowledgments

Created for Robert B. Thieme, Jr sermon transcription operations.
