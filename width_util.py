import os
import cv2

def read_dict(path):
    with open(path, 'r', encoding='utf-8') as file1:
        d = file1.read().splitlines()
    return d

def write_url(path, url):
    with open(path, 'a', encoding='utf-8') as file:
        file.write(url + '\n')
        file.close()

images = os.listdir('/home/luoxilun/train_test/val/')
labels = read_dict('/home/luoxilun/train_test/val/labels.txt')
labels_2 = read_dict('/home/luoxilun/train_test/val/tmp_labels.txt')


for label in labels:
    for image in images:
        if image in label:
            write_url('/home/luoxilun/train_test/val/new_labels.txt',label)

for label_2 in labels_2:
    for image in images:
        if image in label_2:
            write_url('/home/luoxilun/train_test/val/new_tmp_labels.txt', label_2)

