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
    had_wepon = True
    wepon = ""
    while had_wepon :
        wepon = random.choice(user_wepon_list)
        had_wepon = False
        for selected_wepon_line in wepon_set :
            if selected_wepon_line[num] == wepon :
                had_wepon = True
                break
    return wepon

def choiceTeamWepon(wepon_set, user_wepon_list):
    wepon_line = []
    for i in range(len(user_wepon_list)) :
        wepon = choiceUserWepon(wepon_set, user_wepon_list[i], i)
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
    random.shuffle(rule_list)
    wepon_set = getWeponTypeList()
    game_num = 5
    alpha_wepon_type = random.sample(wepon_set, game_num)
    bravo_wepon_type = random.sample(wepon_set, game_num)

    alpha_wepon_list = choiceWepon(alpha_wepon_type)
    bravo_wepon_list = choiceWepon(bravo_wepon_type)

    result_set.append(rule_list)
    result_set.append(alpha_wepon_list)
    result_set.append(bravo_wepon_list)
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


client = discord.Client()
alpha_member = []
bravo_member = []
result_set = []

debug = False
if debug == True :
    setAlphaMember("a")
    setBravoMember("b")
    init_result()
    pprint(setAlphaMember)
    pprint(setBravoMember)
    pprint(result_set)
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
                reply = 'ランダマイザーの内容をリセットしました'
                await client.send_message(message.channel, reply)

    if message.content.startswith('1st') or message.content.startswith('2nd') or message.content.startswith('3rd') or message.content.startswith('4th') or message.content.startswith('5th') :
        if message.channel.id == config['text_id']['general'] :
            if message.author.id == config['user_id']['host'] :
                game_num = int(message.content[0])
                result_set = getResultSet()
                rule_text = str(game_num) + "試合目のバトルルール : " + result_set[0][game_num - 1] + "\n"
                await client.send_message(client.get_channel(config['text_id']['general']), rule_text)
                announce_text = "ギア選択に移ってよければチームの通知部屋で ok とtype してください。\n"
                alpha_text = rule_text + str(game_num) + "試合目のアルファチームの武器\n" + getOutputText(result_set[1][game_num - 1], getAlphaMembers()) + announce_text
                await client.send_message(client.get_channel(config['text_id']['alpha']), alpha_text)
                bravo_text = rule_text + str(game_num) + "試合目のブラボーチームの武器\n" + getOutputText(result_set[2][game_num - 1], getBravoMembers()) + announce_text
                await client.send_message(client.get_channel(config['text_id']['bravo']), bravo_text)

    if message.content.startswith('ok') :
        if message.channel.id == config['text_id']['alpha'] or message.channel.id == config['text_id']['bravo'] :
            text = "幸運を祈る(=_=)b"
            await client.send_message(message.channel, text)

    if 'ワイルドカード' in message.content :
        if message.channel.id == config['text_id']['alpha'] or message.channel.id == config['text_id']['bravo'] :
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
