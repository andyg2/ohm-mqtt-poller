import base64
import os

def read_credentials_file():
    try:
        with open("enc.bin", "rb") as file:
            return file.read().decode().strip()
    except FileNotFoundError:
        return None

def write_credentials_file(encoded_credentials):
    with open("enc.bin", "wb") as file:
        file.write(encoded_credentials.encode())

def set_environment_variable(encoded_credentials):
    os.environ['RAMPMQTT'] = encoded_credentials
    print("Environment variable RAMPMQTT has been set.")

def encode_new_credentials():
    username = input("Enter MQTT username: ")
    password = input("Enter MQTT password: ")
    
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    # print(f"\nBase64 encoded credentials: {encoded_credentials}")
    
    write_credentials_file(encoded_credentials)
    print("Credentials have been saved to enc.bin")
    
    return encoded_credentials

def main():
    encoded_credentials = read_credentials_file()
    
    if encoded_credentials:
        print("Existing credentials found in enc.bin")
        # set_environment_variable(encoded_credentials)
    else:
        print("No existing credentials found. Please enter new credentials.")
        encoded_credentials = encode_new_credentials()
        # set_environment_variable(encoded_credentials)

if __name__ == "__main__":
    main()
