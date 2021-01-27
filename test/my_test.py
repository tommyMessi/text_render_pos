# coding: utf-8
import os
import codecs

def output_fonts_file(root_dir, save_path):
    font_name_list = os.listdir(root_dir)
    with codecs.open(save_path, "w", encoding='utf-8') as f:
        for i, font_name in enumerate(font_name_list):
            font_path = os.path.join(root_dir, font_name)
            f.write(font_path)
            if i < len(font_name_list) - 1:
                f.write('\n')

if __name__ == '__main__':
    root_dir = './data/fonts/eng'
    save_path = './data/fonts_list/eng_list.txt'
    output_fonts_file(root_dir, save_path)
