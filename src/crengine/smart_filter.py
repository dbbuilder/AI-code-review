"""
Smart File Filtering
Intelligently filter repository files to focus only on meaningful code
"""

import yaml
from pathlib import Path
from typing import List, Set
from dataclasses import dataclass


@dataclass
class FilterConfig:
    """Configuration for smart file filtering"""
    include_patterns: List[str]
    exclude_patterns: List[str]
    max_file_size: int
    max_files: int
    priority_patterns: List[str]
    skip_tests: bool
    test_patterns: List[str]


def load_filter_config(config_path: Path) -> FilterConfig:
    """Load smart filter configuration from YAML"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return FilterConfig(
        include_patterns=config.get('include_patterns', []),
        exclude_patterns=config.get('exclude_patterns', []),
        max_file_size=config.get('max_file_size', 1048576),
        max_files=config.get('max_files', 500),
        priority_patterns=config.get('priority_patterns', []),
        skip_tests=config.get('skip_tests', False),
        test_patterns=config.get('test_patterns', [])
    )


def should_include_file(file_path: Path, config: FilterConfig) -> bool:
    """
    Determine if a file should be included in analysis

    Returns True if:
    - File matches include patterns
    - File doesn't match exclude patterns
    - File size is within limits
    - File is not a test (if skip_tests is True)
    """

    # Convert to relative path for pattern matching
    path_str = str(file_path)

    # Check file size
    if file_path.is_file():
        try:
            size = file_path.stat().st_size
            if size > config.max_file_size:
                return False
        except OSError:
            return False

    # Check exclude patterns first (faster to reject)
    for exclude_pattern in config.exclude_patterns:
        if file_path.match(exclude_pattern):
            return False

    # Check if it's a test file and we're skipping tests
    if config.skip_tests:
        for test_pattern in config.test_patterns:
            if file_path.match(test_pattern):
                return False

    # Check include patterns
    for include_pattern in config.include_patterns:
        if file_path.match(include_pattern):
            return True

    return False


def prioritize_files(files: List[Path], config: FilterConfig) -> List[Path]:
    """
    Sort files by priority, with priority_patterns files first

    Priority files are likely to contain main application logic
    """
    priority_files = []
    other_files = []

    for file_path in files:
        is_priority = False
        for priority_pattern in config.priority_patterns:
            if file_path.match(priority_pattern):
                is_priority = True
                break

        if is_priority:
            priority_files.append(file_path)
        else:
            other_files.append(file_path)

    # Sort each group by path for deterministic ordering
    priority_files.sort()
    other_files.sort()

    return priority_files + other_files


def filter_repository_files(repo_root: Path, config_path: Path) -> List[Path]:
    """
    Filter repository files intelligently

    Returns a prioritized list of files that should be analyzed,
    limited by max_files configuration.
    """
    config = load_filter_config(config_path)

    # Collect all files that match criteria
    filtered_files: List[Path] = []

    for file_path in repo_root.rglob('*'):
        if file_path.is_file():
            if should_include_file(file_path, config):
                filtered_files.append(file_path)

    # Prioritize files
    prioritized_files = prioritize_files(filtered_files, config)

    # Limit to max_files
    if len(prioritized_files) > config.max_files:
        prioritized_files = prioritized_files[:config.max_files]

    return prioritized_files


def get_file_summary(files: List[Path], repo_root: Path) -> dict:
    """
    Get summary statistics about filtered files
    """
    from collections import defaultdict

    stats = {
        'total_files': len(files),
        'total_size': 0,
        'by_extension': defaultdict(int),
        'by_directory': defaultdict(int)
    }

    for file_path in files:
        # Size
        try:
            stats['total_size'] += file_path.stat().st_size
        except OSError:
            pass

        # Extension
        ext = file_path.suffix.lower()
        stats['by_extension'][ext] += 1

        # Directory
        try:
            rel_path = file_path.relative_to(repo_root)
            if len(rel_path.parts) > 1:
                top_dir = rel_path.parts[0]
                stats['by_directory'][top_dir] += 1
        except ValueError:
            pass

    return stats
