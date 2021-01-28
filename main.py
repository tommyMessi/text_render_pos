#!/usr/env/bin python3

"""
Generate training and test images with position.
"""
import traceback
import numpy as np
import random
from collections import Counter
import multiprocessing as mp
from itertools import repeat
import os

import cv2

from libs.config import load_config
from libs.timer import Timer
from parse_args import parse_args
import libs.utils as utils
import libs.font_utils as font_utils
from textrenderer.corpus.corpus_utils import corpus_factory
from textrenderer.renderer import Renderer
from tenacity import retry
os.environ['PYTHONWARNINGS'] = 'ignore:semaphore_tracker:UserWarning'

lock = mp.Lock()
counter = mp.Value('i', 0)
STOP_TOKEN = 'kill'

flags = parse_args()
cfg = load_config(flags.config_file)

fonts = font_utils.get_font_paths_from_list(flags.fonts_list)
bgs = utils.load_bgs(flags.bg_dir)

corpus = corpus_factory(flags.corpus_mode, flags.chars_file, flags.corpus_dir, flags.length)

renderer = Renderer(corpus, fonts, bgs, cfg,
                    height=flags.img_height,
                    width=flags.img_width,
                    clip_max_chars=flags.clip_max_chars,
                    debug=flags.debug,
                    gpu=flags.gpu,
                    strict=flags.strict)


def start_listen(q, fname):
    """ listens for messages on the q, writes to file. """

    f = open(fname, mode='a', encoding='utf-8')
    save_path = os.path.realpath(os.path.dirname(fname))
    while 1:
        m = q.get()
        if m == STOP_TOKEN:
            break
        try:
            m_str = str(m)
            space_index = m_str.find(' ')
            img_name = m_str[:space_index] + '.jpg'
            img_label = m_str[space_index + 1:]
            line = os.path.join(save_path, img_name) + '\t' + img_label
            f.write(str(line) + '\n')
        except:
            traceback.print_exc()

        with lock:
            if counter.value % 1000 == 0:
                f.flush()
    f.close()


@retry
def gen_img_retry(renderer, img_index):
    try:
        return renderer.gen_img(img_index)
    except Exception as e:
        print("Retry gen_img: %s" % str(e))
        traceback.print_exc()
        raise Exception


def image_similar_scan(image_o_s):
    k = random.randint(3, 7)
    index_v = np.argwhere(image_o_s < 255)
    color = Counter(image_o_s.flatten()).most_common(1)[0][0] if Counter(image_o_s.flatten()).most_common(1)[0][
                                                                     0] > 0 else 0
    for i in range(len(index_v)):
        if random.randint(0, k) == 2:
            image_o_s[index_v[i][0]][index_v[i][1]] = color
    return image_o_s


def generate_img(img_index, q=None):
    global flags, lock, counter
    # Make sure different process has different random seed
    np.random.seed()

    im, word, split_lines = gen_img_retry(renderer, img_index)
    # ran_int = random.randint(0, 5)
    #
    # if ran_int == 3:
    #     im = image_similar_scan(im)
    base_name = '{:08d}'.format(img_index)

    if not flags.viz:
        fname = os.path.join(flags.save_dir, base_name + '.jpg')
        quality = np.random.randint(40, 90)
        # im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(fname, im, [int(cv2.IMWRITE_JPEG_QUALITY), quality])

        # 增加位置信息的输出
        label = "{} {}\t{}".format(base_name, word, ",".join([str(split_line)for split_line in split_lines[1:]]))

        if q is not None:
            q.put(label)

        with lock:
            counter.value += 1
            print_end = '\n' if counter.value == flags.num_img else '\r'
            if counter.value % 100 == 0 or counter.value == flags.num_img:
                print("{}/{} {:2d}%".format(counter.value,
                                            flags.num_img,
                                            int(counter.value / flags.num_img * 100)),
                      end=print_end)
    else:
        utils.viz_img(im)


def sort_labels(tmp_label_fname, label_fname):
    lines = []
    with open(tmp_label_fname, mode='r', encoding='utf-8') as f:
        lines = f.readlines()

    lines = sorted(lines)
    with open(label_fname, mode='w', encoding='utf-8') as f:
        for line in lines:
            f.write(line[9:])


def restore_exist_labels(label_path):
    # 如果目标目录存在 labels.txt 则向该目录中追加图片
    start_index = 0
    if os.path.exists(label_path):
        start_index = len(utils.load_chars(label_path))
        print('Generate more text images in %s. Start index %d' % (flags.save_dir, start_index))
    else:
        print('Generate text images in %s' % flags.save_dir)
    return start_index


def get_num_processes(flags):
    processes = flags.num_processes
    if processes is None:
        processes = max(os.cpu_count(), 2)
    return processes


if __name__ == "__main__":
    # It seems there are some problems when using opencv in multiprocessing fork way
    # https://github.com/opencv/opencv/issues/5150#issuecomment-161371095
    # https://github.com/pytorch/pytorch/issues/3492#issuecomment-382660636
    if utils.get_platform() == "OS X":
        mp.set_start_method('spawn', force=True)

    if flags.viz == 1:
        flags.num_processes = 1

    tmp_label_path = os.path.join(flags.save_dir, 'big_tmp_labels.txt')
    label_path = os.path.join(flags.save_dir, 'big_labels.txt')

    manager = mp.Manager()
    q = manager.Queue()

    start_index = restore_exist_labels(label_path)

    timer = Timer(Timer.SECOND)
    timer.start()
    with mp.Pool(processes=get_num_processes(flags)) as pool:
        if not flags.viz:
            pool.apply_async(start_listen, (q, tmp_label_path))

        pool.starmap(generate_img, zip(range(start_index, start_index + flags.num_img), repeat(q)))

        q.put(STOP_TOKEN)
        pool.close()
        pool.join()
    timer.end("Finish generate data")

    if not flags.viz:
        sort_labels(tmp_label_path, label_path)
