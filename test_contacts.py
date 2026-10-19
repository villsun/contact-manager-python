import pytest
from main import BusinessContact, PersonalContact


def test_personal_contact_creation():
    """Перевірка створення особистого контакту."""
    contact = PersonalContact(
        name="Test Tester",
        phone="+380000000000",
        email="test@gmail.com",
        birthday="12.05.2230",
    )
    assert contact.name == "Test Tester"
    assert contact.phone == "+380000000000"
    assert contact.get_contact_type() == "Особистий"


def test_business_contact_creation():
    """Перевірка створення робочого контакту."""
    contact = BusinessContact(
        name="Business Tester",
        phone="+380111111111",
        email="business@work.ua",
        company="Test Corp",
        position="Test Manager",
    )
    assert contact.company == "Test Corp"
    assert contact.get_contact_type() == "Робочий"


def test_phone_validation():
    """Перевірка валідації номеру телефону (інкапсуляція)."""
    contact = PersonalContact("Mock User", "+380501234567", "test@mail.com")

    # Некоректний телефон має викликати ValueError
    with pytest.raises(ValueError):
        contact.phone = "123"