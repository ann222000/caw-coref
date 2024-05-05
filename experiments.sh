set -e  # any error will cause the script to exit immediately
# original_dir = wl_coref
# arg $1 = epoch

for part in 0 0.2 0.4 0.6 0.8 1
do
   echo "English + $part part of dutch dataset" >> results.txt
   cp data/english_train_head.jsonlines data/temp.jsonlines
   python mix.py $part
   python run.py train xlm_roberta
   python run.py eval xlm_roberta --data-split test
   python calculate_conll.py xlm_roberta test $1 >> results.txt
   rm data/temp.jsonlines
done

"""
Цикл
for part in [0, 0.2, 0.4, 0.6, 0.8, 1]
echo English + {100 * part} dutch >> results.txt
cp data/english_train_head.jsonlines data/temp.jsonlines
python mix.py {part}
#TODO поправить датасеты + эпохи в config.toml

python run.py train xlm_roberta

Download and save the pretrained model to the data directory Майоров спросить???
python run.py eval xlm_roberta --data-split test

# last arg number of epochs
#TODO добавить в скрипт вывод нужных метрик
python calculate_conll.py xlm_roberta test 20 >> results.txt
rm data/temp.jsonlines

results.txt должен содержать пропроции, precision, recall, F1, muc, B3, ceaf, avg
"""