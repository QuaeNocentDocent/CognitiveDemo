## Testing the demo solution

- clone the repository, run the following command in your terminal:
  - git clone https://github.com/QuaeNocentDocent/CognitiveDemo.git

it is strongly advised to create a python virtual environment, for example you can use: python -m venv .env
source .env/bin/activate

To run the solution, ensure you have the required packages installed. You can do this using pip:
pip install -r requirements.txt

## Setup Secrets 
To set up your keys/secrets, create a .env.local file in the root directory and add the following keys in the specified format:
OPENAI_API_KEY=your_openai_api_key_here
SOME_OTHER_KEY=your_other_key_here

### Example .env file content:
AZURE_COGNITIVE_SERVICE_KEY=your_cognitbve_key
AZURE_COGNITIVE_SERVICE_ENDPOINT=https://<yourname>.cognitiveservices.azure.com/

You can use the .env file as a template

## Running the demo
Run the Streamlit application using the following command:
streamlit run app.py
