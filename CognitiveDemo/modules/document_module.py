# This module connects to Azure Cognitive Servcies multi service workspace to interpret documents, using Document
import os
import json
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

class DocumentModule:
    def __init__(self):
        self.document_key = os.getenv('AZURE_DOCUMENT_KEY')
        self.document_region = os.getenv('AZURE_DOCUMENT_REGION')
        self.document_endpoint_id = os.getenv('AZURE_DOCUMENT_ENDPOINT_ID')

# TODO: Implement the Document Module

# The get_document_properties method get a document stream or file in input and returns a json with the document properties
    def get_document_properties(self, document_input):
        pass

# The get_document_content method get a document stream or file in input and returns a json with the document content
    def get_document_content(self, document_input):
        pass


        def get_document_properties(self, document_input):
            # Initialize the Document Analysis client
            endpoint = f"https://{self.document_region}.api.cognitive.microsoft.com/"
            credential = AzureKeyCredential(self.document_key)
            client = DocumentAnalysisClient(endpoint=endpoint, credential=credential)

            # Determine if input is a file path or file-like object
            if isinstance(document_input, str):
                with open(document_input, "rb") as f:
                    document_data = f.read()
            else:
                document_data = document_input.read()

            # Analyze the document
            poller = client.begin_analyze_document("prebuilt-document", document_data)
            result = poller.result()

            # Extract document properties
            document_properties = {
                "pages": len(result.pages),
                "content": result.content,
                "languages": [language.code for language in result.languages],
                "styles": [style.is_handwritten for style in result.styles],
                "entities": [{"category": entity.category, "content": entity.content} for entity in result.entities]
            }

            return json.dumps(document_properties, indent=4)
