import pytest
from main import BusinessContact, ContactManager, JSONStorage, PersonalContact


def test_contact_manager_workflow(tmp_path):
    # Використовуємо тимчасовий файл для ізоляції тестів сховища
    test_file = tmp_path / "manager_test.json"
    storage = JSONStorage(filename=str(test_file))
    manager = ContactManager(storage)

    # Створюємо контакти з технічними тестовими даними
    c1 = PersonalContact(
        name="Test User 123",
        phone="+380000000001",
        email="test1@test.com",
        birthday="01.01.2000",
    )
    c2 = BusinessContact(
        name="Test Company 456",
        phone="+380000000002",
        email="test2@test.com",
        company="Company 123",
        position="Position 789",
    )

    # 1. Перевірка додавання
    manager.add_contact(c1)
    manager.add_contact(c2)
    assert len(manager.get_all_contacts()) == 2

    # 2. Перевірка пошуку за ім'ям (регістронезалежного)
    search_results = manager.search_contacts("test user 123")
    assert len(search_results) == 1
    assert search_results[0].name == "Test User 123"

    # 3. Перевірка пошуку за частиною номера телефону
    phone_results = manager.search_contacts("0000000002")
    assert len(phone_results) == 1
    assert phone_results[0].company == "Company 123"

    # 4. Перевірка видалення
    # Видаляємо перший контакт
    success = manager.delete_contact(0)
    assert success is True
    assert len(manager.get_all_contacts()) == 1
    # Перевіряємо, що залишився правильний контакт
    assert manager.get_all_contacts()[0].name == "Test Company 456"

    # 5. Перевірка видалення за неіснуючим індексом
    assert manager.delete_contact(99) is False