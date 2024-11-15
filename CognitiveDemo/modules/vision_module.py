
import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import io
from io import BytesIO
from PIL import Image, ImageDraw
import requests

# Get values from .env file
endpoint = os.getenv('AZURE_COGNITIVE_SERVICE_ENDPOINT')
key = os.getenv('AZURE_COGNITIVE_SERVICE_KEY')

# Initialize the client
image_analysis_client = ImageAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

def analyze_image(image):
    # Check if image is already bytes, if not, read it
    if isinstance(image, bytes):
        image_data = image
        image_url = None
    else:
        image_url = image
        image_data = None

    try:
        results = image_analysis_client.analyze(
            image_data=image_data,
            visual_features=[
                VisualFeatures.TAGS,
                VisualFeatures.OBJECTS,
                VisualFeatures.DENSE_CAPTIONS,
                VisualFeatures.PEOPLE
            ]
        )
        return dict(results)
    except Exception as e:
        # Handle exception
        print(f"Error analyzing image: {str(e)}")
        return None
    
# This function analyzes an image for specific object types and logs the findings.
# It specifically looks for apples and classifies them using Azure Custom Vision.
#
# Parameters:
# - image: The image to be analyzed, either as bytes or an image URL.
#
# Returns:
# - A dictionary containing detected apples and their confidence levels.
def analyze_image_apples(image, image_format):
    results = analyze_image(image)
    
    # Prepare Custom Vision headers and URL using environment variables.
    custom_vision_endpoint = os.getenv('AZURE_CUSTOM_VISION_ENDPOINT')
    project_id = os.getenv('AZURE_CUSTOM_VISION_PROJECT_ID')
    published_name = os.getenv('AZURE_CUSTOM_VISION_PUBLISHED_NAME')
    
    # Setting headers for the prediction request
    headers = {
        'Prediction-Key': os.getenv('AZURE_CUSTOM_VISION_PREDICTION_KEY'),
        'Content-Type': 'application/octet-stream'
    }
    prediction_url = f"{custom_vision_endpoint}/customvision/v3.0/Prediction/{project_id}/classify/iterations/{published_name}/image"

    apples = []  # Initialize an empty list to store detected apple types.

    # Iterate through detected objects in the results.
    for obj in results.get('objectsResult').list:
        # tags is a list of tags, we should iterate through it
        is_Apple=False
        for tag in obj.tags:
            print(f"Detected object: {tag.name} with confidence {tag.confidence * 100:.2f}%")
            if tag.name.lower() == "apple":
                is_Apple=True
        
        # Check if the detected object is an apple.
        if is_Apple:
            # Calculate coordinates for cropping the detected apple from the image.
            left = obj.bounding_box.x 
            top = obj.bounding_box.y 
            width = obj.bounding_box.width 
            height = obj.bounding_box.height 
            right = left + width
            bottom = top + height

            # Crop the image to the detected apple's bounding box. But the image is a bytes object, so we need to convert it to an image object
            cropped_image = Image.open(BytesIO(image)).crop((left, top, right, bottom))

            # Convert the cropped image to bytes for prediction request.
            image_stream = BytesIO()
            cropped_image.save(image_stream, format=image_format)
            image_stream.seek(0)
            image_bytes = image_stream.read()

            # Make the prediction request to Azure Custom Vision.
            response = requests.post(prediction_url, headers=headers, data=image_bytes)
            predictions = response.json()['predictions']

            # Get the highest probability prediction for apple type.
            top_prediction = max(predictions, key=lambda x: x['probability'])
            print(f"Apple Type: {top_prediction['tagName']} with confidence {top_prediction['probability'] * 100:.2f}%\n")
            
            # draw a red bounding box around the apple in the original image stream
            mod_image = Image.open(BytesIO(image))
            draw = ImageDraw.Draw(mod_image)
            draw.rectangle((left, top, right, bottom), outline="red", width=5)

            img_byte_arr = io.BytesIO()
            mod_image.save(img_byte_arr, format=image_format)
            image = img_byte_arr.getvalue()

            #refresh the "Uploaded Image in the vision page with the new image stream
            # Append the detected apple type and confidence to the apples list.
            apples.append({'boundingBox:':obj.bounding_box,'name': top_prediction['tagName'], 'confidence': top_prediction['probability'] * 100})
        else:
            print("\n")
    
    # Store the detected apples in the results for further processing or return.
    results['apples'] = apples
    results['image'] = image
    return results



