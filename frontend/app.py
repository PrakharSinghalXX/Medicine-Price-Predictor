import streamlit as st
import requests
import pandas as pd
import plotly.express as px


url = "https://medicine-price-backend.onrender.com"

st.set_page_config(
    page_title="Medicine Price Predictor",
    page_icon="💊",
    layout="wide"
)


# Title
st.title("💊 Medicine Price Predictor")
st.caption("Predictions exclude the top 1% highest-priced medicines in the dataset.")
st.markdown("### Predict the 'fair price' of a medicine and find 'cheaper alternatives'")
st.divider()

# Input
brand_name = st.text_input("Enter Medicine Name")
col1, col2 = st.columns(2)

# PRICE PREDICTION
with col1:

    if st.button("Predict Price"):

        if brand_name.strip() == "":
            st.warning("Please enter a medicine name.")
            st.stop()

        with st.spinner("Loading.."):
            response = requests.get(f"{url}/predict-price",params={"brand_name": brand_name})

        if response.status_code != 200:

            st.error(response.json()["detail"])

        else:

            data = response.json()

            st.success("Prediction Complete")

            st.metric(f"Predicted Fair Price:'{data['brand_name']}'",f"₹{data['predicted_price']:.2f}")


# ALTERNATIVES
with col2:

    if st.button("Find Alternatives"):

        if brand_name.strip() == "":
            st.warning("Please enter a medicine name.")
            st.stop()

        with st.spinner("Loading.."):
            response = requests.get(f"{url}/alternatives",params={"brand_name": brand_name})

        if response.status_code != 200:

            st.error(response.json()["detail"])

        else:

            data = response.json()
            alternatives = data["alternatives"]

            if len(alternatives) == 0:

                st.info("No cheaper alternatives found.")

            else:

                st.subheader("Cheapest Alternatives")

                df = pd.DataFrame(alternatives)
                st.dataframe(df)
                fig = px.bar(df,x='brand_name',y='price_inr',text='price_inr' )

                st.plotly_chart(fig,use_container_width=True)   
