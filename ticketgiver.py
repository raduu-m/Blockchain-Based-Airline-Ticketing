import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import qrcode
from io import BytesIO
import base64
import uuid
import os
import requests

def generate_booking_reference():
    """Generate a 6-character booking reference"""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choices(chars, k=6))

def generate_qr_code(booking_ref):
    """Generate QR code for the booking reference"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(booking_ref)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert PIL image to bytes
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def validate_user_id(user_id):
    """Validate if user ID matches required format"""
    if len(user_id) >= 5 and user_id.isalnum():
        return True
    return False

def initialize_company_id():
    """Initialize or retrieve company ID"""
    if not os.path.exists('company_id.txt'):
        company_id = str(uuid.uuid4())
        with open('company_id.txt', 'w') as f:
            f.write(company_id)
        
        # Register company ID with the API
        try:
            response = requests.post(
                "http://localhost:8080/accounts",
                json={"id": company_id},
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to register company ID: {e}")
            return None
    
    # Read the company ID from file
    with open('company_id.txt', 'r') as f:
        return f.read().strip()

def create_ticket():
    st.title("✈️ Flight Ticket Generator")
    
    # Initialize company ID
    company_id = initialize_company_id()
    if not company_id:
        st.error("Failed to initialize company ID")
        return

    # Generate booking UUID at the start
    booking_uuid = str(uuid.uuid4())
    
    # Create two columns for input details
    col1, col2 = st.columns(2)
    
    with col1:
        user_id = st.text_input("User ID", help="Enter your unique user ID (minimum 5 alphanumeric characters)")
        departure = st.text_input("Departure City")
        departure_date = st.date_input("Departure Date", min_value=datetime.now())
        departure_time = st.time_input("Departure Time")

    with col2:
        seat = st.text_input("Seat Number", max_chars=3)
        destination = st.text_input("Destination City")
        flight_duration = st.number_input("Flight Duration (hours)", min_value=0.5, max_value=24.0, value=2.0, step=0.5)
        flight_class = st.selectbox("Travel Class", ["Economy", "Business", "First Class"])
    
    # Create columns for buttons
    button_col1, button_col2, button_col3 = st.columns([1, 1, 2])
    
    # Generate ticket button in first column
    generate_pressed = button_col1.button("Generate Ticket")
    
    # Initialize session state for ticket generation status if not exists
    if 'ticket_generated' not in st.session_state:
        st.session_state['ticket_generated'] = False
        
    if generate_pressed:
        if user_id and departure and destination:
            if validate_user_id(user_id):
                st.session_state['ticket_generated'] = True
                booking_ref = generate_booking_reference()
                qr_code = generate_qr_code(booking_ref)
                
                # Calculate arrival time
                departure_datetime = datetime.combine(departure_date, departure_time)
                arrival_datetime = departure_datetime + timedelta(hours=flight_duration)
                
                # Create NFT payload
                payload = {
                    "name": "Transferable NFT",
                    "description": "This NFT will be transferred",
                    "owner": company_id,
                    "metadata": {
                        'id': booking_uuid,
                        'document_type': 3,
                        'date_added': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        'image': qr_code,
                        'profile_type': 'Individual'
                    }
                }
                
                # Store payload in session state for download button
                st.session_state['transfer_payload'] = {
                    'from': company_id,
                    'to': user_id,
                    'nft_id': booking_uuid
                }
                
                # Create ticket display
                st.markdown("---")
                st.subheader("🎫 Your Flight Ticket")
                
                # Ticket container with custom styling
                ticket_html = f"""
                <div style="border: 2px solid #1f77b4; border-radius: 10px; padding: 20px; background-color: white;">
                    <h2 style="color: #1f77b4; text-align: center;">BOARDING PASS</h2>
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <p><strong>User ID:</strong> {user_id}</p>
                            <p><strong>From:</strong> {departure}</p>
                            <p><strong>To:</strong> {destination}</p>
                            <p><strong>Date:</strong> {departure_date.strftime('%B %d, %Y')}</p>
                        </div>
                        <div>
                            <p><strong>Flight:</strong> AN{random.randint(100, 999)}</p>
                            <p><strong>Seat:</strong> {seat}</p>
                            <p><strong>Class:</strong> {flight_class}</p>
                            <p><strong>Booking Ref:</strong> {booking_ref}</p>
                            <p><strong>Booking UUID:</strong> {booking_uuid}</p>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 10px;">
                        <p><strong>Departure:</strong> {departure_time.strftime('%H:%M')}</p>
                        <p><strong>Arrival:</strong> {arrival_datetime.strftime('%H:%M')}</p>
                    </div>
                    <div style="text-align: center; margin-top: 10px;">
                        <img src="data:image/png;base64,{qr_code}" 
                             style="width: 150px; height: 150px;"/>
                    </div>
                </div>
                """
                st.markdown(ticket_html, unsafe_allow_html=True)
            else:
                st.error("Invalid User ID format. Please use at least 5 alphanumeric characters.")
        else:
            st.error("Please fill in all required fields")

    # Download button in second column, only visible after ticket generation
    if st.session_state.get('ticket_generated', False):
        if button_col2.download_button(
            label="Download Ticket",
            data=str(st.session_state['transfer_payload']),
            file_name="ticket_transfer.json",
            mime="application/json"
        ):
            try:
                # You can add API call here to handle the transfer
                st.success("Ticket transfer initiated successfully!")
            except Exception as e:
                st.error(f"Failed to initiate transfer: {e}")

if __name__ == "__main__":
    st.set_page_config(page_title="Flight Ticket Generator", page_icon="✈️")
    create_ticket()