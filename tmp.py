import os
if os.path.exists('refresh_token.txt'):
    with open('refresh_token.txt', 'r') as file:
        refresh_token = file.read().strip()
        print(refresh_token)

# if __name__ == "__main__":
    # Replace with a real parent CallSid to test
    