import streamlit as st
import qrcode
from PIL import Image
import io
import base64
import json
from datetime import datetime
import uuid
import requests
import os
import dotenv
from enum import Enum

dotenv.load_dotenv()

def fetch_documents(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch documents from the API")
        return []

# Create a file with a user id if there is no file
if not os.path.exists('user_id.txt'):
    with open('user_id.txt', 'w') as f:
        user_id = str(uuid.uuid4())
        f.write(user_id)
    response = requests.post(
        "http://localhost:8080/accounts",
        json={"id": user_id},
        headers={'Content-Type': 'application/json'}
    )
# Read the user id from the file
with open('user_id.txt', 'r') as f:
    user_id = f.read()
    if 'documents' not in st.session_state:
        api_url = f"http://localhost:8080/accounts/{user_id}/nfts"  # Replace with your API URL
        jsons = fetch_documents(api_url)
        files = [metadata for json_ in jsons for metadata in json_['metadata']]
        st.session_state.documents = jsons
    else:
        st.session_state.documents = []


# Get backend link from environment variables
BACKEND_LINK = os.getenv('BACKEND_LINK')
if not BACKEND_LINK:
    raise ValueError("BACKEND_LINK not found in environment variables")

def create_document_payload(doc):
    """Create a JSON payload with document information"""
    # ... existing imports and code ...

    payload = {
        'document': {
            'id': doc['id'],
            'type': doc['document_type'],
            'date_added': doc['date_added'],
            'profile_type': doc['profile_type'],
            'profile_info': st.session_state.profile_data[doc['profile_type']]
        }
    }
    return json.dumps(payload)

if 'profile_type' not in st.session_state:
    st.session_state.profile_type = 'Individual'
if 'profile_data' not in st.session_state:
    st.session_state.profile_data = {
        'Individual': {
            'name': '',
            'email': '',
            'phone': '',
            'address': '',
            'dob': None,
            'bio': '',
            'profile_pic': None
        },
        'Company': {
            'company_name': '',
            'business_email': '',
            'phone': '',
            'address': '',
            'registration_number': '',
            'industry': '',
            'founding_date': None,
            'description': '',
            'logo': None
        }
    }

DOCUMENT_TYPES = {
    'passport': 'International travel document',
    'id_card': 'National identification card',
    'pass': 'Access or membership pass'
}

class DocumentType(Enum):
    Passport = 1,
    IdCard = 2,
    Pass = 3
    
    @staticmethod
    def get_mapping(document_):
        if document_ == 'passport':
            return 1
        elif document_ == 'id_card':
            return 2
        elif document_ == 'pass':
            return 3

def generate_qr_code(data):
    """Generate QR code from document data"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

def save_document(document_type, uploaded_file):
    """Save document to session state with UUID"""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        b64 = base64.b64encode(bytes_data).decode()
        
        document = {
            'id': str(uuid.uuid4()),  # Generate UUID for document
            'document_type': document_type,
            'image': b64,
            'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'profile_type': st.session_state.profile_type
        }
        
        payload = {
            "name": "Transferable NFT",
            "description": "This NFT will be transferred",
            "owner": user_id,
            "metadata":{
                'id': str(uuid.uuid4()),  # Generate UUID for document
                'document_type': DocumentType.get_mapping(document_type),
                'date_added': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                'image': b64,
                'profile_type': str(st.session_state.profile_type)   
            }
        }
        
        # print(payload)
        try:
            response = requests.post(
                "http://localhost:8080/nfts",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            print(response)
            
            if not response.ok:
                st.error("Failed to store document on blockchain")
                return False
                
        except Exception as e:
            st.error(f"Error connecting to blockchain backend: {str(e)}")
            return False
        st.session_state.documents.append(document)
        return True
    return False

def update_profile(profile_type, data, profile_pic=None):
    """Update profile information"""
    if profile_pic:
        bytes_data = profile_pic.getvalue()
        b64 = base64.b64encode(bytes_data).decode()
        data['profile_pic' if profile_type == 'Individual' else 'logo'] = b64
    
    st.session_state.profile_data[profile_type].update(data)
    return True

def delete_profile_picture(profile_type):
    """Delete profile picture/logo"""
    pic_key = 'profile_pic' if profile_type == 'Individual' else 'logo'
    st.session_state.profile_data[profile_type][pic_key] = None

# Main app layout
st.title("Documents Dashboard")

# Sidebar with profile toggle
with st.sidebar:
    st.title("Profile Settings")
    profile_type = st.radio(
        "Select Profile Type",
        options=['Individual', 'Company'],
        key='profile_type'
    )
    
    st.divider()
    
    # Enhanced document addition section
    st.subheader("Add New Document")
    with st.form("new_document"):
        doc_type = st.selectbox(
            "Document Type",
            options=list(DOCUMENT_TYPES.keys()),
            format_func=lambda x: x.replace('_', ' ').title(),
            help="Select the type of document you're adding"
        )
        
        st.write(f"**Type Description:** {DOCUMENT_TYPES[doc_type]}")
        
        # Options to either upload or take a picture
        option = st.radio("Select an option:", ["Upload Image", "Take Picture"], horizontal=True)
        doc_file = None
        
        if option == "Upload Image":
            doc_file = st.file_uploader("Upload image", type=['png', 'jpg', 'jpeg'])
        elif option == "Take Picture":
            doc_file = st.camera_input("Take a photo")
        
        submitted = st.form_submit_button("Add Document")
        if submitted:
            if doc_file:
                if save_document(doc_type, doc_file):
                    
                    st.success(f"Document added successfully! (ID: {st.session_state.documents[-1]['id']})")
            else:
                st.error("Please provide an image")

# Main content area
tab2, tab3,tab1, = st.tabs(["Documents List", "Document Details","Profile"])

# Profile Tab

# Documents List Tab
with tab2:
    
    # Filter documents based on profile type
    filtered_documents = [doc for doc in st.session_state.documents]
    filtered_documents = [doc['metadata'] for doc in filtered_documents]
    print('*'*50)
    print(filtered_documents)
    print('*'*50)
    st.header(f"{'Personal' if profile_type == 'Individual' else 'Business'} Documents")
    
    # Add sorting options
    sort_col1, sort_col2 = st.columns([2, 1])
    with sort_col1:
        sort_by = st.selectbox(
            "Sort by",
            options=["Date (Newest First)", "Date (Oldest First)"],
            key="sort_documents"
        )
    
    # Sort documents based on selection
    if sort_by == "Date (Newest First)":
        filtered_documents.sort(key=lambda x: x['date_added'], reverse=True)
    elif sort_by == "Date (Oldest First)":
        filtered_documents.sort(key=lambda x: x['date_added'])
    
    # Display document count
    st.write(f"Total documents: {len(filtered_documents)}")
    
    if not filtered_documents:
        st.info(f"No {'personal' if profile_type == 'Individual' else 'business'} documents added yet. Use the sidebar to add new documents.")
    else:
        # Display documents in a grid layout
        for i in range(0, len(filtered_documents), 2):
            col1, col2 = st.columns(2)
            
            if i < len(filtered_documents):
                doc = filtered_documents[i]
                with col1:
                    st.image(base64.b64decode(doc['image']), use_container_width=True)
                    if doc['document_type'] == 1:
                        doc_type = 'Passport'
                    elif doc['document_type'] == 2:
                        doc_type = 'ID Card'
                    else:
                        doc_type = 'Pass'
                    st.write(f"**Type:** {doc_type}")
                    st.write(f"**Added On:** {doc['date_added']}")
            
            if i + 1 < len(filtered_documents):
                doc = filtered_documents[i + 1]
                with col2:
                    st.image(base64.b64decode(doc['image']), use_container_width=True)
                    st.write(f"**Type:** {doc['document_type'].replace('_', ' ').title()}")
                    st.write(f"**Added On:** {doc['date_added']}")

# Document Details Tab
with tab3:
    
    # Document selection dropdown
    st.session_state.documents = [doc['metadata'] for doc in st.session_state.documents]
    for doc in st.session_state.documents:
        print(doc)
        doc_type = doc['document_type']
        if doc_type == 1:
            doc['document_type'] = 'Passport'
        elif doc_type == 2:
            doc['document_type'] = 'ID Card'
        else:
            doc['document_type'] = 'Pass'
    doc_options = {doc['id']: f"{doc['document_type']} (Added on {doc['date_added']})" for doc in st.session_state.documents}
    
    selected_doc_id = st.selectbox(
        "Select a document to view details",
        options=doc_options.keys(),
        format_func=lambda x: doc_options[x]
    )
    
    if selected_doc_id:
        selected_doc = next((doc for doc in st.session_state.documents if doc['id'] == selected_doc_id), None)
        if selected_doc:
            st.image(base64.b64decode(selected_doc['image']), use_container_width=True)
            st.write(f"**Document Type:** {selected_doc['document_type'].replace('_', ' ').title()}")
            st.write(f"**Date Added:** {selected_doc['date_added']}")
            
            qr_code_data = json.dumps({
                'document_id': selected_doc['id'],
                'document_type': selected_doc['document_type'],
                'date_added': selected_doc['date_added']
            })
            qr_code_img = generate_qr_code(qr_code_data)
            st.image(qr_code_img, caption="QR Code", use_container_width=True)


with tab1:
    st.header(f"{'Personal' if profile_type == 'Individual' else 'Business'} Profile")
    
    # Profile Picture/Logo Column
    col1, col2 = st.columns([1, 2])
    with col1:
        pic_key = 'profile_pic' if profile_type == 'Individual' else 'logo'
        current_pic = st.session_state.profile_data[profile_type].get(pic_key)
        
        if current_pic:
            # When picture exists, show it with delete button
            st.image(base64.b64decode(current_pic), width=200)
            if st.button("Delete Profile Picture" if profile_type == 'Individual' else "Delete Logo"):
                delete_profile_picture(profile_type)
                st.rerun()
        else:
            # When no picture exists, show upload widget
            upload_container = st.container()
            with upload_container:
                pic_upload = st.file_uploader(
                    "Upload Profile Picture" if profile_type == 'Individual' else "Upload Company Logo",
                    type=['png', 'jpg', 'jpeg'],
                    key="profile_pic_upload"
                )
                
                if pic_upload:
                    # If file is uploaded, show preview and confirm button
                    st.image(pic_upload, width=200)
                    if st.button("Confirm Upload"):
                        profile_data = st.session_state.profile_data[profile_type].copy()
                        update_profile(profile_type, profile_data, pic_upload)
                        st.rerun()
                    if st.button("Cancel"):
                        st.session_state.profile_pic_upload = None
                        st.rerun()

    # Profile Information Column
    with col2:
        with st.form("profile_form"):
            if profile_type == 'Individual':
                name = st.text_input("Full Name", st.session_state.profile_data['Individual']['name'])
                email = st.text_input("Email", st.session_state.profile_data['Individual']['email'])
                phone = st.text_input("Phone", st.session_state.profile_data['Individual']['phone'])
                address = st.text_area("Address", st.session_state.profile_data['Individual']['address'])
                dob = st.date_input("Date of Birth", st.session_state.profile_data['Individual']['dob'])
                bio = st.text_area("Bio", st.session_state.profile_data['Individual']['bio'])
                
                if st.form_submit_button("Update Profile"):
                    profile_data = {
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'address': address,
                        'dob': dob,
                        'bio': bio
                    }
                    if update_profile('Individual', profile_data):
                        st.success("Profile updated successfully!")
            
            else:  # Company profile
                company_name = st.text_input("Company Name", st.session_state.profile_data['Company']['company_name'])
                business_email = st.text_input("Business Email", st.session_state.profile_data['Company']['business_email'])
                phone = st.text_input("Phone", st.session_state.profile_data['Company']['phone'])
                address = st.text_area("Address", st.session_state.profile_data['Company']['address'])
                reg_number = st.text_input("Registration Number", st.session_state.profile_data['Company']['registration_number'])
                industry = st.text_input("Industry", st.session_state.profile_data['Company']['industry'])
                founding_date = st.date_input("Founding Date", st.session_state.profile_data['Company']['founding_date'])
                description = st.text_area("Company Description", st.session_state.profile_data['Company']['description'])
                
                if st.form_submit_button("Update Profile"):
                    profile_data = {
                        'company_name': company_name,
                        'business_email': business_email,
                        'phone': phone,
                        'address': address,
                        'registration_number': reg_number,
                        'industry': industry,
                        'founding_date': founding_date,
                        'description': description
                    }
                    if update_profile('Company', profile_data):
                        st.success("Company profile updated successfully!")