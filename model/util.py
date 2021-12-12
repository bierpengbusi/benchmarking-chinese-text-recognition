import torch
from data.lmdbReader import lmdbDataset, resizeNormalize
from config import config
import os
import shutil
from shutil import copyfile
from torch.utils.data import Dataset

#----------alphabet----------
alphabet_character_file = open(config['alpha_path'])
alphabet_character = list(alphabet_character_file.read().strip())
alphabet_character_raw = ['START']
for item in alphabet_character:
    alphabet_character_raw.append(item)
alphabet_character_raw.append('END')
alphabet_character = alphabet_character_raw

alp2num_character = {}
for index, char in enumerate(alphabet_character):
    alp2num_character[char] = index


def get_dataloader(root,shuffle=False):
    dataset = lmdbDataset(root, resizeNormalize((config['imageW'], config['imageH'])))
    dataloader = torch.utils.data.DataLoader(
        dataset, batch_size=config['batch'], shuffle=shuffle, num_workers=8,
    )
    return dataloader, dataset

def get_data_package():
    train_dataset = []
    for dataset_root in config['train_dataset'].split(','):
        _ , dataset = get_dataloader(dataset_root,shuffle=True)
        train_dataset.append(dataset)
    train_dataset_total = torch.utils.data.ConcatDataset(train_dataset)

    train_dataloader = torch.utils.data.DataLoader(
        train_dataset_total, batch_size=config['batch'], shuffle=True, num_workers=8,
    )

    test_dataset = []
    for dataset_root in config['test_dataset'].split(','):
        _ , dataset = get_dataloader(dataset_root,shuffle=True)
        test_dataset.append(dataset)
    test_dataset_total = torch.utils.data.ConcatDataset(test_dataset)

    test_dataloader = torch.utils.data.DataLoader(
        test_dataset_total, batch_size=config['batch'], shuffle=False, num_workers=8,
    )


    return train_dataloader, test_dataloader


def converter(label):
    "Convert string label to tensor"

    string_label = label
    label = [i for i in label]
    alp2num = alp2num_character

    batch = len(label)
    length = torch.Tensor([len(i) for i in label]).long().cuda()
    max_length = max(length)

    text_input = torch.zeros(batch, max_length).long().cuda()
    for i in range(batch):
        for j in range(len(label[i]) - 1):
            text_input[i][j + 1] = alp2num[label[i][j]]

    sum_length = sum(length)
    text_all = torch.zeros(sum_length).long().cuda()
    start = 0
    for i in range(batch):
        for j in range(len(label[i])):
            if j == (len(label[i])-1):
                text_all[start + j] = alp2num['END']
            else:
                text_all[start + j] = alp2num[label[i][j]]
        start += len(label[i])

    return length, text_input, text_all, string_label

def get_alphabet():
    return alphabet_character

def tensor2str(tensor):
    alphabet = get_alphabet()
    string = ""
    for i in tensor:
        if i == (len(alphabet)-1):
            continue
        string += alphabet[i]
    return string

def saver():
    try:
        shutil.rmtree('./history/{}'.format(config['exp_name']))
    except:
        pass
    os.mkdir('./history/{}'.format(config['exp_name']))

    src = './train.py'
    dst = os.path.join('./history', config['exp_name'], 'train.py')
    copyfile(src, dst)

    src = './util.py'
    dst = os.path.join('./history', config['exp_name'], 'util.py')
    copyfile(src, dst)

    src = './config.py'
    dst = os.path.join('./history', config['exp_name'], 'config.py')
    copyfile(src, dst)

    src = './model/TransformerSTR.py'
    dst = os.path.join('./history', config['exp_name'], 'TransformerSTR.py')
    copyfile(src, dst)

    src = './model/TransformerUtil.py'
    dst = os.path.join('./history', config['exp_name'], 'TransformerUtil.py')
    copyfile(src, dst)

    src = './model/ResNet.py'
    dst = os.path.join('./history', config['exp_name'], 'ResNet.py')
    copyfile(src, dst)
