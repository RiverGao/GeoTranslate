#!/bin/bash

if [ "$1" = "train" ]; then
	train --train-src=./word_ipa_data/train.word --train-tgt=./word_ipa_data/train.ipa --dev-src=./word_ipa_data/dev.word --dev-tgt=./word_ipa_data/dev.ipa --vocab=vocab.json --cuda
    train --train-src=./word_ipa_data/toy_train.word --train-tgt=./word_ipa_data/toy_train.ipa --dev-src=./word_ipa_data/toy_dev.word --dev-tgt=./word_ipa_data/toy_dev.ipa --vocab=toy_vocab.json --cuda
elif [ "$1" = "test" ]; then
    decode model.bin ./word_ipa_data/test.word ./word_ipa_data/test.ipa outputs/test_outputs.txt --cuda
    decode model.bin ./word_ipa_data/toy_test.word ./word_ipa_data/toy_test.ipa outputs/toy_test_outputs.txt --cuda
elif [ "$1" = "vocab" ]; then
	--train-src=./word_ipa_data/train.word --train-tgt=./word_ipa_data/train.ipa vocab.json
	--train-src=./word_ipa_data/toy_train.word --train-tgt=./word_ipa_data/toy_train.ipa toy_vocab.json
else
	echo "Invalid Option Selected"
fi
