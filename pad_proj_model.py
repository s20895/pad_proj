import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import joblib

# Data loading
df = pd.read_csv('apartments_pl_2024_04.csv')

# Data cleaning based on previous analysis 
df.drop(['condition', 'buildingMaterial', 'id'], axis=1, inplace=True)
df.dropna(axis=0, inplace=True)

df = pd.get_dummies(df, drop_first=True)

# Data split
X = df.drop(columns=['price'])
y = df['price']

X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=100)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.2, random_state=100)

# Data standarization 
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

# Model
model = LinearRegression()
model.fit(X_train, y_train)

joblib.dump(model, 'pad_proj_model_pickle.pkl')

# Prediction based on the validation set
y_val_pred = model.predict(X_val)

# Model evaluation (validation set)
mse = mean_squared_error(y_val, y_val_pred)
print(f'Validation set Mean Squared Error: {mse}')
r2_val = r2_score(y_val, y_val_pred)
print(f'Validation set R-squared: {r2_val}')

# Prediction based on the test set
y_test_pred = model.predict(X_test)

# Model evaluation (test set)
mse_test = mean_squared_error(y_test, y_test_pred)
print(f'Test set Mean Squared Error: {mse_test}')
r2_test = r2_score(y_test, y_test_pred)
print(f'Test set R-squared: {r2_test}')

# W tresci jest wspomniane o ewaluacji poprzez accuracy lub f1, ale
# w przypadku regresji (predykcji wartosci ciaglych) te miary nie maja
# zastosowania. Uzylem zatem Mean Squared Error (MSE) oraz R-squared.