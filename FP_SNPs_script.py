#!/usr/bin/env python3

import pandas as pd
import pysam
import argparse
import os
import sys
from datetime import datetime

def setup_logger(output_path):
    log_path = os.path.splitext(output_path)[0] + '.log'
    def log(message):
        ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        full_msg = f"{ts} {message}"
        print(full_msg)
        with open(log_path, 'a') as f:
            f.write(full_msg + '\n')
    return log, log_path

def parse_args2():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='step', required=True)
    
    # Подкоманда preprocess
    preprocess_parser = subparsers.add_parser('preprocess')
    preprocess_parser.add_argument('--input', nargs='+', required=True)
    
    # Подкоманда validate
    validate_parser = subparsers.add_parser('validate')
    validate_parser.add_argument('--input', nargs='+', required=True)
    validate_parser.add_argument('--output', required=True)  # только здесь!

def parse_args():
    parser = argparse.ArgumentParser(
        description="Скрипт подготавливает данные и валидирует SNP по референсной сборке",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--step', choices=['preprocess', 'validate'], required=True,
                        help='Шаг: preprocess (создание .tsv) или validate (сверка с референсом)')

    parser.add_argument('--input', nargs='+', required=True,
                        help='''Для preprocess: укажите путь к FP_SNPs.txt. Для validate: сначала укажите tsv-файл, затем директорию с референсными хромосомами''')

    parser.add_argument('--output', required=False,
                        help='Только для validate: укажите путь и название для итогового tsv-файла')

    return parser.parse_args()

def preprocess(input_file):
    try:
        df = pd.read_csv(input_file, sep='\t')
    except Exception as e:
        print(f"ОШИБКА: Не удалось прочитать файл {input_file}: {e}")
        sys.exit(1)

    df = df.drop(columns=['GB37_position'])
    df = df[df['chromosome'] != 23]

    df['CHROM'] = 'chr' + df['chromosome'].astype(str)
    df['POS'] = df['GB38_position']
    df['ID'] = 'rs' + df['rs#'].astype(str)

    vcf_like = df[['CHROM', 'POS', 'ID', 'allele1', 'allele2']]
    vcf_like.columns = ['CHROM', 'POS', 'ID', 'REF', 'ALT']

    output_dir = os.path.dirname(os.path.abspath(input_file))
    abs_output_path = os.path.abspath(os.path.join(output_dir, 'FP_SNPs_10k_GB38_twoAllelsFormat.tsv'))


    vcf_like.to_csv(abs_output_path, sep='\t', index=False)
    print(f"Файл предобработки сохранён: {abs_output_path}")

def validate(input_file, fasta_dir, output_file, log, log_path):
    try:
        df = pd.read_csv(input_file, sep='\t', dtype=str, engine='python')
    except Exception as e:
        log(f"Ошибка при чтении файла: {e}")
        sys.exit(1)

    if df.empty:
        log("Входной файл пуст.")
        sys.exit(1)

    log(f"Обработка {len(df)} SNP...")

    results = []
    errors = 0

    for _, row in df.iterrows():
        chrom = row['CHROM'].replace('chr', '')
        fasta_path = os.path.join(fasta_dir, f'chr{chrom}.fa')

        try:
            fasta = pysam.FastaFile(fasta_path)
            ref_base = fasta.fetch(f'chr{chrom}', int(row['POS']) - 1, int(row['POS'])).upper()

            if ref_base == row['REF']:
                ref, alt = row['REF'], row['ALT']
            elif ref_base == row['ALT']:
                ref, alt = row['ALT'], row['REF']
            else:
                log(f"{row['ID']} ({row['CHROM']}:{row['POS']}): GRCh38 = {ref_base}, REF = {row['REF']}, ALT = {row['ALT']} — удалено")
                errors += 1
                continue

            results.append({
                'CHROM': row['CHROM'],
                'POS': row['POS'],
                'ID': row['ID'],
                'REF': ref,
                'ALT': alt})

        except FileNotFoundError:
            log(f"Ошибка: файл {fasta_path} не найден")
            sys.exit(1)
        except Exception as e:
            log(f"Ошибка при обработке {row['ID']}: {e}")
            sys.exit(1)

    pd.DataFrame(results).to_csv(output_file, sep='\t', index=False)
    if errors > 0:
        log(f"Удалено строк с несопоставимыми аллелями: {errors}")
    else:
        log("Все SNP соответствуют референсу.")

    log(f"Файлы {os.path.basename(output_file)} и {os.path.basename(log_path)} сохранены по пути: {os.path.dirname(os.path.abspath(output_file))}")

def main():
    args = parse_args()

    if args.step == 'preprocess':
        if len(args.input) != 1:
            print("ОШИБКА: Для preprocess нужен один путь к входному файлу.")
            sys.exit(1)
        preprocess(args.input[0])
        return

    elif args.step == 'validate':
        if len(args.input) != 2:
            print("ОШИБКА: Для validate укажите два значения через пробел: TSV-файл и директорию с референсными хромосомами.")
            sys.exit(1)
        if not args.output:
            print("ОШИБКА: Для validate требуется --output")
            sys.exit(1)

        input_file = args.input[0]
        fasta_dir = args.input[1]
        log, log_path = setup_logger(args.output)
        validate(input_file, fasta_dir, args.output, log, log_path)

if __name__ == '__main__':
    main()

