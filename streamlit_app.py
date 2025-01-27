import streamlit_app as st
import requests
import re

def ask_gemini(question):
    api_key = 'AIzaSyB7QZPBh8QwzPHS5HL_DiFjf1LE7-ROc04'  
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "contents": [{
            "parts": [{"text": question}]
        }]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        try:
            response_json = response.json()
            answer = response_json.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "No answer found.")
            return answer
        except (ValueError, IndexError, KeyError) as e:
            return f"Error: Unable to parse JSON response. Details: {e}"
    else:
        return f"Error: {response.status_code}, {response.text}"

def extract_day_wise_itinerary(itinerary):
    day_wise_pattern = r"(Day \d+:.*?)(?=(Day \d+:|$))"
    matches = re.findall(day_wise_pattern, itinerary, re.DOTALL)
    day_wise_output = "\n\n".join(match[0].strip() for match in matches)
    return day_wise_output if day_wise_output else "No day-wise itinerary found."


st.title("AI-Powered Travel Itinerary Planner")
st.write("Plan your personalized travel itinerary with the help of AI.")

st.header("User Preferences")

budget = st.selectbox("What is your budget?", ["Low", "Moderate", "High"])
duration = st.slider("How many days is your trip?", min_value=1, max_value=30, value=5)
destination = st.text_input("Enter your destination:")
purpose = st.selectbox("What is the purpose of your trip?", ["Leisure", "Business", "Adventure", "Cultural Exploration", "Other"])
preferences = st.text_area("Describe your preferences for activities, food, or places (e.g., "
                          "'Hidden gems', 'Luxury dining', 'Adventure sports'):")


st.header("Additional Details")
dietary = st.text_input("Do you have any dietary preferences? (e.g., Vegetarian, Vegan, Halal, etc.)")
interests = st.text_area("Specific interests within your preferences (e.g., "
                         "art museums, hiking trails, local food markets):")
mobility = st.selectbox("Are there any mobility concerns?", ["No", "Yes"])
accommodation = st.selectbox("Preferred type of accommodation", ["Budget", "Luxury", "Central Location", "No Preference"])


if st.button("Generate Itinerary"):
    if destination.strip() == "":
        st.error("Please provide a destination to generate the itinerary.")
    else:
        
        question = (
            f"I am planning a {duration}-day trip to {destination}. "
            f"My budget is {budget}, and the purpose of my trip is {purpose}. "
            f"I prefer {preferences}. "
            f"Dietary preference: {dietary if dietary else 'None'}. "
            f"Specific interests: {interests if interests else 'None'}. "
            f"Mobility concerns: {'Yes' if mobility == 'Yes' else 'No'}. "
            f"Accommodation preference: {accommodation}. "
            "Please generate a detailed day-by-day itinerary for my trip."
        )

        
        with st.spinner("Generating your personalized itinerary..."):
            itinerary = ask_gemini(question)
            day_wise_itinerary = extract_day_wise_itinerary(itinerary)
        
        
        st.header("Your Personalized Itinerary")
        st.write(day_wise_itinerary)
