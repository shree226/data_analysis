import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
from google import genai
import openai
warnings.filterwarnings('ignore')
st.set_page_config(page_title="dashboard", page_icon=":bar_chart:",layout="wide")
st.title("Analysis of Key Crop Trends in India (2020-2025)")
#st.markdown('<style>div.block-container{background-color: #222222;}</style>',unsafe_allow_html=True)

st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
df = pd.read_csv("data/Gujarat_Crop_CLEANED.csv", encoding = "ISO-8859-1")


from streamlit_option_menu import option_menu

# Inside your sidebar
with st.sidebar:
    selected = option_menu(
        menu_title="",  # Optional
        options=["Home", "Data Table","Visualize Data", "Time Series Analysis", "Ask anything"],
        icons=["house", "table","bar-chart-line", "graph-up-arrow", "chat-dots-fill"],  # Bootstrap icons
        menu_icon="cast",  # Optional
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#222222"},
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link": {"color": "white", "font-size": "16px", "text-align": "left"},
            "nav-link-selected": {"background-color": "#444444"},
        }
    )

if selected == "Home":
    st.write("This dataset contains agricultural data for various crops (rice, wheat, maize, etc.) across Indian states from 2020-21 to 2024-25. It includes area harvested (in lakh hectares), production (in lakh tonnes), and yield (kg/ha) for each crop, season (Kharif, Rabi, Summer), and state. ")
elif selected == "Data Table":
    st.title("📄 Data Table")
    st.dataframe(df)
elif selected == "Visualize Data":
    crops = st.multiselect("Pick your Crop", df["Crops"].unique())
    if not crops:
        df2 = df.copy()
    else:
        df2 = df[df["Crops"].isin(crops)]

    states = st.multiselect("Pick the State", df2["States"].unique())
    if not states:
        df3 = df2.copy()
    else:
        df3 = df2[df2["States"].isin(states)]
    season = st.multiselect("Pick the Season",df3["Season"].unique())


    # Step 4: Final filtered data (clean and compact)
    filtered_df = df.copy()
    if crops:
        filtered_df = filtered_df[filtered_df["Crops"].isin(crops)]
    if states:
        filtered_df = filtered_df[filtered_df["States"].isin(states)]
    if season:
        filtered_df = filtered_df[filtered_df["Season"].isin(season)]

    metric_type = st.selectbox("Select metric", ["Yield", "Area", "Production"])
    year_option = st.selectbox("Select year", ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"],key="year_select")

    column_map = {
        "Yield": f"Yield-{year_option}(Kg/ha)",
        "Area": f"Area-{year_option}(Lakh ha)",
        "Production": f"Production-{year_option}(Lakh Tonnes)"


    }
    metric_column = column_map[metric_type]
    if metric_column in filtered_df.columns:
        crop_yield_df = filtered_df.groupby(["Crops", "States"], as_index=False)[metric_column].sum()
        st.subheader("Crop-wise "+column_map[metric_type])
        fig = px.bar(
            crop_yield_df,
            x="Crops",
            y=metric_column,
            color="States",  # This partitions each crop bar by state
            text=crop_yield_df[metric_column].apply(lambda x: f'{x:,.2f}'),
            barmode="stack",  # or "group" for side-by-side
            template="seaborn"
        )
        st.plotly_chart(fig, use_container_width=True)



    if metric_column in filtered_df.columns:
        crop_yield_df = filtered_df.groupby("States", as_index=False)[metric_column].sum()
        st.subheader("State-wise "+column_map[metric_type])
        fig = px.pie(crop_yield_df, values =metric_column , names = "States", hole = 0.5)
        fig.update_traces(text = crop_yield_df["States"], textposition = "outside")
        st.plotly_chart(fig,use_container_width=True)

    if metric_column in filtered_df.columns:
        crop_yield_df = filtered_df.groupby("Season", as_index=False)[metric_column].sum()
        st.subheader("Season-wise " + column_map[metric_type])
        fig = px.bar(
            crop_yield_df,
            y="Season",
            x=metric_column,
            orientation="h",
            text=crop_yield_df[metric_column].apply(lambda x: f"{x:,.2f}"),
            template="seaborn",
            color="Season"
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)


#Bar/Pie: "inside", "outside" Line/scatter: "top center", "bottom left", "middle right", etc.
#st.write("Columns in df:", df.columns.tolist())
elif selected == "Time Series Analysis":

    st.title("Time Series Analysis Dashboard")

    # Define metric options and their respective columns
    metric_options = {
        "Yield": [col for col in df.columns if "Yield-" in col],
        "Area": [col for col in df.columns if "Area-" in col],
        "Production": [col for col in df.columns if "Production-" in col]
    }

    # Display-friendly metric labels
    metric_labels = {
        "Yield": "Yield (Kg/ha)",
        "Area": "Area (Lakh ha)",
        "Production": "Production (Lakh Tonnes)"
    }

    # Select which metric to analyze
    metric_type = st.selectbox("Select Metric Type", list(metric_options.keys()))

    # Melt the dataset into time series format
    metric_cols = metric_options[metric_type]
    df_melted = df.melt(
        id_vars=["Crops", "States", "Season"],
        value_vars=metric_cols,
        var_name="Year",
        value_name="Value"
    )
    df_melted["Year"] = df_melted["Year"].str.extract(rf"{metric_type}-(\d{{4}}-\d{{2}})")

    # Cascading dropdowns
    crops = st.selectbox("Select Crop", df_melted["Crops"].dropna().unique(), key="crop_select")

    # Filter states based on selected crop
    available_states = df_melted[df_melted["Crops"] == crops]["States"].dropna().unique()
    states = st.selectbox("Select State", available_states, key="state_select")

    # Filter seasons based on selected crop and state
    available_seasons = df_melted[
        (df_melted["Crops"] == crops) &
        (df_melted["States"] == states)
    ]["Season"].dropna().unique()
    season = st.selectbox("Select Season", available_seasons, key="season_select")

    # Final filtering
    filtered_df = df_melted[
        (df_melted["Crops"] == crops) &
        (df_melted["States"] == states) &
        (df_melted["Season"] == season)
    ]

    # Plotting
    if not filtered_df.empty:
        fig = px.line(
            filtered_df,
            x="Year",
            y="Value",
            title=f"{metric_labels[metric_type]} Trend for {crops} in {states} ({season})",
            labels={"Value": metric_labels[metric_type]},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for selected combination.")
elif selected == "Ask anything":
    import requests
    import streamlit as st
    import pandas as pd

    st.title("🔍 Ask About Your Crop Data")
    import streamlit as st
    import requests

    api_key = st.secrets["GOOGLE_API_KEY"]

    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'
    headers = {
        'Content-Type': 'application/json'
    }

    user_prompt = st.text_area("")

    if st.button("Get Insight"):
        with st.spinner("Analyzing with Gemini..."):
            df_preview = df.head(300).to_csv(index=False)
            full_prompt = f"""You are a data analyst. Analyze this dataset:\n{df_preview}\nUser query: {user_prompt}"""
            
            data = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }]
            }

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                reply = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success(reply)
            else:
                st.error(f"Error {response.status_code}: {response.text}")
