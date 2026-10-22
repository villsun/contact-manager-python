import json
import os
import re
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import messagebox, ttk


class Contact(ABC):

    def __init__(self, name: str, phone: str, email: str):
        self.name = name
        self._phone = ""
        self._email = ""

        # Використання сеттерів для валідації
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
        """Поліморфний метод для отримання повних деталей контакту."""
        pass

    def to_dict(self) -> dict:
        """Словникове представлення для збереження."""
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
        data = [contact.to_dict() for contact in contacts]
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load(self) -> list:
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
            return []

class ContactManager:
    def __init__(self, storage: StorageStrategy):
        self.storage = storage
        self.contacts = self.storage.load()

    def add_contact(self, contact: Contact) -> None:
        self.contacts.append(contact)
        self.storage.save(self.contacts)

    def get_all_contacts(self) -> list:
        return self.contacts

    def search_contacts(self, query: str) -> list:
        query = query.lower()
        matching_contacts = []

        for contact in self.contacts:
            name_match = query in contact.name.lower()
            phone_match = query in contact.phone.lower()
            email_match = query in contact.email.lower()

            if name_match or phone_match or email_match:
                matching_contacts.append(contact)

        return matching_contacts

    def delete_contact(self, index: int) -> bool:
        if 0 <= index < len(self.contacts):
            del self.contacts[index]
            self.storage.save(self.contacts)
            return True
        return False

class ContactManagerUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Система управління контактами")
        self.root.geometry("800x500")

        self.storage = JSONStorage("contacts.json")
        self.manager = ContactManager(self.storage)

        self._build_ui()
        self.refresh_list()

    def _build_ui(self):
        # Панель пошуку
        search_frame = ttk.LabelFrame(self.root, text="Пошук контактів")
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Запит:").pack(side="left", padx=5, pady=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # Таблиця контактів (Treeview)
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("type", "name", "phone", "email", "extra")
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.tree.heading("type", text="Тип")
        self.tree.heading("name", text="ПІБ / Ім'я")
        self.tree.heading("phone", text="Телефон")
        self.tree.heading("email", text="Email")
        self.tree.heading("extra", text="Додаткова інформація")

        self.tree.column("type", width=90)
        self.tree.column("name", width=160)
        self.tree.column("phone", width=120)
        self.tree.column("email", width=150)
        self.tree.column("extra", width=200)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управління
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="Додати контакт", command=self.open_add_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Видалити обраний", command=self.delete_selected_contact).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Оновити список", command=self.refresh_list).pack(side="right", padx=5)

    def refresh_list(self, contacts_list=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        items = contacts_list if contacts_list is not None else self.manager.get_all_contacts()
        for idx, contact in enumerate(items):
            extra = ""
            if isinstance(contact, PersonalContact):
                extra = f"Д/Н: {contact.birthday}" if contact.birthday else ""
            elif isinstance(contact, BusinessContact):
                extra = f"Компанія: {contact.company} ({contact.position})"

            self.tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    contact.get_contact_type(),
                    contact.name,
                    contact.phone,
                    contact.email,
                    extra,
                ),
            )

    def on_search(self, event):
        query = self.search_entry.get()
        results = self.manager.search_contacts(query)
        self.refresh_list(results)

    def delete_selected_contact(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Увага", "Оберіть контакт у списку для видалення.")
            return

        idx = int(selected[0])
        if messagebox.askyesno("Підтвердження", "Ви впевнені, що хочете видалити цей контакт?"):
            if self.manager.delete_contact(idx):
                self.refresh_list()
                messagebox.showinfo("Успіх", "Контакт успішно видалено!")
            else:
                messagebox.showerror("Помилка", "Не вдалося видалити контакт.")

    def open_add_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Додавання нового контакту")
        dialog.geometry("400x380")
        dialog.grab_set()

        ttk.Label(dialog, text="Тип контакту:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        type_var = tk.StringVar(value="Особистий")
        type_cb = ttk.Combobox(dialog, textvariable=type_var, values=["Особистий", "Робочий"], state="readonly")
        type_cb.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        fields = {}
        labels = [
            ("Ім'я / ПІБ:", "name"),
            ("Телефон:", "phone"),
            ("Email:", "email"),
            ("День народження:", "birthday"),
            ("Компанія:", "company"),
            ("Посада:", "position"),
        ]

        for i, (label_text, key) in enumerate(labels, start=1):
            ttk.Label(dialog, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ent = ttk.Entry(dialog)
            ent.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            fields[key] = ent

        def toggle_fields(*args):
            if type_var.get() == "Особистий":
                fields["birthday"].config(state="normal")
                fields["company"].config(state="disabled")
                fields["position"].config(state="disabled")
            else:
                fields["birthday"].config(state="disabled")
                fields["company"].config(state="normal")
                fields["position"].config(state="normal")

        type_var.trace_add("write", toggle_fields)
        toggle_fields()

        def save_contact():
            try:
                ctype = type_var.get()
                name = fields["name"].get().strip()
                phone = fields["phone"].get().strip()
                email = fields["email"].get().strip()

                if not name:
                    raise ValueError("Ім'я не може бути порожнім.")

                if ctype == "Особистий":
                    contact = PersonalContact(name, phone, email, fields["birthday"].get().strip())
                else:
                    contact = BusinessContact(
                        name, phone, email, 
                        fields["company"].get().strip(), 
                        fields["position"].get().strip()
                    )

                self.manager.add_contact(contact)
                self.refresh_list()
                dialog.destroy()
                messagebox.showinfo("Успіх", "Контакт успішно додано!")
            except ValueError as e:
                messagebox.showerror("Помилка валідації", str(e))

        ttk.Button(dialog, text="Зберегти", command=save_contact).grid(row=7, column=0, columnspan=2, pady=15)


if __name__ == "__main__":
    root = tk.Tk()
    app = ContactManagerUI(root)
    root.mainloop()