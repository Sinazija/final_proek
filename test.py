from collections import UserDict
from datetime import date, datetime
import re
import pickle



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.value == other.value
        return self.value == other

    def __hash__(self):
        return hash(self.value)

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value
        
        
class Name(Field):
    pass


class Phone(Field):
     def set_value(self, value):
        if not re.match(r'^\+38\d{10}$', value):
            raise ValueError("Phone number should be in the format +380XXXXXXXXX")
        self.value = value


class Birthday():
    def __init__(self, day, month):
        self.day = day
        self.month = month
    
    def set_value(self, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        self.value = value
        
    def next_birthday(self):
        today = date.today()
        next_birthday = date(today.year, self.month, self.day)
        if next_birthday < today:
            next_birthday = date(today.year+1, self.month, self.day)
        return next_birthday
    
    def days_to_birthday(self):
        next_birthday = self.next_birthday()
        days_to_birthday = (next_birthday - date.today()).days
        return days_to_birthday


class Record:
    def __init__(self, name, phones=None,birthday=None):
        self.name = Name(name)
        self.phones = phones or []
        self.birthday = birthday
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        return False

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return True
        return False

    def days_to_birthday(self):
        if self.birthday:
            return self.birthday.days_to_birthday()
        else:
            return None

    
class AddressBook(UserDict):
    def __init__(self):
        self.data = {}
        self.records = {}
    def add_contact(self, name, phone, email):
        self.contacts.append({'name': name, 'phone': phone, 'email': email})
        
    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(address_book.data, file)
            print("Address book has been saved to file.")
            
    def load_from_file(self, filename):
        try:
            with open(filename, 'rb') as file:
                data = pickle.load(file)
                address_book = AddressBook()
                address_book.data = data  # додали рядок для збереження завантажених даних
                return address_book
        except FileNotFoundError:
            print("File not found.")
            return AddressBook()      
    
    def add_record(self, record):
        self.data[record.name.value] = record

    def search(self, search_str):
        results = []
        for record in self.data.values():
            if search_str.lower() in record.name.value.lower():
                results.append(record)
            else:
                for phone in record.phones:
                    if search_str in phone.value:
                        results.append(record)
                        break
        return results
            
    def __iter__(self):
        self.iter_index = 0
        self.n = 5
        self.iter_keys = list(self.data.keys())
        return self

    def __next__(self):
        if self.iter_index < len(self.iter_keys):
            records = []
            for key in self.iter_keys[self.iter_index:min(self.iter_index+self.n, len(self.iter_keys))]:
                records.append(f"{self.data[key].name.value}: {', '.join([phone.value for phone in self.data[key].phones])}")
            self.iter_index += self.n
            return "\n".join(records)
        raise StopIteration
    

def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except (KeyError, ValueError, IndexError) as f:
            return str(f)
    return inner


@input_error
def handle_hello():
    return "How can I help you?"


@input_error
def handle_add(name, phone, address_book):
    if len(name.strip()) == 0 or len(phone.strip()) == 0:
        raise ValueError("Please enter both name and phone number")
    record = address_book.records.get(name.lower())
    if not record:
        record = Record(name)
        address_book.add_record(record)
    record.add_phone(phone)
    return f"Added phone {phone} for contact {name}"


@input_error
def handle_change(name, old_phone, new_phone, address_book):
    record = address_book.get(name.lower())
    if not record:
        raise KeyError(f"{name} is not in contacts")
    if not record.edit_phone(old_phone, new_phone):
        raise ValueError(f"{old_phone} is not in {name}'s phones")
    return f"Changed phone {old_phone} to {new_phone} for contact {name}"


@input_error
def handle_phone(name, address_book):
    record = address_book.get(name.lower())
    if not record:
        raise KeyError(f"{name} is not in contacts")
    return "\n".join([phone.value for phone in record.phones])


@input_error
def handle_show_all(address_book):
    return "\n".join([f"{name}: {', '.join([phone.value for phone in record.phones])}" for name, record in address_book.items()])


@input_error
def handle_search(search_str, address_book):
    if len(search_str.strip()) == 0:
        raise ValueError("Please enter a search string")
    split_command = search_str.split()
    if len(split_command) < 2:
        raise ValueError(
            "Invalid search format. Please enter a search string and try again.")
    results = address_book.search(split_command[1])
    if not results:
        return f"No contacts found for '{split_command[1]}'"
    else:
        return "\n".join([f"{record.name.value}: {', '.join([phone.value for phone in record.phones])}" for record in results])


def main():
    address_book = AddressBook()

    while True:
        command = input("Enter a command: ").lower()
        if command == "hello":
            print(handle_hello())
        elif command == '.':
            break
        elif command.startswith("add"):
            try:
                name, phone = command.split()[1:]
                print(handle_add(name, phone, address_book))
            except ValueError as e:
                print(str(e))
        elif command.startswith("change"):
            try:
                name, old_phone, new_phone = command.split()[1:]
                print(handle_change(name, old_phone, new_phone, address_book))
            except ValueError as e:
                print(str(e))
            except KeyError as e:
                print(str(e))
        elif command.startswith("phone"):
            try:
                name = command.split()[1]
                print(handle_phone(name, address_book))
            except KeyError as e:
                print(str(e))
        elif command == "show all":
            print(handle_show_all(address_book))
        elif command.startswith("search"):
            try:
                search_str = command.split()[1]
                print(handle_search(search_str, address_book))
            except IndexError:
                print("You have entered insufficient arguments")
            except ValueError as e:
                print(str(e))
        elif command in ("good bye", "close", "exit",):
            print("Good bye!")
            break
        else:
            print("Unknown command. Please try again.")


if __name__ == '__main__':
    main()
    address_book = AddressBook()
    address_book.add_contact('John Doe', '123456789', 'johndoe@example.com')
    address_book.save_to_file('address_book.json')