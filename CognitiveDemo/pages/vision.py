import streamlit as st
import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from PIL import Image
import io
from CognitiveDemo.modules.vision_module import analyze_image, analyze_image_apples


def show_vision():
    # Combo box for selection
    model_type = st.selectbox("Select Model Type:", ["Standard", "Fine Tuned"])

    st.header("Vision Page")
    st.write(f"You selected: {model_type}")
    # Add more functionality for the Vision page here

    # File uploader
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        image_container = st.empty()
        image_container.image(image, caption='Uploaded Image', use_column_width=True)

        # Analyze the image when user clicks the button
        if st.button('Analyze Image'):
            with st.spinner('Analyzing...'):
                # Convert image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format)
                img_bytes = img_byte_arr.getvalue()
                if model_type == "Standard":
                    results = analyze_image(img_bytes)
                else:
                    results = analyze_image_apples(img_bytes,image.format)
                #print(results)
            # Display results
            st.subheader("Image Analysis Results:")
            st.write("Description:", results.caption.text if results.get('caption') else "No caption available")
            # Display dense captions with confidence
            if results.get('denseCaptionsResult'):
                st.subheader("Dense Captions:")
                st.write("\n".join([f"Text: {caption.text}, Confidence: {caption.confidence:.2f}\n" for caption in results.get('denseCaptionsResult').list]))
            else:
                st.write("No dense captions")

            #st.write("Dense Captions:", ", ".join(results.dense_captions) if results.dense_captions else "No dense captions")
            st.subheader("Tags:")
            if results.get('tagsResult'):
                st.write("Tags:", ", ".join(results.get('tagsResult')))
                st.write("\n".join([f"Text: {tag.name}, Confidence: {tag.confidence:.2f}\n" for tag in results.get('tagsResult').list]))
            else:
                st.write("No tags")
            st.subheader("Objects:")
            if results.get('objectsResult'):
                #st.write("\n".join([f"Text: {thing.name}, Confidence: {thing.confidence:.2f}\n" for thing in results.objects.list]))
                st.write("\n".join([f"Name: {tag.name}, Confidence: {tag.confidence:.2f}\n" 
                    for obj in results.get('objectsResult').list for tag in obj.tags]))
            else:
                st.write("No objects")
            if results.get('peopleResult'):
                st.subheader("People:")
                st.write(f"Detected people: {sum(1 for person in results.get('peopleResult').list if person.confidence > 0.5)}")
            else:
                st.write("No people")
            if results.get('apples'):
                st.subheader("Apples:")
                image = Image.open(io.BytesIO(results['image']))
                image_container.image(image, caption='Uploaded Image', use_column_width=True)
                st.write("\n".join([f"Name: {obj.get('name')}, Confidence: {obj.get('confidence'):.2f}\n" 
                    for obj in results.get('apples')]))


