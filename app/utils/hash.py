

from passlib.context import CryptContext

ctx = CryptContext(schemes="bcrypt", deprecated="auto")


class Hash:
    def bcrypt(self,plain_password: str):
        return ctx.hash(plain_password)

    def verify(self, plain_password: str, encrypted_password: str):
        return ctx.verify(plain_password, encrypted_password)