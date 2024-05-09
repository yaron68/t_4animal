
import re


def is_valid_israeli_id(id_number):
    # Remove leading/trailing whitespaces
    id_number = id_number.strip()

    # Check for invalid length (more than 9 digits or not a number)
    if len(id_number) > 9 or not id_number.isdigit():
        return False

    # Pad ID with leading zeros if less than 9 digits
    if len(id_number) < 9:
        id_number_complete = "0" * (9 - len(id_number)) + id_number
    else:
        id_number_complete = id_number

    # Convert ID digits to integers
    digits = [int(d) for d in id_number_complete]

    # Calculate checksum using Luhn algorithm variation
    checksum = 0
    weight = 1
    for i, digit in enumerate(digits[:-1]):  # Exclude the last digit (checksum)
        if digit * weight < 10:
            checksum += digit * weight
        else:
            checksum += digit * weight // 10 + digit * weight % 10
        weight = 1 if weight == 2 else 2

    # Check if checksum digit (last digit) matches calculated value
    return (checksum % 10) == digits[-1]


def is_filed_valid(name, value, required):
    print(f"{name} :  {str(value)}")
    pattern = ""
    if required and value is None:
        return False, f"The {name} filed is required"
    elif not required and value is None:
        return True, ""
    if name == "full_name":
        pattern = r"^[A-Za-z]+(?: [A-Za-z]+)*$"  # Matches one or more words with spaces
    elif name == "Teudat_Zehut" or name == "current_owner":
        if is_valid_israeli_id(value):
            return True, ""
        else:
            return False, "Fix isreali id"
    elif name == "address":
        pattern = r"^(?:[A-Za-z]+\s?)+\d+$"
    elif name == "city":
        pattern = r"^[A-Za-z]+(?:\s[-'\w]*)*$"  # Allows letters, spaces, hyphens, and apostrophes
    elif name == "mail":
        pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
    elif name == "phone":
        pattern = r"^0[1-9]\d?[1-9][0-9]{6}$"
    elif name == "owner_of":
        pattern = r"^(?:[A-Z][a-z]+(?: [A-Z][a-z]+)*|\b[a-z]{2,}-\w+\b)$"
    elif name == "name":
        pattern = r"^(?:[A-Za-z][a-z]+(?: [A-Za-z][a-z]+)*|\b[a-z]{2,}-\w+\b)$"
    elif name == "gender":
        pattern = r"^(Male|Female)$"
    elif name == "color":
        r"^[A-Za-z]+(?: [A-Za-z]+)*$"
    elif name == "birth_date" or name == "arrival":
        pattern = r"^\d{4}-\d{2}-\d{2}$"
    elif name == "age":
        pattern = r"^[1-9]\d*(?:\.\d{1})?$"
    elif name == "species":
        pattern = r"^(Dog|Cat|Fish|Bird|Reptie|Other)$"
    elif name == "breed_name":
        pattern = r"^(?:[A-Za-z]+(?: [A-Za-z]+)*|\b[a-z]{2,}-\w+\b)$"
    elif name == "chip_number":
        pattern = r"^9\d{14}$"
    elif name == "spayed_neutered":
        pattern = r"^(True|False)$"
    # elif name == "foster":
    #     pattern = r"^ (True|False)$"
    elif name == "vaccines":
        pattern = r"^ [ ^,]+(?:, \s *[^, ]+) *$"
    elif name == "current_owner":
        pattern = r"^(?!0)\d+"

    result = bool(re.match(pattern, str(value)))
    if result:
        return result, ""
    else:
        return result, f"Fix the {name} filed"


def validate_form(**fields):
    validation = True
    errors = []
    for field, param_dict in fields.items():
        name = param_dict['name']
        value = param_dict['value']
        required = param_dict['required']
        valid, error = is_filed_valid(name, value, required)
        if not valid:
            validation = False
            errors.append(error)
    return validation, errors