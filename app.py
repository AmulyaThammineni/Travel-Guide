import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import requests
from io import BytesIO
from dotenv import load_dotenv  # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Check if the API key is available
if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
    st.stop()  # Stop the app if the API key is missing

genai.configure(api_key=GEMINI_API_KEY)

# Function to load the Gemini Pro Vision model
def load_gemini_pro_vision_model():
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

# Helper Functions
def get_image_from_url(image_url):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        image = Image.open(BytesIO(response.content))
        return image
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching image from URL: {e}")
        return None
    except Exception as e:
        st.error(f"Error opening image: {e}")
        return None

def generate_tourist_info(model, image, prompt):
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        st.error(f"Error generating content: {e}")
        return None

# Main Function
def main():
    st.title("Tourist Place Information App")

    # Load the Gemini Pro Vision model
    model = load_gemini_pro_vision_model()

    # Input: Image URL or file upload
    input_type = st.radio("Select input type:", ("Image URL", "Upload Image"))

    image = None
    if input_type == "Image URL":
        image_url = st.text_input("Enter image URL:")
        if image_url:
            image = get_image_from_url(image_url)
    else:
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)

    if image:
        st.image(image, caption="Input Image", use_container_width=True)

        # Prompt for Gemini
        prompt = """
        You are an expert travel guide. Analyze the image and provide the following information:
        1. A detailed description of the tourist place.
        2. Suggest 3 popular accommodations near this place, including their approximate price range.
        3. Recommend 3 cultural foods to try in this area, including where to find them.
        """

        # Generate information
        if st.button("Generate Information"):
            with st.spinner("Generating information..."):
                response = generate_tourist_info(model, image, prompt)
                if response:
                    st.subheader("Generated Information:")
                    st.write(response)
    else:
        st.info("Please provide an image URL or upload an image to get started.")

if __name__ == "__main__":
    main()
