import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

f1 = pd.read_csv('members_channel1.csv')
f2 = pd.read_csv('members_channel2.csv')

# rows present in 2nd file missing in 1st
print(f2[~f2.userid.isin(f1.userid)])
print("+++++++++++++++++++")

# rows present in 1st file missing in 2nd
print(f1[~f1.userid.isin(f2.userid)])
print("+++++++++++++++++++")

with open('file.csv', mode='w') as file_object:
    # print(f2[~f2.userid.isin(f1.userid)], file=file_object)
    print(f1[~f1.userid.isin(f2.userid)], file=file_object)
