# FP_SNPs_script.py

Скрипт предназначен для предобработки и валидации SNP-маркеров на основе референсного генома человека (GRCh38) и работает в двух режимах:

- **Предобработка** (`--step preprocess`)  
Преобразует исходный файл `FP_SNPs.txt` в формат `.tsv`, необходимый для последующей валидации.
  
- **Валидация** (`--step validate`)  
Проверяет, соответствует ли allele1 и allele2 референсному значению в сборке GRCh38. При необходимости меняет местами REF и ALT. SNPs, у которых ни один аллель не совпадает с референсом, исключаются.

Режим `--step preprocess` запускается только с указанием аргумента `--input`. Аргумент `--input` требует файл `FP_SNPs.txt`. Итоговый файл сохраняется в той же директории с именем `FP_SNPs_10k_GB38_twoAllelsFormat.tsv`.

Режим `--step validate` запускается с указанием аргументов `--input`, `--output`. Аргумент `--input` требует 2 переменные: файл `FP_SNPs_10k_GB38_twoAllelsFormat.tsv` и директорию `GRCh38` с проиндексированными хромосомами. Аргумент `--output` требует имя конечного файла (например, `validated_SNP.tsv` или `./validated/validated_SNP.tsv`). По окончании работы режима `--step validate` создаются `--output` файл и лог-файл с результатами работы в `--output` директории.

## Зависимости

- Python 3.6 или выше
- Библиотеки:
  - `pandas`
  - `pysam`
  
## Подготовительный этап для предобработки (--step preprocess)

1. Скачаем архив GRCh38.d1.vd1.fa.tar.gz и разархивируем командой

tar -xzvf GRCh38.d1.vd1.fa.tar.gz

2. Создадим директорию GRCh38_split

mkdir GRCh38_split

3. Выполним разбивку файла GRCh38.d1.vd1.fa на отдельные файлы,
которые начинаются с символа '>', и повторим шаблон до конца файла '{*}'.
Файлы напраляются в директорию GRCh38_split

csplit -f GRCh38_split/chr GRCh38.d1.vd1.fa '/^>/' '{*}'

4. Создадим директорию GRCh38_main

mkdir GRCh38_main

5. Перенесем файлы с 25 хромосомами в директорию GRCh38_main

mv GRCh38_split/chr{1..22}.fa GRCh38_main  
mv GRCh38_split/chrX.fa GRCh38_main  
mv GRCh38_split/chrY.fa GRCh38_main  
mv GRCh38_split/chrM.fa GRCh38_main

6. Проиндексируем перенесенные хромосомы

for f in GRCh38_main/*.fa; do
    samtools faidx "$f"
done

## Запуск предобработки (--step preprocess)

python3 FP_SNPs_script.py \
  --step preprocess \
  --input FP_SNPs.txt
  
По результатам работы файл `FP_SNPs_10k_GB38_twoAllelsFormat.tsv` будет сохранён в той же директории, что и исходный (`FP_SNPs.txt`).

## Запуск валидации (--step validate) 

python3 FP_SNPs_script.py \
  --step validate \
  --input FP_SNPs_10k_GB38_twoAllelsFormat.tsv GRCh38_main \
  --output validated_SNP.tsv

По результатам работы файлы `validated_SNP.tsv` и `validated_SNP.log` будут сохранены в директории (GRCh38_main).  

## Результат

По итогам работы скрипта получается 3 файла:
-  .tsv-файл после предобработки (`--step preprocess`) `FP_SNPs_10k_GB38_twoAllelsFormat.tsv`
-  .tsv-файл после валидации (`--step validate`) (например, validated_SNP.tsv)
-  .log-файл после валидации (`--step validate`) (например, validated_SNP.log)
