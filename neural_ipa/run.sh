#!/bin/bash

if [ "$1" = "train" ]; then
	python run.py train --train-src=./word_ipa_data/train.word --train-tgt=./word_ipa_data/train.ipa --dev-src=./word_ipa_data/dev.word --dev-tgt=./word_ipa_data/dev.ipa --vocab=vocab.json --cuda
elif [ "$1" = "toy-train"]; then
	python run.py train --train-src=./word_ipa_data/toy_train.word --train-tgt=./word_ipa_data/toy_train.ipa --dev-src=./word_ipa_data/toy_dev.word --dev-tgt=./word_ipa_data/toy_dev.ipa --vocab=toy_vocab.json --cuda
elif [ "$1" = "test" ]; then
    python run.py decode model.bin ./word_ipa_data/test.word ./word_ipa_data/test.ipa outputs/test_outputs.txt --cuda
elif [ "$1" = "toy-test"]; then
	python run.py decode model.bin ./word_ipa_data/toy_test.word ./word_ipa_data/toy_test.ipa outputs/toy_test_outputs.txt --cuda
elif [ "$1" = "vocab" ]; then
	python vocab.py --train-src=./word_ipa_data/train.word --train-tgt=./word_ipa_data/train.ipa vocab.json
elif [ "$1" = "toy-vocab"]; then
	python vocab.py --train-src=./word_ipa_data/toy_train.word --train-tgt=./word_ipa_data/toy_train.ipa toy_vocab.json
else
	echo "Invalid Option Selected"
fi