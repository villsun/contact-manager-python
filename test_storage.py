import os
import pytest
from main import BusinessContact, JSONStorage, PersonalContact


def test_json_storage_save_and_load(tmp_path):
    """Перевірка збереження та завантаження контактів через JSONStorage."""
    test_file = tmp_path / "test_contacts.json"
    storage = JSONStorage(filename=str(test_file))

    # Створюємо тестові контакти
    c1 = PersonalContact(
        name="Test User One",
        phone="+380991111111",
        email="one@test.com",
        birthday="01.01.2000",
    )
    c2 = BusinessContact(
        name="Test User Two",
        phone="+380992222222",
        email="two@test.com",
        company="TestLab",
        position="Developer",
    )

    # Зберігаємо
    storage.save([c1, c2])
    assert os.path.exists(test_file)

    # Завантажуємо назад
    loaded_contacts = storage.load()
    assert len(loaded_contacts) == 2

    # Перевіряємо дані першого контакту
    assert loaded_contacts[0].name == "Test User One"
    assert loaded_contacts[0].get_contact_type() == "Особистий"
    assert loaded_contacts[0].birthday == "01.01.2000"

    # Перевіряємо дані другого контакту
    assert loaded_contacts[1].name == "Test User Two"
    assert loaded_contacts[1].get_contact_type() == "Робочий"
    assert loaded_contacts[1].company == "TestLab"