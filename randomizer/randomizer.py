#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import discord
import sys
import copy
from configparser import ConfigParser
from pprint import pprint

config = ConfigParser()
config.read('./randomizer.ini')

def readFileToList(path):
	list = []
	f = open(path,'r')
	for line in f:
		line = line.strip()
		if line.startswith('#'):
			continue
		if len(line) == 0:
			continue
		list.append(line)
	f.close()
	return list

def choiceUserWepon(wepon_set, user_wepon_list, num):
    duplicated_wepon = True
    wepon = ""
    while duplicated_wepon :
        wepon = random.choice(user_wepon_list)
        duplicated_wepon = False
        for selected_wepon_line in wepon_set :
            if selected_wepon_line[num] == wepon :
                duplicated_wepon = True
                break
    return wepon

def choiceTeamWepon(wepon_set, user_wepon_list):
    wepon_line = []
    for i in range(len(user_wepon_list)) :
        duplicated_wepon = True
        while duplicated_wepon :
            wepon = choiceUserWepon(wepon_set, user_wepon_list[i], i)
            if wepon not in wepon_line :
                duplicated_wepon = False
        wepon_line.append(wepon)
    return wepon_line

def getWeponTypeList():
    wepon_set = []
    wepon_type_list = ["blaster", "charger", "manuver", "roller_brush", "shelter", "shooter", "slosher", "splatling"]
    user_wepon_list = []
    for i in range(4) :
        user_wepon_list.append(copy.deepcopy(wepon_type_list))

    # 1週目はランダムに選ぶ
    wepon_set.append(random.sample(wepon_type_list, 4))
    # 選んだ武器種を候補リストから削除
    for i in range(len(user_wepon_list)) :
        user_wepon_list[i].remove(wepon_set[0][i])

    # 2週目以降
    for i in range(1, 5):
        wepon_line = choiceTeamWepon(wepon_set, user_wepon_list)
        for j in range(len(user_wepon_list)) :
            user_wepon_list[j].remove(wepon_line[j])
        wepon_set.append(wepon_line)
    return wepon_set

def choiceWepon(wepon_type):
    wepon_set = []
    for i in wepon_type :
        wepon_list = []
        for j in i :
            path = "./wepons/" + j + "_file.txt"
            wepon_list.append(random.choice(readFileToList(path)))
        wepon_set.append(wepon_list)
    return wepon_set

def init_result():
    global result_set
    result_set = []
    rule_list = ["ナワバリ", "ガチエリア", "ガチアサリ", "ガチホコ", "ガチヤグラ"]
    path = "./stage.txt"
    stage_list = readFileToList(path)
    random.shuffle(rule_list)
    wepon_set = getWeponTypeList()
    alpha_wepon_type = getWeponTypeList()
    bravo_wepon_type = getWeponTypeList()

    alpha_wepon_list = choiceWepon(alpha_wepon_type)
    bravo_wepon_list = choiceWepon(bravo_wepon_type)

    result_set.append(rule_list)
    result_set.append(alpha_wepon_list)
    result_set.append(bravo_wepon_list)
    result_set.append(random.sample(stage_list,5))
    return

def setAlphaMember(name):
    path = "./teams/" + name + ".txt"
    global alpha_member
    alpha_member = readFileToList(path)

def setBravoMember(name):
    path = "./teams/" + name + ".txt"
    global bravo_member
    bravo_member = readFileToList(path)

def setTeamMember(name):
    path = "./teams/" + name + ".txt"
    return readFileToList(path)

def getOutputText(wepon_list, member_list):
    text = ""
    for i in range(len(member_list)) :
        text = text + member_list[i] + " : " + wepon_list[i] + "\n"
    return text

def getResultSet():
    global result_set
    return result_set

def getAlphaMembers():
    global alpha_member
    return alpha_member
        
def getBravoMembers():
    global bravo_member
    return bravo_member

def is_unique(seq):
    return len(seq) == len(set(seq))

def weponCheck(wepon_set):
    text = ""
    for i in range(len(wepon_set)) :
        text = text + str(i+1) + "ゲーム目の武器種の組み合わせ"
        if is_unique(wepon_set[i]) :
            text = text + "は重複なし\n"
        else :
            text = text + "に重複を確認\n"
            text = text + ",".join(wepon_set[i]) + "\n"

    user_wepon_set = [[],[],[],[]]
    for i in range(len(wepon_set)) :
        for j in range(len(user_wepon_set)) :
            user_wepon_set[j].append(wepon_set[i][j])
        
    for i in range(len(user_wepon_set)) :
        text = text + str(i+1) + "人目の武器種の組み合わせ"
        if is_unique(user_wepon_set[i]): 
            text = text + "は重複なし\n"
        else :
            text = text + "に重複を確認\n"
            text = text + ",".join(user_wepon_set[i]) + "\n"

    return text
        
client = discord.Client()
alpha_member = []
bravo_member = []
result_set = []

debug = False
if debug :
    setAlphaMember("a")
    setBravoMember("b")
    init_result()
    pprint(setAlphaMember)
    pprint(setBravoMember)
    pprint(result_set)

    print(weponCheck(result_set[1]))
    print(weponCheck(result_set[2]))
    sys.exit()
    

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    # reset,teamA,teamB という入力前提 
    # うまいやり方があれば変更する
    if message.content.startswith('reset,'):
        if message.channel.id == config['text_id']['general'] :
            if message.author.id == config['user_id']['host'] :
                contents = message.content.split(",")
                setAlphaMember(contents[1])
                setBravoMember(contents[2])
                init_result()
                result_set = getResultSet()
                print(weponCheck(result_set[1]))
                print(weponCheck(result_set[2]))
                reply = 'ランダマイザーの内容をリセットしました'
                await client.send_message(message.channel, reply)

    if message.content.startswith('1st') or message.content.startswith('2nd') or message.content.startswith('3rd') or message.content.startswith('4th') or message.content.startswith('5th') :
        if message.channel.id == config['text_id']['general'] :
            if message.author.id == config['user_id']['host'] :
                game_num = int(message.content[0])
                result_set = getResultSet()
                delimiter = "xxx-------------------------------------xxx\n"
                rule_text = str(game_num) + "試合目のバトルルール : 「" + result_set[0][game_num - 1] + "」\n"
                stage_text = str(game_num) + "試合目のバトルステージ : 「" + result_set[3][game_num - 1] + "」\n"
                header_text = delimiter + rule_text + stage_text + delimiter
                await client.send_message(client.get_channel(config['text_id']['general']), header_text)
                announce_text = delimiter + "ギア選択に移ってよければチームの通知部屋で ok とtype してください。\n"
                announce_text = announce_text + "ワイルドカードを使用する場合は\n「xxx がワイルドカードを使用します」とtype してください。\n "
                footer_text = announce_text + delimiter
                alpha_text = header_text + str(game_num) + "試合目のアルファチームの武器\n\n" + getOutputText(result_set[1][game_num - 1], getAlphaMembers()) + footer_text
                await client.send_message(client.get_channel(config['text_id']['alpha']), alpha_text)
                bravo_text = header_text + str(game_num) + "試合目のブラボーチームの武器\n\n" + getOutputText(result_set[2][game_num - 1], getBravoMembers()) + footer_text
                await client.send_message(client.get_channel(config['text_id']['bravo']), bravo_text)

    if message.content.startswith('ok') :
        if message.channel.id == config['text_id']['alpha'] or message.channel.id == config['text_id']['bravo'] :
            if message.author.id != client.user.id :
                text = "幸運を祈る(=_=)b"
                await client.send_message(message.channel, text)

    if 'ワイルドカード' in message.content :
        if message.channel.id == config['text_id']['alpha'] or message.channel.id == config['text_id']['bravo'] :
            if message.author.id != client.user.id :
                text = "一騎当千の活躍を期待する(=_=)b"
                await client.send_message(message.channel, text)

    if message.content.startswith('カモン') :
        if message.channel.id == config['text_id']['general'] :
            if message.author.id == config['user_id']['host'] :
                text = "皆さん general のボイスチャンネルにお集まりください\n"
                await client.send_message(client.get_channel(config['text_id']['alpha']), text)
                await client.send_message(client.get_channel(config['text_id']['bravo']), text)
                await client.send_message(message.channel, text)

client.run(config['access_token']['token'])
