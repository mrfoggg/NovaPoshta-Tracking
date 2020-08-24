import json
import requests
import textwrap
import string
import re
import os
import pyperclip
from prettytable import PrettyTable

clear = lambda: os.system('clear')

Black="\033[0;30m"        # Black
Red="\033[0;31m" 
On_IRed="\033[0;101m"         # Red
Green="\033[0;32m"
IGreen = "\033[0;92m"
BGreen="\033[1;32m"        # Green
Yellow="\033[0;33m"       # Yellow
Blue="\033[0;34m"         # Blue
Purple="\033[0;35m"       # Purple
Cyan="\033[0;36m"         # Cyan
White="\033[0;37m"        # White
N = "\033[0m" # Reset
Color_Off="\033[0m"

width = 70
api_key = ''
url = 'https://api.novaposhta.ua/v2.0/json/'
print()
input("Нажмите любую клавишу чтобы вставить номера ТТНок из буфера обмена) - ")
ttnsInput = pyperclip.paste()
while ttnsInput.find("\n\n") != -1:
	ttnsInput = ttnsInput.replace("\n\n", "\n")

ttnsList = ttnsInput.strip().replace("\n\n", "\n").split("\n")

counterStrings = len(ttnsList)

print("Получено %s строк" % counterStrings)

phone = "0123456789"
phonenumber = ttnInput = "a"

while ( ((not (phonenumber.isdigit())) or len(phonenumber)!=10) and phone!='0' and phone!=''):
	print()
	phone = input("Введите номер отправителя или получателя \n(введите '1' чтобы вставить номер из буфера обмена, '0' чтобы выйти из программы, или нажмите Enter чтобы пропустить ввод номера и осуществить поиск только по ТТН) - ")
	if phone == "1":
		phone = pyperclip.paste()
		print(phone)
	translator = phone.maketrans('', '', string.punctuation)
	phonenumber = phone.translate(translator).replace(" ", "")
	phonenumber = ''.join(re.findall('\d+', phonenumber))
	print(phonenumber)
	if phonenumber.isdigit()==False and phone!='':
		print('\033[91m' + "Введены недопустимые символы" + '\033[0m')
	if phonenumber[0:2]=="38":
		phonenumber = phonenumber[2:]
	if len(phonenumber)!=10 and phone!='0' and phonenumber.isdigit()!=False:
		print('\033[91m' + "Вы ввели больше или меньше цифр номера" + '\033[0m')

print()


def MakeRequest(ttnsList, ttnones, phonenumber):
	dictTTNphone = {}
	data = 	{
	"apiKey": api_key,
	"modelName": "TrackingDocument",
	"calledMethod": "getStatusDocuments",
	"methodProperties": {
	    "Documents": []
	}
	}

	counter = 0
	if ttnones =='':
		for ttn in ttnsList:
			mail = ""
			if ttn.find("\t")!=-1:
				mail = ttn.split("\t")[1]
				if mail == "petryk@gmail.com":
					phonenumber = '0500000000'

				elif mail == "vasyl@gmail.com":
					phonenumber = '0630000000'	


				ttn = ttn.split("\t")[0]
			ttn = ttn.replace(" ", "")
			ttn = ''.join(re.findall('\d+', ttn))
			document = {
			"DocumentNumber": ttn,
			"Phone": phonenumber
			}
			data["methodProperties"]["Documents"].append(document)

			counter += 1
			dictTTNphone[ttn] = mail
		print("Обработано %s строк" % counter)
	else:
		data["methodProperties"]["Documents"].append({
			"DocumentNumber": ttnones,
			"Phone": phonenumber
			})


	request_json = json.dumps(data, indent = 4)
	response = requests.post(url, data = request_json)
	response_dict = json.loads(response.text)

	
	return [response_dict['data'] , dictTTNphone]



hundreds = counterStrings // 100

i = 0
info = []
dictTTNphone = {}
while i <= hundreds:
	request = MakeRequest(ttnsList[i*100: i*100+100], '', phonenumber)
	info += request[0]
	# print(request[1]+)
	dictTTNphone.update(request[1])
	i += 1

print()
def PrintTable(info, dictTTNphone):
	statuses = {}
	table = PrettyTable ()
	table.field_names =["Дата созд.", "Ожид. дата приб.", "Город отрп.", "Город получ", "ФИО",  "ТТН", 'Вес', 'Наложка', "Статус посылки", "Код стат", "Дата см. статуса"]
	table.align["Город отрп."] = table.align["Город получ"] = table.align["Статус"] = "l"
	statuses_list = []
	for statusTTN in info:
		if statusTTN['StatusCode'] == '2' or statusTTN['StatusCode'] == '3':
			statusTTN['CitySender'] = statusTTN['CityRecipient'] = statusTTN['DateScan'] = statusTTN['Redelivery'] = statusTTN['RedeliverySum'] = statusTTN['ScheduledDeliveryDate'] = statusTTN['DocumentWeight'] = "---"


		if len(str(statusTTN['Status']))>width:
			statusTTN['Status'] = textwrap.fill(statusTTN['Status'], width)
		try:
			DateCreated = statusTTN['DateCreated'][:-3]
		except:
			DateCreated = "HZZ"

		try:
			fio = textwrap.fill(statusTTN['RecipientFullNameEW'], 28)
			if statusTTN['StatusCode'] == '7' or statusTTN['StatusCode'] == '102' or statusTTN['StatusCode'] == '103' or statusTTN['StatusCode'] == '108':
				fio += ("\n" + statusTTN['PhoneRecipient'])
		except:
			fio =  "Скрыто (не указан номер)"

			# statusTTN['DateCreated'] = "hz"
		if statusTTN['StatusCode'] == '1':
			statusTTN['Status'] = Yellow + "Не отправлена" + Color_Off

		elif statusTTN['StatusCode'] == '5':
			statusTTN['Status'] = Blue + "В пути" + Color_Off
			
		elif statusTTN['StatusCode'] == '10':
			statusTTN['Status'] = BGreen + "Забрать наложку" + Color_Off

		elif statusTTN['StatusCode'] == '11':
			statusTTN['Status'] = Cyan + "Наложку забрали" + Color_Off

		elif statusTTN['StatusCode'] == '9':
			statusTTN['Status'] = Cyan + "Получена" + Color_Off

		elif statusTTN['StatusCode'] == '7':
			statusTTN['Status'] = Red + "Прибыла%s\n(хран. с %s)"% (Color_Off,statusTTN['DatePayedKeeping'][:10]) 

		elif statusTTN['StatusCode'] == '6':
			statusTTN['Status'] = Purple + "В целевом нас. пункте" + Color_Off

		elif statusTTN['StatusCode'] == '102' or statusTTN['StatusCode'] == '103' or statusTTN['StatusCode'] == '108':
			statusTTN['Status'] = On_IRed + "ПИДР ОТКАЗ" + Color_Off

		if statusTTN['DateScan'] == "0001-01-01 00:00:00":
			statusTTN['DateScan'] = ""

		nlg = '0'
		if statusTTN['Redelivery'] == 1 and statusTTN['RedeliverySum'] != '':
			nlg = statusTTN['RedeliverySum']
		elif statusTTN['Redelivery'] == 1:
			nlg = "Есть"

		table.add_row([DateCreated, statusTTN['ScheduledDeliveryDate'], textwrap.fill(statusTTN['CitySender'], 26),  textwrap.fill(statusTTN['CityRecipient'], 26), fio, statusTTN['Number'], statusTTN['DocumentWeight'], nlg, textwrap.fill(statusTTN['Status'], 26), statusTTN['StatusCode'], statusTTN['DateScan']])

		if (statusTTN['StatusCode'] == '104' or statusTTN['StatusCode'] == '102' or statusTTN['StatusCode'] == '103'  or statusTTN['StatusCode'] == '108') and statusTTN['LastCreatedOnTheBasisNumber']:
			additional_info = MakeRequest([], statusTTN['LastCreatedOnTheBasisNumber'],"")[0]
			table.add_row([additional_info[0]['DateCreated'][:-3], additional_info[0]['ScheduledDeliveryDate'], textwrap.fill(additional_info[0]['CitySender'], 26),  textwrap.fill(additional_info[0]['CityRecipient'], 26), "----", additional_info[0]['Number'] + "\n(переадр. ТТН)", "---", "---", textwrap.fill(additional_info[0]['Status'], 26), statusTTN['StatusCode'], '---'])
		try:
			statuses[(statusTTN['StatusCode'])].append(statusTTN['Number'] +'\t'+ dictTTNphone[statusTTN['Number']])
		except:
			try:
				statuses[(statusTTN['StatusCode'])] = [0]
				statuses[(statusTTN['StatusCode'])][0] = statusTTN['Number'] +'\t'+ dictTTNphone[statusTTN['Number']]
			except:
				pass

	print(table)
	print(' '.join(statuses.keys()))
	return statuses
# print(dictTTNphone)
statuses = PrintTable(info, dictTTNphone)
# print(statuses)
def printFiltred(statuses, statNumbers):
	for status in statNumbers:
		print()
		if str(status) in statuses:
			print("Отправки с кодом статуса: ", status)
			filtredTTN = statuses[str(status)]
			request = MakeRequest(filtredTTN, '', phonenumber)[0]
			PrintTable(request, {})
		elif status != '111':
			print("Отсутствуют отправки с кодом статуса: ", status)
		print()

# hundreds = counterStrings // 100

# i = 0
# info = []
# dictTTNphone = {}
# while i <= hundreds:
# 	request = MakeRequest(ttnsList[i*100: i*100+100], '', phonenumber)
# 	info += request[0]
# 	# print(request[1]+)
# 	dictTTNphone.update(request[1])
# 	i += 1

repeat = ""		
while repeat != '0':
	repeat =input("Через пробел введите статусы для фильтрации и обновления и нажмите ентер (111 для обновления всех посылок или 0 для выхода): ")
	if repeat == '111':
		info = []
		i = 0
		while i <= hundreds:
			request = MakeRequest(ttnsList[i*100: i*100+100], '', phonenumber)
			info += request[0]
			i += 1
		statuses = PrintTable(info, dictTTNphone)
		print("Все ТТН обновлены")
	if repeat != '' and repeat != '111':
		clear()
		PrintTable(info, dictTTNphone)
	printFiltred(statuses, repeat.split(' '))

