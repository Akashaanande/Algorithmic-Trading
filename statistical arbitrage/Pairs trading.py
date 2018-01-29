# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 07:03:17 2018

@author: le
"""

import pandas as pd 
import numpy as np 





def get_data():
    
    df1 =pd.DataFrame(pd.read_csv('C:\\Users\\le\\Desktop\\Quantinsti\\Qi project\\statistical arbitrage\\HDFCBANK.NS.csv'))
    df1.drop(['Open','High','Low','Adj Close','Volume'],axis=1,inplace=True)
    df1.rename(columns={'Close':'HDFCBANK_Close'},inplace=True)
    df1.set_index('Date',inplace=True)


    df2=pd.DataFrame(pd.read_csv('C:\\Users\\le\\Desktop\\Quantinsti\\Qi project\\statistical arbitrage\\HDFC.NS.csv'))
    df2.drop(['Open','High','Low','Adj Close','Volume'],axis=1,inplace=True)
    df2.rename(columns={'Close':'HDFC_Close'},inplace=True)
    df2.set_index('Date',inplace=True)

    df = df1.merge(df2, how='inner',left_index=True,right_index=True)

    return df

def generate_sig(df,n,z):
    

    df['HDFCBANK_Close'].replace('null', np.nan, inplace=True)
    df['HDFC_Close'].replace('null', np.nan, inplace=True)
    df.dropna(inplace=True)
    
    df['Ratio']=np.log10(df['HDFCBANK_Close'].astype(float)/df['HDFC_Close'].astype(float))

    df['HDFCBANK_Returns']=df['HDFCBANK_Close'].astype(float).pct_change()
    df['HDFC_Returns']=df['HDFC_Close'].astype(float).pct_change()

    df['Mean']=df['Ratio'].rolling(window=n,center=False).mean()
    df['STDEV']=df['Ratio'].rolling(window=n,center=False).std()


    df['Mean'].fillna( 0, inplace=True)
    df['STDEV'].fillna( 0, inplace=True)

    df['Upper Line']=df['Mean']+2.25*df['STDEV']
    df['Lower Line']=df['Mean']-2.25*df['STDEV']

    df['Z-Score']=abs((df['Ratio'].astype(float)-df['Mean'].astype(float)))/df['STDEV'].astype(float)

    df['Signal'] = df.apply(lambda x : "Enter_Trade" if x['Z-Score']>z else ( "Exit_Trade" if x['Z-Score']<z else "" ) ,axis=1)

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
        else:
                df['Z_Cont'][i]=df['Z_Cont'][i-1]
        

    df['Z_Cont_shift']=df['Z_Cont'].shift(1)

    df['Final_Sig']=df.apply(lambda x:x['Signal'] if x['Z_Cont_shift']!=x['Z_Cont'] else"" ,axis=1)

    df['HDFC_Enter_Exit']=df.apply(lambda x:x['HDFC_Close'] if (x['Final_Sig']=="Exit_Trade" or x['Final_Sig']=="Enter_Trade") else "" ,axis=1  )

    df['HDFCBANK_Enter_Exit']=df.apply(lambda x:x['HDFCBANK_Close'] if (x['Final_Sig']=="Exit_Trade" or x['Final_Sig']=="Enter_Trade") else "" ,axis=1  )


    df['HDFC_Ret_Enter_Exit']=df.apply(lambda x:x['HDFC_Returns'] if (x['Final_Sig']=="Exit_Trade" or x['Final_Sig']=="Enter_Trade") else "" ,axis=1  )

    df['HDFCBANK_Ret_Enter_Exit']=df.apply(lambda x:x['HDFCBANK_Returns'] if (x['Final_Sig']=="Exit_Trade" or x['Final_Sig']=="Enter_Trade") else "" ,axis=1  )


    for i in range(len(df['Final_Sig'])):
        if df['Z_Cont'][i]==df['Z_Cont_shift'][i]:
            df['Final_Sig'][i]=df['Final_Sig'][i-1]
            df['HDFC_Enter_Exit'][i]=df['HDFC_Enter_Exit'][i-1]
            df['HDFCBANK_Enter_Exit'][i]=df['HDFCBANK_Enter_Exit'][i-1]
            df['HDFC_Ret_Enter_Exit'][i]=df['HDFC_Ret_Enter_Exit'][i-1]
            df['HDFCBANK_Ret_Enter_Exit'][i]=df['HDFCBANK_Ret_Enter_Exit'][i-1]
        else:
            df['Final_Sig'][i]=df['Final_Sig'][i]
            df['HDFC_Enter_Exit'][i]=df['HDFC_Enter_Exit'][i]
            df['HDFCBANK_Enter_Exit'][i]=df['HDFCBANK_Enter_Exit'][i]
            df['HDFC_Ret_Enter_Exit'][i]=df['HDFC_Ret_Enter_Exit'][i]
            df['HDFCBANK_Ret_Enter_Exit'][i]=df['HDFCBANK_Ret_Enter_Exit'][i]

    df=df.iloc[n:]

    df['HDFC_Enter_Exit']=df['HDFC_Enter_Exit'].astype(float)
    df['HDFCBANK_Enter_Exit']=df['HDFCBANK_Enter_Exit'].astype(float)
    df['HDFC_Ret_Enter_Exit']=df['HDFC_Ret_Enter_Exit'].astype(float)
    df['HDFCBANK_Ret_Enter_Exit']=df['HDFCBANK_Ret_Enter_Exit'].astype(float)
    df['HDFC_Ret_Enter_Exit_Shift']=df['HDFC_Ret_Enter_Exit'].shift(1)
    df['HDFCBANK_Ret_Enter_Exit_Shift']=df['HDFCBANK_Ret_Enter_Exit'].shift(1)

    df['Final_Sig_shift']=df['Final_Sig'].shift(1)
    df['HDFC_Enter_Exit_Shift']=df['HDFC_Enter_Exit'].shift(1)
    df['HDFC_Enter_Exit_Shift']=df['HDFC_Enter_Exit_Shift'].astype(float)
    df['HDFCBANK_Enter_Exit_Shift']=df['HDFCBANK_Enter_Exit'].shift(1)
    df['HDFCBANK_Enter_Exit_Shift']=df['HDFCBANK_Enter_Exit_Shift'].astype(float)

    
    
    df['HDFC_Trade_Ret']=df.apply(lambda _:'',axis=1)
    df['HDFC_Trade_Ret']=df.apply(lambda x : (x['HDFC_Enter_Exit']/x['HDFC_Enter_Exit_Shift']) -1 if (x['Final_Sig']=="Exit_Trade" and x['Final_Sig_shift']=="Enter_Trade") and (x['HDFCBANK_Ret_Enter_Exit_Shift']>x['HDFC_Ret_Enter_Exit_Shift']) else (
        1-(x['HDFC_Enter_Exit']/x['HDFC_Enter_Exit_Shift']) if (x['Final_Sig']=="Exit_Trade" and x['Final_Sig_shift']=="Enter_Trade") and (x['HDFCBANK_Ret_Enter_Exit_Shift']<x['HDFC_Ret_Enter_Exit_Shift']) else 0) ,axis=1)
    
    df['HDFCBANK_Trade_Ret']=df.apply(lambda _:'',axis=1)
    df['HDFCBANK_Trade_Ret']=df.apply(lambda x : (x['HDFCBANK_Enter_Exit']/x['HDFCBANK_Enter_Exit_Shift']) -1 if (x['Final_Sig']=="Exit_Trade" and x['Final_Sig_shift']=="Enter_Trade") and (x['HDFCBANK_Ret_Enter_Exit_Shift']<x['HDFC_Ret_Enter_Exit_Shift']) else (
        1-(x['HDFCBANK_Enter_Exit']/x['HDFCBANK_Enter_Exit_Shift']) if (x['Final_Sig']=="Exit_Trade" and x['Final_Sig_shift']=="Enter_Trade") and (x['HDFCBANK_Ret_Enter_Exit_Shift']>x['HDFC_Ret_Enter_Exit_Shift']) else 0) ,axis=1)

    df['Total_Ret']=df['HDFCBANK_Trade_Ret']+df['HDFC_Trade_Ret']
    Strat_Returns=df['Total_Ret'].sum()*100

    return Strat_Returns

df2=get_data()

Returns=generate_sig(df2,30,0.9) 


z = np.linspace(1,3,2,dtype=int)
n = np.linspace(10,30,2,dtype=int)
results_pnl = np.zeros((len(z),len(n)))
#z=[0.9,1,1.5,2]
#n=[10,15,20,30]
#a=len(z)
#b=len(n)

for i, z in enumerate(z):
    for j, n in enumerate(n):
        Returns=generate_sig(df2,n,z)        
        results_pnl[i,j] = Returns



print(Returns)

print(results_pnl)


