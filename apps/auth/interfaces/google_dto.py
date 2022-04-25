from pydantic.networks import EmailStr


class GoogleIDInfoResponse:
    iss: str
    sub: str
    azp: str
    aud: str
    iat: str
    exp: str
    email: EmailStr
    email_verified: str
    name: str
    picture: str
    given_name: str
    family_name: str
    locale: str
