import pytest
from main import BusinessContact, PersonalContact


def test_personal_contact_creation():
    """Перевірка створення особистого контакту."""
    contact = PersonalContact(
        name="Іван Петренко",
        phone="+380991234567",
        email="ivan@gmail.com",
        birthday="12.05.2000",
    )
    assert contact.name == "Іван Петренко"
    assert contact.phone == "+380991234567"
    assert contact.get_contact_type() == "Особистий"


def test_business_contact_creation():
    """Перевірка створення робочого контакту."""
    contact = BusinessContact(
        name="Ольга Коваль",
        phone="0677654321",
        email="olga@work.ua",
        company="TechCorp",
        position="Manager",
    )
    assert contact.company == "TechCorp"
    assert contact.get_contact_type() == "Робочий"


def test_phone_validation():
    """Перевірка валідації номеру телефону (інкапсуляція)."""
    contact = PersonalContact("Тест", "+380501234567", "test@mail.com")

    # Некоректний телефон має викликати ValueError
    with pytest.raises(ValueError):
        contact.phone = "123"