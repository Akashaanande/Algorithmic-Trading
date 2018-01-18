# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 07:03:17 2018

@author: le
"""

import pandas as pd 
import numpy as np 



df1 =pd.DataFrame(pd.read_csv('C:\\Users\\le\\Desktop\\Quantinsti\\Qi project\\statistical arbitrage\\HDFCBANK.NS.csv'))
df1.drop(['Open','High','Low','Adj Close','Volume'],axis=1,inplace=True)
df1.rename(columns={'Close':'HDFCBANK_Close'},inplace=True)
df1.set_index('Date',inplace=True)


df2=pd.DataFrame(pd.read_csv('C:\\Users\\le\\Desktop\\Quantinsti\\Qi project\\statistical arbitrage\\HDFC.NS.csv'))
df2.drop(['Open','High','Low','Adj Close','Volume'],axis=1,inplace=True)
df2.rename(columns={'Close':'HDFC_Close'},inplace=True)
df2.set_index('Date',inplace=True)

df = df1.merge(df2, how='inner',left_index=True,right_index=True)



df['HDFCBANK_Close'].replace('null', np.nan, inplace=True)
df['HDFC_Close'].replace('null', np.nan, inplace=True)
df.dropna(inplace=True)

df['Ratio']=np.log10(df['HDFCBANK_Close'].astype(float)/df['HDFC_Close'].astype(float))

df['HDFCBANK_Returns']=df['HDFCBANK_Close'].astype(float).pct_change()
df['HDFC_Returns']=df['HDFC_Close'].astype(float).pct_change()

df['Mean']=df['Ratio'].rolling(window=30,center=False).mean()
df['STDEV']=df['Ratio'].rolling(window=30,center=False).std()


df['Mean'].fillna( 0, inplace=True)
df['STDEV'].fillna( 0, inplace=True)

df['Upper Line']=df['Mean']+2.25*df['STDEV']
df['Lower Line']=df['Mean']-2.25*df['STDEV']

df['Z-Score']=abs((df['Ratio'].astype(float)-df['Mean'].astype(float)))/df['STDEV'].astype(float)

df['Signal'] = df.apply(lambda x : "Enter_Trade" if x['Z-Score']>0.9 else ( "Exit_Trade" if x['Z-Score']<0.5 else "" ) ,axis=1)

df['Z_Cont']=df.apply(lambda _: '' ,axis=1)

l=len(df['Z-Score'])
B=""
C=""

for i in range( l) :
    
    if df['Signal'][i]!="":
        B=df['Signal'][i]
        if B!=C:
            
            C=B
            df['Z_Cont'][i]=df['Z-Score'][i]
        else:
            df['Z_Cont'][i]=df['Z_Cont'][i-1]

df['Z_Cont_shift']=df['Z_Cont'].shift(1)

df['Final_Sig']=df.apply(lambda x:x['Signal'] if x['Z_Cont_shift']!=x['Z_Cont'] else"" ,axis=1)

df['Final_Sig_shift']=df['Final_Sig'].shift(-1)

df['Signal_cont']=df.apply(lambda _: '' ,axis=1)

#df['Signal_cont_sh']=df['Signal_cont'].shift(-1)    
df['Signal_cont']=df.apply(lambda x:x['Signal'] if x['Z_Cont_shift']!=x['Z_Cont'] else x['Final_Sig_shift'] ,axis=1) 




print(df.head())

print(df.tail())
