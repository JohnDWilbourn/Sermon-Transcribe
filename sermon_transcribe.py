#!/usr/bin/env python3
"""
Sermon Transcribe - Workflow Automation Tool

Monitors a log file for segment processing completion, merges segmented
transcription files into content-descriptive outputs, logs all actions,
and deletes input files after processing.
"""

import sys
import time
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import re


class TranscriptionMerger:
    """Handles merging of segmented transcription files."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def merge_txt_files(self, files: List[Path], output_path: Path) -> bool:
        """Merge plain text transcription files."""
        try:
            self.logger.info(f"Merging {len(files)} text files into {output_path}")
            with output_path.open('w', encoding='utf-8') as outfile:
                for i, file_path in enumerate(sorted(files)):
                    self.logger.debug(f"Processing text file: {file_path}")
                    with file_path.open('r', encoding='utf-8') as infile:
                        content = infile.read()
                        if i > 0:
                            outfile.write('\n\n')
                        outfile.write(content)
            self.logger.info(f"Successfully merged text files to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error merging text files: {e}")
            return False

    def merge_srt_files(self, files: List[Path], output_path: Path) -> bool:
        """Merge SRT subtitle files with renumbered indices."""
        try:
            self.logger.info(f"Merging {len(files)} SRT files into {output_path}")
            subtitle_index = 1
            with output_path.open('w', encoding='utf-8') as outfile:
                for file_path in sorted(files):
                    self.logger.debug(f"Processing SRT file: {file_path}")
                    with file_path.open('r', encoding='utf-8') as infile:
                        content = infile.read()
                        # Process each subtitle block
                        blocks = content.strip().split('\n\n')
                        for block in blocks:
                            if block.strip():
                                lines = block.split('\n')
                                if len(lines) >= 3:
                                    # Write renumbered subtitle
                                    outfile.write(f"{subtitle_index}\n")
                                    outfile.write('\n'.join(lines[1:]) + '\n\n')
                                    subtitle_index += 1
            self.logger.info(f"Successfully merged SRT files to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error merging SRT files: {e}")
            return False

    def merge_vtt_files(self, files: List[Path], output_path: Path) -> bool:
        """Merge WebVTT subtitle files."""
        try:
            self.logger.info(f"Merging {len(files)} VTT files into {output_path}")
            with output_path.open('w', encoding='utf-8') as outfile:
                outfile.write('WEBVTT\n\n')
                for file_path in sorted(files):
                    self.logger.debug(f"Processing VTT file: {file_path}")
                    with file_path.open('r', encoding='utf-8') as infile:
                        content = infile.read()
                        # Skip the WEBVTT header
                        lines = content.split('\n')
                        start_idx = 0
                        for i, line in enumerate(lines):
                            if line.strip() == 'WEBVTT' or line.startswith('WEBVTT'):
                                start_idx = i + 1
                                break
                        # Write the rest
                        remaining = '\n'.join(lines[start_idx:]).strip()
                        if remaining:
                            outfile.write(remaining + '\n\n')
            self.logger.info(f"Successfully merged VTT files to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error merging VTT files: {e}")
            return False

    def merge_tsv_files(self, files: List[Path], output_path: Path) -> bool:
        """Merge TSV transcription files."""
        try:
            self.logger.info(f"Merging {len(files)} TSV files into {output_path}")
            with output_path.open('w', encoding='utf-8') as outfile:
                header_written = False
                for file_path in sorted(files):
                    self.logger.debug(f"Processing TSV file: {file_path}")
                    with file_path.open('r', encoding='utf-8') as infile:
                        lines = infile.readlines()
                        if not header_written and lines:
                            # Write header from first file
                            outfile.write(lines[0])
                            header_written = True
                        # Write data lines (skip header)
                        for line in lines[1:] if header_written else lines:
                            outfile.write(line)
            self.logger.info(f"Successfully merged TSV files to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error merging TSV files: {e}")
            return False

    def merge_json_files(self, files: List[Path], output_path: Path) -> bool:
        """Merge JSON transcription files."""
        try:
            self.logger.info(f"Merging {len(files)} JSON files into {output_path}")
            sorted_files = sorted(files)
            merged_data = {
                'segments': [],
                'text': '',
                'metadata': {
                    'merged_from': [str(f) for f in sorted_files],
                    'merge_timestamp': datetime.now().isoformat(),
                    'total_segments': 0
                }
            }

            for file_path in sorted_files:
                self.logger.debug(f"Processing JSON file: {file_path}")
                with file_path.open('r', encoding='utf-8') as infile:
                    data = json.load(infile)
                    if isinstance(data, dict):
                        if 'segments' in data:
                            merged_data['segments'].extend(data.get('segments', []))
                        if 'text' in data:
                            if merged_data['text']:
                                merged_data['text'] += ' '
                            merged_data['text'] += data.get('text', '')
                    elif isinstance(data, list):
                        merged_data['segments'].extend(data)

            merged_data['metadata']['total_segments'] = len(merged_data['segments'])

            with output_path.open('w', encoding='utf-8') as outfile:
                json.dump(merged_data, outfile, indent=2, ensure_ascii=False)

            self.logger.info(f"Successfully merged JSON files to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error merging JSON files: {e}")
            return False


class LogMonitor:
    """Monitors log file for processing completion signals."""

    def __init__(self, log_file: Path, logger: logging.Logger, 
                 completion_pattern: str = r"segment.*complete|processing.*done|finished.*segment"):
        self.log_file = log_file
        self.logger = logger
        self.completion_pattern = re.compile(completion_pattern, re.IGNORECASE)
        self.last_position = 0

    def check_for_completion(self) -> bool:
        """Check if log file indicates processing completion."""
        if not self.log_file.exists():
            return False

        try:
            with self.log_file.open('r', encoding='utf-8') as f:
                # Handle log rotation/truncation: reset position if file is smaller
                file_size = self.log_file.stat().st_size
                if file_size < self.last_position:
                    self.logger.info("Log file truncated or rotated, resetting position")
                    self.last_position = 0
                
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()

                for line in new_lines:
                    if self.completion_pattern.search(line):
                        self.logger.info(f"Completion signal detected: {line.strip()}")
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Error reading log file: {e}")
            return False


class WorkflowAutomation:
    """Main workflow automation orchestrator."""

    def __init__(self, config: Dict):
        self.config = config
        self.setup_logging()
        self.merger = TranscriptionMerger(self.logger)
        
        if config.get('monitor_log'):
            self.log_monitor = LogMonitor(
                Path(config['monitor_log']), 
                self.logger,
                config.get('completion_pattern', r"segment.*complete|processing.*done|finished.*segment")
            )
        else:
            self.log_monitor = None

    def setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get('log_level', 'INFO')
        log_file = self.config.get('log_file', 'workflow_automation.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('SermonTranscribe')
        self.logger.info("Workflow automation initialized")

    def find_segment_files(self, input_dir: Path) -> Dict[str, List[Path]]:
        """Find segmented files grouped by base name and extension."""
        self.logger.info(f"Scanning for segment files in {input_dir}")
        
        files_by_type = {}
        if not input_dir.exists():
            self.logger.warning(f"Input directory does not exist: {input_dir}")
            return files_by_type

        # Find all files matching the pattern
        for ext in ['.txt', '.srt', '.vtt', '.tsv', '.json']:
            matching_files = list(input_dir.glob(f"*{ext}"))
            if matching_files:
                # Group by base name (removing segment numbers)
                grouped = {}
                for file_path in matching_files:
                    # Extract base name (e.g., "sermon_001.txt" -> "sermon")
                    base_name = re.sub(r'_\d+' + re.escape(ext) + r'$', '', file_path.name)
                    if base_name not in grouped:
                        grouped[base_name] = []
                    grouped[base_name].append(file_path)
                
                # Only include groups with multiple files
                for base_name, file_list in grouped.items():
                    if len(file_list) > 1:
                        # Store with tuple key (base_name, ext) to avoid double extension issue
                        key = (base_name, ext)
                        files_by_type[key] = sorted(file_list)
                        self.logger.info(f"Found {len(file_list)} segment files for {base_name}{ext}")

        return files_by_type

    def merge_files(self, files: List[Path], output_path: Path) -> bool:
        """Merge files based on their extension."""
        if not files:
            return False

        ext = files[0].suffix.lower()
        
        if ext == '.txt':
            return self.merger.merge_txt_files(files, output_path)
        elif ext == '.srt':
            return self.merger.merge_srt_files(files, output_path)
        elif ext == '.vtt':
            return self.merger.merge_vtt_files(files, output_path)
        elif ext == '.tsv':
            return self.merger.merge_tsv_files(files, output_path)
        elif ext == '.json':
            return self.merger.merge_json_files(files, output_path)
        else:
            self.logger.warning(f"Unsupported file type: {ext}")
            return False

    def cleanup_files(self, files: List[Path]):
        """Delete processed input files."""
        self.logger.info(f"Cleaning up {len(files)} processed files")
        for file_path in files:
            try:
                file_path.unlink()
                self.logger.info(f"Deleted: {file_path}")
            except Exception as e:
                self.logger.error(f"Error deleting {file_path}: {e}")

    def process_files(self):
        """Process all segment files found in input directory."""
        input_dir = Path(self.config['input_dir'])
        output_dir = Path(self.config['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("Starting file processing")
        
        files_by_type = self.find_segment_files(input_dir)
        
        if not files_by_type:
            self.logger.info("No segment files found to process")
            return

        for (base_name, ext), files in files_by_type.items():
            output_name = f"{base_name}_merged{ext}"
            output_path = output_dir / output_name
            
            self.logger.info(f"Processing {base_name}{ext}: {len(files)} files -> {output_path}")
            
            if self.merge_files(files, output_path):
                self.logger.info(f"Successfully created merged file: {output_path}")
                
                if self.config.get('delete_after_processing', True):
                    self.cleanup_files(files)
            else:
                self.logger.error(f"Failed to merge files for {base_name}{ext}")

    def run(self):
        """Main run loop."""
        self.logger.info("Workflow automation started")
        
        if self.config.get('mode') == 'monitor':
            self.logger.info("Running in monitor mode")
            check_interval = self.config.get('check_interval', 5)
            
            while True:
                if self.log_monitor and self.log_monitor.check_for_completion():
                    self.logger.info("Processing triggered by log completion signal")
                    self.process_files()
                
                time.sleep(check_interval)
        else:
            self.logger.info("Running in single-run mode")
            self.process_files()
            self.logger.info("Processing complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Sermon Transcribe - Workflow Automation Tool'
    )
    parser.add_argument(
        '-i', '--input-dir',
        default='./input',
        help='Input directory containing segment files (default: ./input)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        default='./output',
        help='Output directory for merged files (default: ./output)'
    )
    parser.add_argument(
        '-l', '--log-file',
        default='workflow_automation.log',
        help='Log file path (default: workflow_automation.log)'
    )
    parser.add_argument(
        '-m', '--monitor-log',
        help='Log file to monitor for completion signals'
    )
    parser.add_argument(
        '--mode',
        choices=['single', 'monitor'],
        default='single',
        help='Execution mode: single (run once) or monitor (continuous) (default: single)'
    )
    parser.add_argument(
        '--check-interval',
        type=int,
        default=5,
        help='Interval in seconds for checking log file in monitor mode (default: 5)'
    )
    parser.add_argument(
        '--no-delete',
        action='store_true',
        help='Do not delete input files after processing'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--completion-pattern',
        default=r"segment.*complete|processing.*done|finished.*segment",
        help='Regex pattern to detect completion in monitored log'
    )

    args = parser.parse_args()

    config = {
        'input_dir': args.input_dir,
        'output_dir': args.output_dir,
        'log_file': args.log_file,
        'monitor_log': args.monitor_log,
        'mode': args.mode,
        'check_interval': args.check_interval,
        'delete_after_processing': not args.no_delete,
        'log_level': args.log_level,
        'completion_pattern': args.completion_pattern
    }

    automation = WorkflowAutomation(config)
    
    try:
        automation.run()
    except KeyboardInterrupt:
        automation.logger.info("Workflow automation stopped by user")
        sys.exit(0)
    except Exception as e:
        automation.logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
