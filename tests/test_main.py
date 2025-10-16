import os
import subprocess
import sys
import tempfile
import csv

# from unittest.mock import patch
import pytest
from pathlib import Path

from main import create_report, get_data4report, read_csv


@pytest.fixture(scope='module')
def temp_csv_file():
    '''Create a temporary CSV file with some data.'''
    with tempfile.NamedTemporaryFile(
        mode='w', delete=False, suffix='.csv'
    ) as tf:
        writer = csv.writer(tf)
        writer.writerow(['name', 'brand', 'price', 'rating'])
        writer.writerow(['iphone 15 pro', 'apple', '999', '4.9'])
        writer.writerow(['galaxy s23 ultra', 'samsung', '1199', '4.8'])
        writer.writerow(['redmi note 12', 'xiaomi', '199', '4.6'])
        writer.writerow(['iphone 14', 'apple', '799', '4.7'])
        writer.writerow(['galaxy a54', 'samsung', '349', '4.2'])

    yield tf.name
    os.remove(tf.name)


def test_read_csv(temp_csv_file):
    result = read_csv(temp_csv_file)
    assert len(result) == 6
    assert result[0] == ['name', 'brand', 'price', 'rating']


@pytest.mark.parametrize(
    'sample_data,expected_data,expected_header',
    [
        (
            [
                ['name', 'brand', 'price', 'rating'],
                ['iphone 15 pro', 'apple', '999', '4.9'],
                ['galaxy s23 ultra', 'samsung', '1199', '4.8'],
                ['redmi note 12', 'xiaomi', '199', '4.6'],
                ['iphone 14', 'apple', '799', '4.7'],
                ['galaxy a54', 'samsung', '349', '4.2'],
            ],
            [
                ['apple', 4.9],
                ['samsung', 4.8],
                ['xiaomi', 4.6],
                ['apple', 4.7],
                ['samsung', 4.2],
            ],
            ['brand', 'rating'],
        ),
        ([], [], []),
    ],
)
def test_get_data4report(sample_data, expected_data, expected_header):
    data, header = get_data4report(
        sample_data, analyzed_col1=1, analyzed_col2=3
    )
    assert data == expected_data
    assert header == expected_header


@pytest.mark.parametrize(
    'data,report_name,header,expected_file_output, expected_console_output',
    [
        (
            [
                ['apple', 4.9],
                ['samsung', 4.8],
                ['xiaomi', 4.6],
                ['apple', 4.7],
                ['samsung', 4.2],
            ],
            'test-report.txt',
            ['brand', 'rating'],
            '''+---+---------+--------+
|   | brand   | rating |
+---+---------+--------+
| 1 | apple   | 4.8    |
| 2 | xiaomi  | 4.6    |
| 3 | samsung | 4.5    |
+---+---------+--------+''',
            '''+---+---------+--------+
|   | brand   | rating |
+---+---------+--------+
| 1 | apple   | 4.8    |
| 2 | xiaomi  | 4.6    |
| 3 | samsung | 4.5    |
+---+---------+--------+\n\n''',
        ),
        (
            [],
            'empty-report.txt',
            [],
            '',
            'Нет данных для формирования отчёта\n',
        ),
    ],
)
def test_create_report(
    capfd,
    data,
    report_name,
    header,
    expected_file_output,
    expected_console_output,
):
    try:
        create_report(data, report_name, header)

        if expected_file_output:
            assert Path(report_name).exists()
            with open(report_name, 'r') as f:
                content = f.read().strip()
            assert content == expected_file_output
        else:
            assert not Path(report_name).exists()

        captured = capfd.readouterr()
        assert captured.out == expected_console_output
    finally:
        if Path(report_name).exists():
            os.remove(report_name)


@pytest.mark.parametrize(
    'args,expected_return_code',
    [
        (
            [
                sys.executable,
                'main.py',
                '--files',
                'test1.csv',
                'test2.csv',
                '--report',
                'output.txt',
            ],
            0,
        ),
        (
            [
                sys.executable,
                'main.py',
                '--files',
                'test1.csv',
                'test2.csv',
            ],
            0,
        ),
        (
            [
                sys.executable,
                'main.py',
                '--report',
                'output.txt',
            ],
            2,
        ),
        (
            [
                sys.executable,
                'main.py',
                '--files',
                'test1.csv',
                '--report',
                'output.txt',
            ],
            0,
        ),
        (
            [
                sys.executable,
                'main.py',
            ],
            2,
        ),
    ],
)
def test_argparse_via_subprocess(args, expected_return_code):
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
    )
    assert result.returncode == expected_return_code
