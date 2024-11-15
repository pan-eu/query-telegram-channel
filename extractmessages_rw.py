# ======================================================================================================================
#                                               Extracts Telegram Chats
# ======================================================================================================================

# below code authenticates into telegram and fetches list of groups where you are part of, and extracts all member info
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from datetime import date
import csv
import configparser
import pandas as pd
import re

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")


# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
api_hash = str(api_hash)
phone = config['Telegram']['phone']

# create connection
client = TelegramClient(phone, api_id, api_hash)
client.connect()

# setting print defaults
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

chats = []
last_date = None
chunk_size = 200
groups=[]
 
result = client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
         ))
chats.extend(result.chats)
for chat in chats:
    try:
        if chat.megagroup== True:
            groups.append(chat)
    except:
        continue

target_group= input("Enter a group/channel handle to scrape, ex: @group_name or https://t.me/group_name: ")
# target_group=groups[int(g_index)]
# target_group='@HEcosystem'

# create export file name but first check if input is a link to a channel/group
today = date.today()
regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
url_check = re.findall(regex,target_group)   
if len(url_check) == 1:
    print('URL was provided')
    spl_char = "/"
    res = target_group.rsplit(spl_char, 1)[1]
    print("Group/Channel name is : " + str(res))
    export_file_name = 'export_messages_' + res + '_' + today.strftime("%b-%d-%Y") + '.csv'
else:
    print('Handle was provided')
    print("Group/Channel name is : " + target_group)
    export_file_name = 'export_messages_' + target_group + '_' + today.strftime("%b-%d-%Y") + '.csv'
 
print('Extracting Messages...')

chats =client.get_messages(target_group, 1000000) # n number of messages to be extracted
# Get message id, message, sender id, reply to message id, and timestamp
message_id =[]
message =[]
sender =[]
reply_to =[]
time = []
if len(chats):
    for chat in chats:
        message_id.append(chat.id)
        message.append(chat.message)
        sender.append(chat.from_id)
        reply_to.append(chat.reply_to_msg_id)
        time.append(chat.date)
data ={'message_id':message_id, 'message': message, 'sender_ID':sender, 'reply_to_msg_id':reply_to, 'time':time}
df = pd.DataFrame(data)
messages = df.sort_index(ascending= False)

# print(df)

print('Saving In file...')
with open(export_file_name,"w",encoding='UTF-8') as f:
    writer = csv.writer(f,delimiter=",",lineterminator="\n")
    writer.writerow(['message_id','message', 'sender_name', 'time', 'group', 'reply_to', 'other_sender_info'])
    for chat in chats:
        if chat.id:
            message_id= chat.id
        else:
            message_id= ""
        if chat.message:
            message= chat.message
        else:
            message= ""
        if chat.reply_to:
            reply_to= chat.reply_to
        else:
            reply_to= ""
        if chat.date:
            time= chat.date
        else:
            time= ""
        if chat.sender:
            sender= chat.sender
        else:
            sender= "" 
        try:
            if chat.sender.first_name:
                first_name= chat.sender.first_name
            else:
                first_name= ""
        except AttributeError:
            first_name= ""
        try:
            if chat.sender.last_name:
                last_name= chat.sender.last_name
            else:
                last_name= ""
        except AttributeError:
            last_name= ""
        sender_name= (first_name + ' ' + last_name).strip()
        writer.writerow([message_id, message, sender_name, time, target_group, reply_to, chat.sender])      
print('Messages scraped successfully.')
