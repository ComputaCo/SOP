import stringcase


def camelize(name: str) -> str:
    return stringcase.camelcase(name.lower())
