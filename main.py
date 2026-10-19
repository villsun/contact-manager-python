import re
from abc import ABC, abstractmethod
import json
import os

class Contact(ABC):
    def __init__(self, name: str, phone: str, email: str):
        self.name = name
        self._phone = ""
        self._email = ""

        self.phone = phone
        self.email = email

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        cleaned_phone = re.sub(r"[^\d+]", "", value)
        if not cleaned_phone or len(cleaned_phone) < 7:
            raise ValueError("Номер телефону повинен містити щонайменше 7 цифр.")
        self._phone = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        if value and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", value):
            raise ValueError("Некоректний формат email адреси.")
        self._email = value

    @abstractmethod
    def get_contact_type(self) -> str:
        pass

    @abstractmethod
    def get_details(self) -> str:
        pass

    def to_dict(self) -> dict:
        """Конвертація об'єкта в словник для збереження."""
        return {
            "type": self.get_contact_type(),
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
        }


class PersonalContact(Contact):

    def __init__(self, name: str, phone: str, email: str, birthday: str = ""):
        super().__init__(name, phone, email)
        self.birthday = birthday

    def get_contact_type(self) -> str:
        return "Особистий"

    def get_details(self) -> str:
        bday_str = f", День народження: {self.birthday}" if self.birthday else ""
        return f"[Особистий] {self.name} | Тел: {self.phone} | Email: {self.email}{bday_str}"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["birthday"] = self.birthday
        return data


class BusinessContact(Contact):

    def __init__(
        self,
        name: str,
        phone: str,
        email: str,
        company: str = "",
        position: str = "",
    ):
        super().__init__(name, phone, email)
        self.company = company
        self.position = position

    def get_contact_type(self) -> str:
        return "Робочий"

    def get_details(self) -> str:
        comp_str = (
            f", Компанія: {self.company} ({self.position})"
            if self.company
            else ""
        )
        return f"[Робочий] {self.name} | Тел: {self.phone} | Email: {self.email}{comp_str}"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["company"] = self.company
        data["position"] = self.position
        return data

class StorageStrategy(ABC):
    @abstractmethod
    def save(self, contacts: list) -> None:
        pass

    @abstractmethod
    def load(self) -> list:
        pass


class JSONStorage(StorageStrategy):
    def __init__(self, filename: str = "contacts.json"):
        self.filename = filename

    def save(self, contacts: list) -> None:
        """Серіалізація списку контактів у JSON файл."""
        data = [contact.to_dict() for contact in contacts]
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load(self) -> list:
        """Десеріалізація та відновлення об'єктів контактів із JSON файлу."""
        if not os.path.exists(self.filename):
            return []

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                contacts = []
                for item in data:
                    c_type = item.get("type")
                    if c_type == "Особистий":
                        contact = PersonalContact(
                            name=item.get("name", ""),
                            phone=item.get("phone", ""),
                            email=item.get("email", ""),
                            birthday=item.get("birthday", ""),
                        )
                        contacts.append(contact)
                    elif c_type == "Робочий":
                        contact = BusinessContact(
                            name=item.get("name", ""),
                            phone=item.get("phone", ""),
                            email=item.get("email", ""),
                            company=item.get("company", ""),
                            position=item.get("position", ""),
                        )
                        contacts.append(contact)
                return contacts
        except (json.JSONDecodeError, KeyError):
            # Якщо файл пошкоджено, повертаємо порожній список
            return []