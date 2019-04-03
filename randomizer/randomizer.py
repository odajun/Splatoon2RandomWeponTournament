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

def choiceUserweapon(weapon_set, user_weapon_list, num):
    duplicated_weapon = True
    weapon = ""
    while duplicated_weapon :
        weapon = random.choice(user_weapon_list)
        duplicated_weapon = False
        for selected_weapon_line in weapon_set :
            if selected_weapon_line[num] == weapon :
                duplicated_weapon = True
                break
    return weapon

def choiceTeamweapon(weapon_set, user_weapon_list):
    weapon_line = []
    for i in range(len(user_weapon_list)) :
        duplicated_weapon = True
        while duplicated_weapon :
            weapon = choiceUserweapon(weapon_set, user_weapon_list[i], i)
            if weapon not in weapon_line :
                duplicated_weapon = False
        weapon_line.append(weapon)
    return weapon_line

def getweaponTypeList():
    weapon_set = []
    weapon_type_list = ["blaster", "charger", "manuver", "roller_brush", "shelter", "shooter", "shooter2", "slosher", "splatling"]
    user_weapon_list = []
    for i in range(4) :
        user_weapon_list.append(copy.deepcopy(weapon_type_list))

    # 1週目はランダムに選ぶ
    weapon_set.append(random.sample(weapon_type_list, 4))
    # 選んだ武器種を候補リストから削除
    for i in range(len(user_weapon_list)) :
        user_weapon_list[i].remove(weapon_set[0][i])

    # 2週目以降
    for i in range(1, 5):
        weapon_line = choiceTeamweapon(weapon_set, user_weapon_list)
        for j in range(len(user_weapon_list)) :
            user_weapon_list[j].remove(weapon_line[j])
        weapon_set.append(weapon_line)
    return weapon_set

def choiceweapon(weapon_type):
    weapon_set = []
    for i in weapon_type :
        weapon_list = []
        for j in i :
            path = "./weapons/" + j + "_file.txt"
            weapon_list.append(random.choice(readFileToList(path)))
        weapon_set.append(weapon_list)
    return weapon_set

def init_result():
    global result_set
    result_set = []
    rule_list = ["ナワバリ", "ガチエリア", "ガチアサリ", "ガチホコ", "ガチヤグラ"]
    path = "./stage.txt"
    stage_list = readFileToList(path)
    random.shuffle(rule_list)
    weapon_set = getweaponTypeList()
    alpha_weapon_type = getweaponTypeList()
    bravo_weapon_type = getweaponTypeList()

    alpha_weapon_list = choiceweapon(alpha_weapon_type)
    bravo_weapon_list = choiceweapon(bravo_weapon_type)

    result_set.append(rule_list)
    result_set.append(alpha_weapon_list)
    result_set.append(bravo_weapon_list)
    result_set.append(random.sample(stage_list,5))
    return

def setAlphaMember(name):
    path = "./teams/" + name + ".txt"
    global alpha_member
    alpha_member = readFileToList(path)
    global alpha_team_name
    alpha_team_name = alpha_member[0]
    alpha_member = alpha_member[1:]


def setBravoMember(name):
    path = "./teams/" + name + ".txt"
    global bravo_member
    bravo_member = readFileToList(path)
    global bravo_team_name
    bravo_team_name = bravo_member[0]
    bravo_member = bravo_member[1:]

def setTeamMember(name):
    path = "./teams/" + name + ".txt"
    return readFileToList(path)

def getOutputText(weapon_list, member_list):
    text = ""
    for i in range(len(member_list)) :
        text = text + member_list[i] + " : " + weapon_list[i] + "\n"
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

def weaponCheck(weapon_set):
    text = ""
    for i in range(len(weapon_set)) :
        text = text + str(i+1) + "ゲーム目の武器種の組み合わせ"
        if is_unique(weapon_set[i]) :
            text = text + "は重複なし\n"
        else :
            text = text + "に重複を確認\n"
            text = text + ",".join(weapon_set[i]) + "\n"

    user_weapon_set = [[],[],[],[]]
    for i in range(len(weapon_set)) :
        for j in range(len(user_weapon_set)) :
            user_weapon_set[j].append(weapon_set[i][j])
        
    for i in range(len(user_weapon_set)) :
        text = text + str(i+1) + "人目の武器種の組み合わせ"
        if is_unique(user_weapon_set[i]): 
            text = text + "は重複なし\n"
        else :
            text = text + "に重複を確認\n"
            text = text + ",".join(user_weapon_set[i]) + "\n"

    return text
        
client = discord.Client()
alpha_member = []
bravo_member = []
result_set = []

debug = True
if debug :
    setAlphaMember("A")
    setBravoMember("B")
    init_result()
    #pprint(setAlphaMember)
    #pprint(setBravoMember)
    #pprint(result_set)

    print(weaponCheck(result_set[1]))
    print(weaponCheck(result_set[2]))

    delimiter = "xxx-------------------------------------xxx\n"
    for i in range(len(result_set[0])) :
        rule_text = str(i+1) + "試合目のバトルルール : 「" + result_set[0][i] + "」\n"
        stage_text = str(i+1) + "試合目のバトルステージ : 「" + result_set[3][i] + "」\n"
        header_text = delimiter + rule_text + stage_text + delimiter
        alpha_text = str(i+1) + "試合目のチーム " + alpha_team_name + " の武器\n\n" + getOutputText(result_set[1][i], getAlphaMembers())
        bravo_text = str(i+1) + "試合目のチーム " + bravo_team_name + " の武器\n\n" + getOutputText(result_set[2][i], getBravoMembers())
        print(delimiter + rule_text + stage_text + delimiter + alpha_text + delimiter + bravo_text + delimiter)

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
                print(weaponCheck(result_set[1]))
                print(weaponCheck(result_set[2]))
                reply = 'ランダマイザーの内容をリセットしました'
                await client.send_message(message.channel, reply)

    if message.content.startswith('1st') or message.content.startswith('2nd') or message.content.startswith('3rd') or message.content.startswith('4th') or message.content.startswith('5th') :
        if message.channel.id == config['text_id']['general'] :
            if message.author.id == config['user_id']['host'] :
                game_num = int(message.content[0])
                result_set = getResultSet()
                delimiter = "xxx-------------------------------------xxx\n"
                card_text = alpha_team_name + " vs " + bravo_team_name + "\n"
                rule_text = str(game_num) + "試合目のバトルルール : 「" + result_set[0][game_num - 1] + "」\n"
                stage_text = str(game_num) + "試合目のバトルステージ : 「" + result_set[3][game_num - 1] + "」\n"
                header_text = delimiter + card_text + rule_text + stage_text + delimiter
                await client.send_message(client.get_channel(config['text_id']['general']), header_text)
                announce_text = delimiter + "ギア選択に移ってよければチームの通知部屋で ok とtype してください。\n"
                announce_text = announce_text + "ワイルドカードを使用する場合は\n「xxx がワイルドカードを使用します」とtype してください。\n "
                footer_text = announce_text + delimiter
                alpha_text = header_text + str(game_num) + "試合目のチーム「" + alpha_team_name + "」の武器\n\n" + getOutputText(result_set[1][game_num - 1], getAlphaMembers()) + footer_text
                await client.send_message(client.get_channel(config['text_id']['alpha']), alpha_text)
                bravo_text = header_text + str(game_num) + "試合目のチーム「" + bravo_team_name + "」の武器\n\n" + getOutputText(result_set[2][game_num - 1], getBravoMembers()) + footer_text
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
