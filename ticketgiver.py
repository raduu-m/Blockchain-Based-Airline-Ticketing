import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import qrcode
from io import BytesIO
import base64

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

def create_ticket():
    st.title("✈️ Flight Ticket Generator")
    
    # Create two columns for passenger details
    col1, col2 = st.columns(2)
    
    with col1:
        first_name = st.text_input("First Name")
        departure = st.text_input("Departure City")
        departure_date = st.date_input("Departure Date", min_value=datetime.now())
        departure_time = st.time_input("Departure Time")
        seat = st.text_input("Seat Number", max_chars=3)

    with col2:
        last_name = st.text_input("Last Name")
        destination = st.text_input("Destination City")
        flight_duration = st.number_input("Flight Duration (hours)", min_value=0.5, max_value=24.0, value=2.0, step=0.5)
        flight_class = st.selectbox("Travel Class", ["Economy", "Business", "First Class"])
        
    # Generate ticket button
    if st.button("Generate Ticket"):
        if first_name and last_name and departure and destination:
            booking_ref = generate_booking_reference()
            qr_code = generate_qr_code(booking_ref)
            
            # Calculate arrival time
            departure_datetime = datetime.combine(departure_date, departure_time)
            arrival_datetime = departure_datetime + timedelta(hours=flight_duration)
            
            # Create ticket display
            st.markdown("---")
            st.subheader("🎫 Your Flight Ticket")
            
            # Ticket container with custom styling
            ticket_html = f"""
            <div style="border: 2px solid #1f77b4; border-radius: 10px; padding: 20px; background-color: white;">
                <h2 style="color: #1f77b4; text-align: center;">BOARDING PASS</h2>
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <p><strong>Passenger:</strong> {first_name} {last_name}</p>
                        <p><strong>From:</strong> {departure}</p>
                        <p><strong>To:</strong> {destination}</p>
                        <p><strong>Date:</strong> {departure_date.strftime('%B %d, %Y')}</p>
                    </div>
                    <div>
                        <p><strong>Flight:</strong> AN{random.randint(100, 999)}</p>
                        <p><strong>Seat:</strong> {seat}</p>
                        <p><strong>Class:</strong> {flight_class}</p>
                        <p><strong>Booking Ref:</strong> {booking_ref}</p>
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
            
            # Download button
            st.download_button(
                label="Download Ticket Details",
                data=f"""Flight Ticket Details:
Passenger: {first_name} {last_name}
From: {departure}
To: {destination}
Date: {departure_date}
Time: {departure_time}
Seat: {seat}
Class: {flight_class}
Booking Reference: {booking_ref}
                """,
                file_name="flight_ticket.txt",
                mime="text/plain"
            )
        else:
            st.error("Please fill in all required fields")

if __name__ == "__main__":
    st.set_page_config(page_title="Flight Ticket Generator", page_icon="✈️")
    create_ticket()