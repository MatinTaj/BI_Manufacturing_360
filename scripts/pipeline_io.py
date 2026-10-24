"""Explicit, exclusive staging-only generator output. Never writes processed data."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def output_directory(path, root=ROOT):
    root = Path(root).resolve()
    if path is None:
        raise ValueError('An explicit --output-dir is required; processed output is forbidden')
    target = Path(path).resolve()
    staging = root / 'data' / 'staging'
    allowed = target == staging or staging in target.parents
    repeat = target.parent == root / 'data' and target.name.startswith('staging_repro_')
    if not (allowed or repeat):
        raise ValueError(f'Unsafe output directory: {target}; use data/staging or a data/staging_repro_ temporary directory')
    return target


def parse_output_directory():
    parser = argparse.ArgumentParser(description='Generate to an explicit safe staging directory only')
    parser.add_argument('--output-dir', required=True, type=Path)
    return output_directory(parser.parse_args().output_dir)


def write_csv(frame, name, directory):
    directory = output_directory(directory)
    if not name.isidentifier():
        raise ValueError('CSV name must be a plain dataset identifier')
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f'{name}.csv'
    # Opening exclusively prevents overwriting prior candidates, including links.
    with target.open('x', encoding='utf-8', newline='') as stream:
        frame.to_csv(stream, index=False, float_format='%.8f', lineterminator='\n')
