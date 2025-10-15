import argparse
import csv
import os

from tabulate import tabulate


REPORT_NAME = 'average-rating.txt'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Обработка файлов и создание отчета'
    )

    parser.add_argument(
        '--files',
        nargs='+',
        required=True,
        help='Список файлов для обработки',
    )

    parser.add_argument(
        '--report',
        required=False,
        help='Имя выходного отчета',
        default=REPORT_NAME,
    )

    return parser.parse_args()


def read_csv(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            reader = csv.reader(f)
            return [row for row in reader]
    else:
        return []


def get_data4report(source, analyzed_col1: int, analyzed_col2: int):
    data4report = []
    for row in source:
        if row[0].upper() == 'NAME':
            header4report = [row[analyzed_col1], row[analyzed_col2]]
        else:
            data4report.append([row[analyzed_col1], float(row[analyzed_col2])])
    return data4report, header4report


def create_report(data: tuple, report_name, report_header) -> str:
    if not data:
        print("Нет данных для формирования отчета")
        return

    sum_dict = {}
    count_dict = {}
    for analyzed_name, analyzed_value in data:
        sum_dict[analyzed_name] = (
            sum_dict[analyzed_name] + analyzed_value
            if analyzed_name in sum_dict
            else analyzed_value
        )
        count_dict[analyzed_name] = (
            count_dict[analyzed_name] + 1 if analyzed_name in count_dict else 1
        )
    for key in sum_dict.keys():
        sum_dict[key] = round(sum_dict[key] / count_dict[key], 2)

    out_table = tabulate(
        sorted(sum_dict.items(), key=lambda x: x[1], reverse=True),
        headers=report_header,
        tablefmt="pretty",
        numalign="decimal",
        stralign="left",
        showindex=[i for i in range(1, len(sum_dict) + 1)],
    )
    with open(report_name, "w", encoding="utf-8") as f:
        f.write(out_table)
    print(out_table)
    print()


if __name__ == "__main__":
    args = parse_args()
    csvfiles = []
    for file in args.files:
        csvfiles.extend(read_csv(file))

    report_data, report_header = get_data4report(csvfiles, 1, 3)
    create_report(tuple(report_data), args.report, report_header)
