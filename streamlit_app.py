import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie.")

# Name input
name_on_order = st.text_input("Name on Smoothie: ", " ")
st.write("The name on your smoothie will be: ", name_on_order)

# Connect to Snowflake and fetch fruit options
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)

# Convert to pandas DataFrame for easier manipulation
pd_df = my_dataframe.to_pandas()

# Create a list of fruit names for the multiselect
fruit_list = pd_df["FRUIT_NAME"].tolist()

# Allow user to select up to 5 fruits
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients: ',
    fruit_list,
    max_selections=5
)

# If user has selected fruits, show nutrition info and order option
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        try:
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.subheader(fruit_chosen + ' Nutrition Information')
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
            fruityvice_response.raise_for_status()
            fruityvice_data = fruityvice_response.json()
            st.dataframe(data=fruityvice_data, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to fetch data for {fruit_chosen}: {e}")

    # Order submission
    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
