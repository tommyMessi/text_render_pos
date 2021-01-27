import  os

path = '/home/luoxilun/text_renderer_2.0/data/corpus/date_data/filter_data.txt'

def read_dict(path):
    with open(path, 'r', encoding='utf-8') as file1:
        d = file1.read().splitlines()
    return d

def write_url(path, url):
    with open(path, 'a', encoding='utf-8') as file:
        file.write(url + '\n')
        file.close()

d = read_dict(path)
d_2 = sorted(d,key = lambda i:len(i),reverse=False)
for line in d_2:
    print(line)
    write_url('/home/luoxilun/text_renderer_2.0/data/corpus/date_data/sort_data.txt',line)




