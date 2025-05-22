# FP_SNPs_script.py

Скрипт предназначен для предобработки и валидации SNP-маркеров на основе референсного генома человека (GRCh38) и работает в двух режимах:

- **Предобработка** (`--step preprocess`)  
Преобразует исходный файл `FP_SNPs.txt` в формат `.tsv`, необходимый для последующей валидации.
  
- **Валидация** (`--step validate`)  
Проверяет, соответствует ли allele1 и allele2 референсному значению в сборке GRCh38. При необходимости меняет местами REF и ALT. SNPs, у которых ни один аллель не совпадает с референсом, исключаются.

Режим `--step preprocess` запускается только с указанием аргумента `--input`. Аргумент `--input` требует файл `FP_SNPs.txt`. Итоговый файл сохраняется в той же директории с именем `FP_SNPs_10k_GB38_twoAllelsFormat.tsv`.

Режим `--step validate` запускается с указанием аргументов `--input`, `--output`. Аргумент `--input` требует 2 переменные: файл `FP_SNPs_10k_GB38_twoAllelsFormat.tsv` и директорию `GRCh38` с проиндексированными хромосомами. Аргумент `--output` требует имя конечного файла (например, `validated_SNP.tsv` или `./validated/validated_SNP.tsv`). Итоговый tsv-файл и лог-файл с результатами работы сохраняются в `--output` директории.
  
## Подготовительный этап для предобработки (--step preprocess)

1. Скачайте архив GRCh38.d1.vd1.fa.tar.gz и разархивируйте командой

tar -xzvf GRCh38.d1.vd1.fa.tar.gz

2. Укажите путь к FASTA-файлу

FASTA="GRCh38.d1.vd1.fa"

3. Укажите список нужных хромосом

CHROMS=("chr1" "chr2" "chr3" "chr4" "chr5" "chr6" "chr7" "chr8" "chr9" "chr10" \
        "chr11" "chr12" "chr13" "chr14" "chr15" "chr16" "chr17" "chr18" "chr19" \
        "chr20" "chr21" "chr22" "chrX" "chrY" "chrM")

4. Создайте выходную директорию

OUTDIR="chromosomes"

mkdir -p "$OUTDIR"

5. Индексируйте исходный FASTA-файл (один раз)

samtools faidx "$FASTA"

6. Извлеките и проиндексируйте хромосомы по отдельности

for chr in "${CHROMS[@]}"; do echo "Извлечение $chr..."; samtools faidx "$FASTA" "$chr" > "${OUTDIR}/${chr}.fa"; samtools faidx "${OUTDIR}/${chr}.fa"; done


## Запуск предобработки (--step preprocess)

python3 FP_SNPs_script.py \
  --step preprocess \
  --input FP_SNPs.txt
  
По результатам работы файл `FP_SNPs_10k_GB38_twoAllelsFormat.tsv` будет сохранён в той же директории, что и исходный (`FP_SNPs.txt`).

## Запуск валидации (--step validate) 

python3 FP_SNPs_script.py \
  --step validate \
  --input FP_SNPs_10k_GB38_twoAllelsFormat.tsv chromosomes \
  --output validated_SNP.tsv

По результатам работы файлы `validated_SNP.tsv` и `validated_SNP.log` будут сохранены в --output директории 

## Результат

По итогам работы скрипта получается 3 файла:
-  .tsv-файл после предобработки (`--step preprocess`) `FP_SNPs_10k_GB38_twoAllelsFormat.tsv`
-  .tsv-файл после валидации (`--step validate`) (например, validated_SNP.tsv)
-  .log-файл после валидации (`--step validate`) (например, validated_SNP.log)
