from aisle.lexer.lexer import Lexer


def main():  # pragma: no cover
    src = (
        'service Backend:\n'
        '    Provides API\n'
        '    Maybe split into microservices later\n'
        '    tech = Litestar, sqlalchemy, \n'
        '           faststream\n'
        '    links:\n'
        '        --> Anti-fraud Service over HTTP'
    )
    print(len(src))
    lexer = Lexer(src)
    tokens = lexer.scan()
    for token in tokens:
        print(token)


if __name__ == '__main__':
    main()
