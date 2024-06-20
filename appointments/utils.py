# appointments/utils.py
import segno
from io import BytesIO
import base64

def generate_appointment_qr_code(appointment):
    # Construct QR Code Data
    data = f"Appointment Details:\n\n"
    data += f"Reference Number: {appointment.reference_number}\n"
    data += f"Full Name: {appointment.full_name}\n"
    data += f"Phone Number: {appointment.phone_number}\n"
    data += f"Email: {appointment.email}\n"
    data += f"Dentist: {appointment.dentist}\n"
    data += f"Date: {appointment.date}\n"
    data += f"Time: {appointment.time.strftime('%H:%M')}\n"
    data += f"Service: {appointment.service}\n"
    if appointment.notes:
        data += f"Notes: {appointment.notes}\n"

    # Generate QR Code Image
    qr = segno.make_qr(data)
    img_buffer = BytesIO()
    qr.save(img_buffer, kind='png', scale=10)  # Adjust scale as needed
    img_buffer.seek(0)

    # Encode image to base64
    img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    return img_str
