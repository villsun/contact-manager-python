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

class ContactManager:
    def __init__(self, storage: StorageStrategy):
        self.storage = storage
        self.contacts = self.storage.load()  # Завантажуємо існуючі контакти при старті

    def add_contact(self, contact: Contact) -> None:
        self.contacts.append(contact)
        self.storage.save(self.contacts)

    def get_all_contacts(self) -> list:
        return self.contacts

    def search_contacts(self, query: str) -> list:
        query = query.lower()  # Переводимо пошуковий запит у нижній регістр
        matching_contacts = []  # Список для збереження знайдених контактів

        for contact in self.contacts:
            # Перевіряємо кожне поле окремо для наочності
            name_match = query in contact.name.lower()
            phone_match = query in contact.phone.lower()
            email_match = query in contact.email.lower()

            # Якщо пошуковий запит збігається хоча б з одним із полів
            if name_match or phone_match or email_match:
                matching_contacts.append(contact)

        return matching_contacts

    def delete_contact(self, index: int) -> bool:
        if 0 <= index < len(self.contacts):
            del self.contacts[index]
            self.storage.save(self.contacts)
            return True
        return False

def main():
    storage = JSONStorage("contacts.json")
    manager = ContactManager(storage)

    while True:
        print("\n=== МЕНЕДЖЕР КОНТАКТІВ ===")
        print("1. Переглянути всі контакти")
        print("2. Додати особистий контакт")
        print("3. Додати робочий контакт")
        print("4. Пошук контактів")
        print("5. Видалити контакт")
        print("0. Вихід")

        choice = input("Оберіть опцію: ").strip()

        if choice == "1":
            contacts = manager.get_all_contacts()
            if not contacts:
                print("\nСписок контактів порожній.")
            else:
                print("\n--- СПИСОК КОНТАКТІВ ---")
                for idx, c in enumerate(contacts):
                    print(f"{idx}. {c.get_details()}")

        elif choice == "2":
            try:
                name = input("Ім'я: ")
                phone = input("Телефон: ")
                email = input("Email: ")
                birthday = input("День народження (необов'язково): ")
                contact = PersonalContact(name, phone, email, birthday)
                manager.add_contact(contact)
                print("Особистий контакт успішно додано!")
            except ValueError as e:
                print(f"Помилка валідації: {e}")

        elif choice == "3":
            try:
                name = input("Ім'я: ")
                phone = input("Телефон: ")
                email = input("Email: ")
                company = input("Компанія: ")
                position = input("Посада: ")
                contact = BusinessContact(name, phone, email, company, position)
                manager.add_contact(contact)
                print("Робочий контакт успішно додано!")
            except ValueError as e:
                print(f"Помилка валідації: {e}")

        elif choice == "4":
            query = input("Введіть пошуковий запит (ім'я або телефон): ")
            results = manager.search_contacts(query)
            if not results:
                print("Нічого не знайдено.")
            else:
                print("\n--- РЕЗУЛЬТАТИ ПОШУКУ ---")
                for c in results:
                    print(c.get_details())

        elif choice == "5":
            contacts = manager.get_all_contacts()
            if not contacts:
                print("Немає контактів для видалення.")
                continue
            for idx, c in enumerate(contacts):
                print(f"{idx}. {c.get_details()}")
            try:
                idx_to_del = int(input("Введіть номер контакту для видалення: "))
                if manager.delete_contact(idx_to_del):
                    print("Контакт успішно видалено!")
                else:
                    print("Невірний номер контакту.")
            except ValueError:
                print("Будь ласка, введіть число.")

        elif choice == "0":
            print("До побачення!")
            break
        else:
            print("Невірний вибір. Спробуйте ще раз.")

if __name__ == "__main__":
    main()