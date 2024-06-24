# test_argon2_passlib.py
from passlib.hash import argon2

hashed_password = argon2.hash("mysecretpassword")
print("Hashed password:", hashed_password)

is_correct = argon2.verify("mysecretpassword", hashed_password)
print("Password match:", is_correct)

