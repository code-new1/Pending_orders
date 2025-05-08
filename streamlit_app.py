# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col,when_matched

# Write directly to the app
#st.title(f":cup_with_straw: Pending Smoothie Orders! :cup_with_straw:")
st.title(f"⏳  Pending Smoothie Orders! ⏳")
st.write(
  """Orders that need to be filled!
  """)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED")==0).collect()

if my_dataframe:
    editable_df = st.data_editor(my_dataframe)
    #st.dataframe(data=my_dataframe, use_container_width=True)
    submitted = st.button('Submit')   
    if submitted:    
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(editable_df)

        try:
         og_dataset.merge(edited_dataset
                     , (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID'])
                     , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                    )
         st.success('Someone clicked the button', icon = '👍')
        except:
         st.write('Something went wrong.')
else:
    st.success('There are no pending orders right now', icon = '👍')

st.stop()


name_on_order = st.text_input('Name of the Smoothie:')
st.write("The name on the Smoothie will be", name_on_order)
# Convert Snowpark DataFrame to a list of values
fruit_list = [row['FRUIT_NAME'] for row in my_dataframe.collect()]
 

#ingredients_list = st.multiselect(
 #   "choose up to 5 ingredients",     
  #   my_dataframe,
   #  #default=["Dragon Fruit", "Guava"],
#)
 
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients'
     , my_dataframe     
 )
#st.write(ingredients_list)
#st.text(ingredients_list)
 
if ingredients_list:
    st.write(ingredients_list)
    st.text(ingredients_list)

    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string +"""','"""+name_on_order +"""')"""

    #st.write(my_insert_stmt)
    #st.stop()
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()  
        #works st.success('Your Smoothie is ordered!', icon="✅")
        #works st.success(f"Your Smoothie is ordered, {name_on_order}%", icon="✅")
        st.success("Your Smoothie is ordered, " + name_on_order + "%", icon="✅")

