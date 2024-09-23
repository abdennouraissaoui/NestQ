import bcrypt


class Hash:
    def bcrypt(password: str) -> str:
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        return hashed_password

    def verify(hashed_password: bytes, plain_password: str) -> bool:
        return bcrypt.checkpw(
            password=plain_password.encode("utf-8"), hashed_password=hashed_password
        )


if __name__ == "__main__":
    print(Hash.bcrypt("password"))
    print(
        Hash.verify(
            hashed_password=b"$2b$12$bOyHKV3mhRLtQ5xYY4q5R.GbMD5vTQuGtflBWF7Ryyh/FDT83NVT6",
            plain_password="password",
        )
    )
