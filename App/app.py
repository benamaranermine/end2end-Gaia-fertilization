import streamlit as st
import pandas as pd
import numpy as np 

import pickle
# Load Database Pkg
import sqlite3
conn = sqlite3.connect('data.db')
c = conn.cursor()
# Add company logo on the left side of the page
st.image("picture.png", width=100)

# CSS to adjust the layout
st.markdown(
    """
    <style>
        .element-container img {
            float: left;
            margin-left: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)
# Load the model for IVF prediction
ivf_model = pickle.load(open('models/IVF_LR.pkl', 'rb'))

# Track Utils
#c.execute('DROP TABLE IF EXISTS FertilityData')
# Fxn To Track Input & Prediction
def create_emotionclf_table():
	c.execute('CREATE TABLE IF NOT EXISTS FertilityData(ID INTEGER PRIMARY KEY AUTOINCREMENT,PreviousLiveBirths_IVF_DI INTEGER,PreviousPregnancies_IVF_DI INTEGER,Endometriosis INTEGER,OvulatoryDisorder INTEGER,TotalIVFCycles INTEGER,TotalDICycles INTEGER,AgeAtTreatment INTEGER,TubalDisease INTEGER,Prediction INTEGER,Probability INTEGER)')

def add_prediction_details(PreviousLiveBirths_IVF_DI,
            PreviousPregnancies_IVF_DI,
            Endometriosis,
            OvulatoryDisorder,
            TotalIVFCycles,
            TotalDICycles,
            AgeAtTreatment,
            TubalDisease,
            Prediction,
            Probability):
	c.execute('INSERT INTO FertilityData(PreviousLiveBirths_IVF_DI,PreviousPregnancies_IVF_DI,Endometriosis,OvulatoryDisorder,TotalIVFCycles,TotalDICycles,AgeAtTreatment,TubalDisease,Prediction,Probability) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',(PreviousLiveBirths_IVF_DI,PreviousPregnancies_IVF_DI,Endometriosis,OvulatoryDisorder,TotalIVFCycles,TotalDICycles,AgeAtTreatment,TubalDisease,Prediction,Probability))
	conn.commit()




# Streamlit app
st.title("In Vitro Fertilization (IVF) Outcome Prediction")

# Function to convert radio button response to binary
def binary_response(response):
    return 1 if response == 'Yes' else 0

# Function to get user input features for IVF prediction
# Define the variables in the broader scope of your Streamlit app
previous_live_births = 0
previous_pregnancies = 0
fertility_issues_binary = 0
ovulation_issues_binary = 0
number_of_cycles = 0
previous_cycles_DI = 0
age = 0
tubal_issues_binary = 0

# Function to get user input features for IVF prediction
def ivf_input_features():
    # Update the variables with user input
    global previous_live_births, previous_pregnancies, fertility_issues_binary, ovulation_issues_binary, number_of_cycles, previous_cycles_DI, age, tubal_issues_binary
    previous_live_births = st.sidebar.number_input("previous live births", min_value=0, max_value=3, value=0)
    previous_pregnancies = st.sidebar.number_input("previous pregnancies", min_value=0, max_value=5, value=0)
    fertility_issues = st.sidebar.radio("Do you have other fertility issues?", ('Yes', 'No'))
    fertility_issues_binary = binary_response(fertility_issues)
      
    ovulation_issues = st.sidebar.radio("Do you have other ovulation issues?", ('Yes', 'No'))
    ovulation_issues_binary = binary_response(ovulation_issues)
    number_of_cycles = st.sidebar.number_input("Number of IVF Cycles", min_value=0, max_value=4, value=0)
    previous_cycles_DI = st.sidebar.number_input("Previous DI Cycles", min_value=0, max_value=4, value=0)
    age = st.sidebar.number_input("Age", min_value=18, max_value=50, value=30)
    tubal_issues = st.sidebar.radio("Do you have  tubal issues?", ('Yes', 'No'))
    tubal_issues_binary = binary_response(tubal_issues)

    # Define the data dictionary
    data = {
        'Total number of previous live births - IVF or DI': previous_live_births,
        'Total number of previous pregnancies - IVF and DI': previous_pregnancies,
        'Causes of infertility - endometriosis': fertility_issues_binary,
        'Causes of infertility - ovulatory disorder': ovulation_issues_binary,
        'Total number of previous IVF cycles': number_of_cycles,
        'Total number of previous DI cycles': previous_cycles_DI,
        'Patient age at treatment': age,
        'Causes of infertility - tubal disease': tubal_issues_binary
    }
    features = pd.DataFrame(data, index=[0])
    return features

# Function to view the content of the SQLite database in the console
def view_database_content():
    print("Viewing Database Content")
    
    # Connect to the SQLite database
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Execute a SQL query to fetch all data from the FertilityData table
    c.execute('SELECT * FROM FertilityData')
    data = c.fetchall()
    
    # Close the database connection
    conn.close()
    
    # Print the data in the console
    if data:
        for row in data:
            print(row)
    else:
        print("No data found in the database.")
# Get user input features for IVF prediction
ivf_input_df = ivf_input_features()

# Display user input features
st.subheader('User Input Features for IVF Prediction')
st.write(ivf_input_df)

# Button to trigger IVF prediction
if st.button("Calculate Results"):
    # Prepare input data for IVF prediction
    input_data = ivf_input_df
    
    # Make IVF prediction using the loaded model

    probability = ivf_model.predict_proba(input_data)[:,1]
    prediction = int(ivf_model.predict(input_data)[0])
    create_emotionclf_table()
    add_prediction_details(previous_live_births,previous_pregnancies,fertility_issues_binary,ovulation_issues_binary,number_of_cycles,previous_cycles_DI,age,tubal_issues_binary,prediction,np.max(probability))
    st.subheader('The Probability to have live birth is')
    st.write(probability)
    # Call the function to view the database content
    view_database_content()




