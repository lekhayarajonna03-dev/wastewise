import streamlit as st
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []
import pandas as pd
import joblib


st.set_page_config(
    page_title="WasteWise",
    page_icon="🌱",
    layout="centered"
)

# Load the trained AI model
model = joblib.load("wastewise_model.pkl")
model_name = type(model).__name__
data = pd.read_excel("data.xlsx")
data["Total_Waste_kg"] = data["KSW kg"] + data["PW kg"]


# App title
st.markdown(
    "<h1 style='text-align: center;'>🌱 WASTEWISE</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h3 style='text-align: center;'>AI-Powered Food Waste Prediction</h3>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; font-size: 18px;'>"
    "Smarter food planning. Less waste. A greener future. 🌍"
    "</p>",
    unsafe_allow_html=True
)


st.write("🌱 Enter the details below to estimate the amount of food waste.")

# User inputs
col1, col2, col3 = st.columns(3)
st.markdown("### 📋 Enter Prediction Details")
with col1:
    diners = st.number_input(
       "Number of Diners",
         min_value=1,
         max_value=2000,
         value=450
)
with col2:
         menu = st.number_input(
         "Menu Number",
           min_value=1,
           max_value=25,
           value=12
)
with col3:
        day = st.selectbox(
             "Day of the Week",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
)


# Prediction button
if st.button("🌱 Predict Food Waste", use_container_width=True):

    new_data = pd.DataFrame({
        "DINERS": [diners]
    })

    for column in model.feature_names_in_:
        if column not in new_data.columns:
            new_data[column] = 0

    menu_column = "MENU_" + str(menu)

    if menu_column in new_data.columns:
        new_data[menu_column] = 1

    day_column = "Day_of_Week_" + day

    if day_column in new_data.columns:
        new_data[day_column] = 1
    new_data = new_data[model.feature_names_in_]

    prediction = model.predict(new_data)[0]
    if prediction < 23.55:
        waste_level = "🟢 Low Waste"
    elif prediction < 41.54:
        waste_level = "🟡 Moderate Waste"
    else:
        waste_level = "🔴 High Waste"

    st.session_state.prediction_history.append({
        "Diners": diners,
        "Menu": menu,
        "Day": day,
        "Predicted Waste (kg)": round(prediction, 2),
        "Waste Level": waste_level
    })

    

    st.markdown("### 🤖 AI Prediction Result")

    st.caption(
        f"Prediction for {diners} diners • Menu {menu} • {day}"
    )
    st.markdown(
    f"""
    <div style="
        text-align: center;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    ">
        <h3>🌱 Predicted Food Waste</h3>
        <h1>{prediction:.2f} kg</h1>
    </div>
    """,
    unsafe_allow_html=True
)

    st.info(
    "🤖 The AI model analyzes the selected diners, menu, "
    "and day to estimate expected food waste."
)


    if prediction < 23.55:
        st.success("🟢 Low Waste")
        st.caption("The predicted food waste is relatively low.")

    elif prediction < 41.54:
        st.warning("🟡 Moderate Waste")
        st.caption(
            "Consider adjusting food quantities based on this prediction."
        )

    else:
        st.error("🔴 High Waste")
        st.caption(
            "Consider reviewing food quantities and menu planning."
        )

    st.caption(
        "This estimate is based on the number of diners, selected menu, "
        "and day of the week."
    )


    st.info(
        "💡 This prediction can help the school plan food quantities "
        "and reduce unnecessary food waste."
    )
    st.markdown("---")

st.markdown("### 📊 Food Waste Overview")

total_waste = data["KSW kg"].sum() + data["PW kg"].sum()
total_diners = data["DINERS"].sum()
average_waste = total_waste / total_diners

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "♻️ Total Food Waste",
        f"{total_waste:.2f} kg"
    )

with col2:
    st.metric(
        "👥 Total Diners",
        f"{total_diners:,.0f}"
    )

with col3:
    st.metric(
        "📊 Waste per Diner",
        f"{average_waste:.3f} kg"
    )
data["DATE"] = pd.to_datetime(data["DATE"])

data["Day"] = data["DATE"].dt.day_name()

daily_waste = data.groupby("Day")[["KSW kg", "PW kg"]].sum()

day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

daily_waste = daily_waste.reindex(day_order)
daily_waste["Total Waste"] = daily_waste["KSW kg"] + daily_waste["PW kg"]

st.markdown("### 📈 Food Waste by Day")

chart_data = daily_waste[["Total Waste"]].reset_index()

chart_data["Day"] = pd.Categorical(
    chart_data["Day"],
    categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    ordered=True
)

st.bar_chart(
    chart_data,
    x="Day",
    y="Total Waste"
)
menu_waste = data.groupby("MENU")[["KSW kg", "PW kg"]].sum()

menu_waste["Total Waste"] = (
    menu_waste["KSW kg"] + menu_waste["PW kg"]
)
st.markdown("### 🍽️ Food Waste by Menu")

st.bar_chart(
    menu_waste[["Total Waste"]]
)
st.markdown("---")
st.markdown("### 💡 Key Insights")

st.markdown("### 📊 Waste Distribution")

data["Waste Level"] = data["Total_Waste_kg"].apply(
    lambda x: "Low Waste" if x < 23.55
    else "Moderate Waste" if x < 41.54
    else "High Waste"
)

waste_distribution = data["Waste Level"].value_counts()

st.bar_chart(waste_distribution)
highest_waste_day = daily_waste["Total Waste"].idxmax()
highest_waste_menu = menu_waste["Total Waste"].idxmax()
insight1, insight2, insight3 = st.columns(3)

with insight1:
    st.info(
        f"📅 Highest Waste Day\n\n**{highest_waste_day}**"
    )

with insight2:
    st.info(
        f"🍽️ Highest Waste Menu\n\n**Menu {highest_waste_menu}**"
    )

with insight3:
    st.info(
        f"👥 Waste per Diner\n\n**{average_waste:.3f} kg**"
    )


st.markdown("---")

st.caption("🌱 WasteWise | AI-Powered Food Waste Prediction")
st.caption("School AI Project")
st.markdown("---")

st.markdown("### 🌱 About WasteWise")

st.write(
    "WasteWise is an AI-powered food waste prediction system "
    "designed to help schools estimate food waste and plan food "
    "quantities more efficiently."
)
st.markdown("---")

st.markdown("### 🤖 How WasteWise Works")

st.write(
    "1️⃣ Enter the number of diners, menu number, and day of the week."
)

st.write(
    "2️⃣ WasteWise processes these inputs using a trained machine learning model."
)

st.write(
    "3️⃣ The model predicts the expected amount of food waste in kilograms."
)

st.write(
    "4️⃣ The dashboard helps visualize recorded food waste and identify patterns."
)
st.markdown("### 🧠 Machine Learning Model")

st.info(
    f"WasteWise is currently using **{model_name}** to make predictions."
)
st.markdown("---")

st.markdown("### 💡 Waste Reduction Tips")

st.write("🥗 Plan food quantities according to the expected number of diners.")
st.write("📊 Monitor days and menus with higher recorded food waste.")
st.write("🍽️ Adjust future food preparation based on previous waste patterns.")
st.write("♻️ Separate and record kitchen and plate waste regularly.")

st.markdown("---")

st.markdown("### 🕘 Prediction History")

if st.session_state.prediction_history:
    history_df = pd.DataFrame(st.session_state.prediction_history)
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No predictions made yet.")

if st.session_state.prediction_history:
    if st.button("🗑️ Clear Prediction History"):
        st.session_state.prediction_history = []
        st.rerun()
st.download_button(
    "📥 Download Prediction History",
    data=pd.DataFrame(
        st.session_state.prediction_history
    ).to_csv(index=False),
    file_name="wastewise_prediction_history.csv",
    mime="text/csv"
)

