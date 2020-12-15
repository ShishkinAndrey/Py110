import random
import re
import json
import csv

import argparse
from faker import Faker

import conf

PK_FILE = 'books.txt'
AUTHOR_FILE = 'authors.txt'


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, required=True, help='Кол-во случайных элементов, которое необходимо сгенерировать')
    parser.add_argument('--authors', type=int, required=False, help='Кол-во авторов для каждого элемента')
    parser.add_argument('--sale', type=int, required=False, help='Скидка')
    parser.add_argument('--output', required=False, help='Формат вывода(.json / .csv')
    subparsers = parser.add_subparsers(dest='json_csv')
    subparsers_json(subparsers)
    subparsers_csv(subparsers)
    return parser


def subparsers_json(subparsers):
    save_json = subparsers.add_parser('json', help='Введите json для записи в .json файл')
    save_json.add_argument('-jsfn', required=False, type=argparse.FileType('w'), help='Имя .json файла')
    save_json.add_argument('--indent', required=False, type=int, default=0, help='Размер отступов')
    return save_json


def subparsers_csv(subparsers):
    save_csv = subparsers.add_parser('csv', help='Введите csv для записи в .json файл')
    save_csv.add_argument('--csvname', required=False, type=argparse.FileType('w'), help='Имя .csv файла')
    return save_csv


def get_authors():
    '''
    Функция, выполняющая проверку файла authors.txt на соответствие регулярному выражению
    :return: список, содержащий корректные строки
    '''
    reg_author = re.compile(r'\b[A-Z][a-z]*\b\s[A-Z][a-z]*\b')
    with open(AUTHOR_FILE, 'rt') as f:
        author_list = []
        i = 0
        for line in f:
            i += 1
            if re.match(reg_author, line):
                author_list.append(line[:line.index('\n')])
            else:
                print('Строка', line[:line.index("\n")], 'номер', i, 'не прошла проверку', )
    return author_list


def decorator_func(fn):
    def wrapper():
        res_func = fn()
        return next(res_func)['model']
    return wrapper


@decorator_func
def gen_book():
    dict_book = {}
    pk_value = 1
    title_number = 0
    fake = Faker()
    author_list = get_authors()
    while True:
        dict_book['model'] = conf.model
        dict_book['pk'] = pk_value
        dict_book['fields'] = {}
        with open(PK_FILE, 'rt') as f:
            title_list = f.read().splitlines()
        dict_book['fields']['title'] = title_list[title_number]
        dict_book['fields']['year'] = random.randint(1900, 2020)
        dict_book['fields']['pages'] = random.randint(1, 1000)
        dict_book['fields']['isbn13'] = fake.isbn13()
        dict_book['fields']['rating'] = round(random.uniform(0, 5), 1)
        dict_book['fields']['price'] = round(random.uniform(10, 100), 2)
        if args.sale:
            dict_book['fields']['discount'] = args.sale
        else:
            dict_book['fields']['discount'] = random.randint(1, 100)
        if args.authors:
            dict_book['fields']['author'] = [random.choice(author_list) for _ in range(args.authors)]
        else:
            dict_book['fields']['author'] = [random.choice(author_list) for _ in range(random.randint(1, 3))]
        yield dict_book
        pk_value += 1
        title_number += 1

if __name__ == '__main__':
    result = gen_book()
    parser = create_parser()
    args = parser.parse_args()
    if args.json_csv == 'json':
        for _ in range(args.count):
            json.dump(next(result), args.jsfn, indent=args.indent)
    elif args.json_csv == 'csv':
        my_list = []
        list_fieldnames = []
        i = 0
        updated_dict = next(result)
        for fieldnames in updated_dict.keys():
            list_fieldnames.append(fieldnames)
        for fields_keys in updated_dict.get('fields').keys():
            list_fieldnames.append(fields_keys)
        # работающий вариант!!!
        while i != args.count:
            updated_dict.update(updated_dict.pop('fields'))
            my_list.append(updated_dict)
            csv_writer(args.csvname.name, list_fieldnames, my_list)
            my_list.clear()
            i += 1
            updated_dict = next(result)
    else:
        for _ in range(args.count):
            print(next(result))
