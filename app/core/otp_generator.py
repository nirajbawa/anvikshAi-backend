import secrets

def generate_otp(length: int = 6) -> str:
    otp = ''.join(str(secrets.randbelow(10)) for _ in range(length))  # Generates a numeric OTP
    return otp