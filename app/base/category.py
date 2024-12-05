class Category(str):
    def __new__(cls, name):
        return super().__new__(cls, name)

    def to_plural(self):
        if self == "dog":
            return "dogs"
        elif self == "person":
            return "owners"
        return f"{self}s"