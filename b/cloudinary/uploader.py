import core.cloudinary 

def upload(file, folder):
    url = "https://api.cloudinary.com/v1_1/<cloud_name>/image/upload"

    # Build multipart/form-data
    files = {
        "file": file
    }

    # Build form fields
    data = {
        "folder": folder,
        "api_key": API_KEY,
        "timestamp": timestamp,
        "signature": signature,
    }

    # Send HTTP request
    response = requests.post(
        url,
        files=files,
        data=data,
    )

    # Parse JSON response
    return response.json()