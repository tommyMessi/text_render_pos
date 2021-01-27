import os
import json

labels_path = r'/home/huluwa/sample_crnn/text_renderer_2.0/output/training_eng/big_tmp_labels.txt'
new_labels_path = r'/home/huluwa/sample_crnn/text_renderer_2.0/output/new_labels.txt'

char_path = r'/home/huluwa/sample_crnn/text_renderer_2.0/output/lexicon_fix.txt'

with open(char_path, 'r') as f_char:
    char_list = f_char.readlines()
    char_list = [x.replace('\n','') for x in char_list]

new_list = []
with open(labels_path, 'r') as f:
    data = f.readlines()
    # print(data)
    for str_char in data:
        # print(str_char)
        char_s = str_char.split('\t')[1]

        K = 1
        for c in char_s:
            if c in char_list:
                pass
            else:
                print(str_char)
                K = 0
                break
        if K == 0:
            continue
        new_list.append(str_char)

print(new_list)

with open(new_labels_path, 'a') as f_new:
    for new_char in new_list:
        f_new.write(new_char)





