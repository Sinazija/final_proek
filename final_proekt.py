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


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        self.value = value

    def next_birthday(self):
        today = date.today()
        next_birthday = date(today.year, self.value.month, self.value.day)
        if next_birthday < today:
            next_birthday = date(today.year + 1, self.value.month, self.value.day)
        return next_birthday

    def days_to_birthday(self):
        next_birthday = self.next_birthday()
        days_to_birthday = (next_birthday - date.today()).days
        return days_to_birthday


class Record:
    def __init__(self, name, phones=None, birthday=None):
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
        super().__init__()

    def add_record(self, record):
        self.data[record.name.value.lower()] = record

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

class CLI:
    def __init__(self):
        self.address_book = AddressBook()
        self.commands = {
            "hello": handle_hello,
            "add": handle_add,
            "change": handle_change,
            "phone": handle_phone,
            "show all": handle_show_all,
            "search": handle_search,
            "birthday": handle_birthday,
            "exit": handle_exit
        }
        
    def run(self):
        print("Hello! This is your address book.")
        print("Enter a command (type 'hello' for a list of commands):")
        while True:
            user_input = input("> ")
            command_parts = user_input.split(maxsplit=1)
            command_name = command_parts[0].lower()
            if command_name not in self.commands:
                print(f"Unknown command '{command_name}'. Type 'hello' for a list of commands.")
                continue
            if len(command_parts) > 1:
                args = command_parts[1].strip()
            else:
                args = ""
            result = self.commands[command_name](args, self.address_book)
            if result is not None:
                print(result)


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
    record = address_book.data.get(name.lower())
    if not record:
        raise KeyError(f"{name} is not in contacts")
    return "\n".join([phone.value for phone in record.phones])
                

@input_error
def handle_show_all(_, address_book):
    result = ""
    for record in address_book.data.values():
        result += f"{record.name.value}: {', '.join([phone.value for phone in record.phones])}\n"
    return result


@input_error
def handle_search(search_str, address_book):
    results = address_book.search(search_str)
    if len(results) == 0:
        return f"No matches found for '{search_str}'"
    else:
        result = ""
        for record in results:
            result += f"{record.name.value}: {', '.join([phone.value for phone in record.phones])}\n"
        return result
    

@input_error
def handle_birthday(_, address_book):
    result = ""
    for record in address_book.data.values():
        days_to_birthday = record.days_to_birthday()
        if days_to_birthday is not None:
            result += f"{record.name.value}'s birthday is in {days_to_birthday} days\n"
    if result == "":
        return "No birthdays coming up"
    else:
        return result


def handle_exit(*_):
    print("Goodbye!")
    exit()

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


address_book = AddressBook()
address_book.add_contact('John Doe', '123456789', 'johndoe@example.com')
address_book.save_to_file('address_book.json')



if __name__ == "__main__":
    cli = CLI()
    cli.run()