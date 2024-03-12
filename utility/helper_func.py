from uuid import uuid4
import random

def generate_otp(uuid = uuid4()):
  return ''.join(random.sample(uuid.hex, 6)).upper()


