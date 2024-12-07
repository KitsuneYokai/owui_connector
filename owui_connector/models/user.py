class User:
    id: str
    email: str
    name: str
    role: str
    profile_image_url: str

    def __init__(
        self, user_id: str, email: str, name: str, role: str, profile_image_url: str
    ):
        self.id = user_id
        self.email = email
        self.name = name
        self.role = role
        self.profile_image_url = profile_image_url
