import pandas as pd
from sklearn.model_selection import train_test_split

dfpreperi = pd.read_csv('df_extracted_features_pre&peri.csv')
print('length df preperi', len(dfpreperi))

dfpre = pd.read_csv('df_extracted_features_pre.csv')

y = pd.read_csv('C:/Users/johns/Documents/10semester/P10/For_machinelearning/number_of_days_in_ICU.csv')
print('original y', len(y))
y=y.drop('icu_days', axis='columns')
print(y.head())

mer_df = pd.merge(dfpreperi, y, on="caseid")

print(len(mer_df))

X=mer_df.drop('icu_days_binary', axis='columns')

y = mer_df[['caseid', 'icu_days_binary']]

print(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2,            # 20 % til test
    random_state=42,          # for reproduserbarhet
    stratify=y                # behold klassefordeling
)

train_ids, test_ids = train_test_split(
    caseid_labels["caseid"],
    test_size=0.2,
    random_state=42,
    stratify=caseid_labels["icu_days_binary"]
)





########################################################################################################


