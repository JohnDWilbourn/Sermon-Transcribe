# Example Configuration for Sermon-Transcribe

## Directory Structure

```
Sermon-Transcribe/
├── sermon_transcribe.py    # Main application
├── requirements.txt         # Python dependencies
├── README.md               # Documentation
├── LICENSE                 # MIT License
├── .gitignore             # Git ignore rules
├── input/                 # Place segmented files here
│   ├── sermon_001.txt
│   ├── sermon_002.txt
│   └── sermon_003.txt
└── output/                # Merged files appear here
    └── sermon_merged.txt
```

## Example Usage Scenarios

### Scenario 1: Basic One-Time Processing
```bash
# Process all segment files once
python sermon_transcribe.py -i ./input -o ./output
```

### Scenario 2: Continuous Monitoring
```bash
# Monitor a log file and process when "segment complete" appears
python sermon_transcribe.py \
  --mode monitor \
  --monitor-log ./processing.log \
  --input-dir ./input \
  --output-dir ./output \
  --check-interval 5
```

### Scenario 3: Development/Testing (Keep Source Files)
```bash
# Process files but don't delete them (useful for testing)
python sermon_transcribe.py \
  --input-dir ./test_data \
  --output-dir ./test_output \
  --no-delete \
  --log-level DEBUG
```

### Scenario 4: Custom Completion Pattern
```bash
# Use a custom regex pattern to detect completion
python sermon_transcribe.py \
  --mode monitor \
  --monitor-log ./custom.log \
  --completion-pattern "PROCESSING_COMPLETE|ALL_DONE"
```

## Sample Input Files

### Text Segment (sermon_001.txt)
```
This is the first segment of the sermon transcription.
It contains the opening remarks and introduction.
```

### Text Segment (sermon_002.txt)
```
This is the second segment continuing the main teaching.
The doctrine is explained in detail here.
```

### SRT Segment (sermon_001.srt)
```
1
00:00:00,000 --> 00:00:05,000
This is the first subtitle segment.

2
00:00:05,000 --> 00:00:10,000
It contains timed text.
```

### JSON Segment (sermon_001.json)
```json
{
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 5.0,
      "text": "This is the first segment."
    }
  ],
  "text": "This is the first segment."
}
```

## Expected Output

### Merged Text (sermon_merged.txt)
```
This is the first segment of the sermon transcription.
It contains the opening remarks and introduction.

This is the second segment continuing the main teaching.
The doctrine is explained in detail here.
```

### Merged JSON (sermon_merged.json)
```json
{
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 5.0,
      "text": "This is the first segment."
    },
    {
      "id": 1,
      "start": 5.0,
      "end": 10.0,
      "text": "This is the second segment."
    }
  ],
  "text": "This is the first segment. This is the second segment.",
  "metadata": {
    "merged_from": ["input/sermon_001.json", "input/sermon_002.json"],
    "merge_timestamp": "2026-02-11T10:30:00.123456",
    "total_segments": 2
  }
}
```

## Log File Monitoring

The application can monitor a log file for completion signals. Example log entries that trigger processing:

```
2026-02-11 10:15:23 - Segment processing complete
2026-02-11 10:20:45 - Processing done for batch
2026-02-11 10:25:12 - Finished segment transcription
```

Default pattern matches: `segment.*complete|processing.*done|finished.*segment` (case-insensitive)

## Environment Variables (Optional)

While not currently implemented, you could extend the application to use:
- `SERMON_INPUT_DIR`: Default input directory
- `SERMON_OUTPUT_DIR`: Default output directory
- `SERMON_LOG_LEVEL`: Default logging level

## Troubleshooting

### No files found
- Ensure input directory exists and contains properly named segment files
- Check that files have supported extensions (.txt, .srt, .vtt, .tsv, .json)
- Verify files follow naming pattern with numbers (e.g., name_001.txt)

### Monitor mode not triggering
- Verify the monitor log file exists and is being written to
- Check the completion pattern matches the log entries
- Increase log level to DEBUG to see what's being detected

### Merge errors
- Check file encoding (should be UTF-8)
- Verify file format matches extension
- Review log file for detailed error messages
