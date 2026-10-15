import re
from abc import ABC, abstractmethod


class Contact(ABC):
    """Базовий абстрактний клас контакту (демонстрація інкапсуляції та абстракції)."""

    def __init__(self, name: str, phone: str, email: str):
        self.name = name
        self._phone = ""
        self._email = ""

        # Викликаємо сеттери для валідації вводу
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
        """Повертає тип контакту."""
        pass

    @abstractmethod
    def get_details(self) -> str:
        """Поліморфний метод для отримання деталей."""
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
    """Особистий контакт (успадкування від Contact)."""

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
    """Робочий контакт (успадкування від Contact)."""

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


if __name__ == "__main__":
    print("Прототип 1: Класи моделей успішно ініціалізовані!")