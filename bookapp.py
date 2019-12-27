import re
import traceback

from bookdb import BookDB

DB = BookDB()


def book(book_id):
    book = DB.title_info(book_id)
    if not book:
        raise NameError
    body = """
    <h1>{title}</h1>
    <table>
        <tr><th align="left">Author</th><td>{author}</td></tr>
        <tr><th align="left">Publisher</th><td>{publisher}</td></tr>
        <tr><th align="left">ISBN</th><td>{isbn}</td></tr>
    </table>
    <a href="/">Return to all books</a>
    """.format(**book)
    return body

def books():
    all_books = DB.titles()
    body = ['<h1>My Library</h1>', '<ul>']
    book_template = '<li><a href="/book/{id}">{title}</a></li>'
    for book in all_books:
        body.append(book_template.format(**book))
    body.append('</ul>')

    return '\n'.join(body)

def resolve_path(path):
    functions = {'':books,
                 'book':book}
    path = path.strip('/').split('/')
    func_name = path[0]
    args = path[1:]
    try:
        func = functions[func_name]
    except KeyError:
        raise NameError

    return func, args

def application(environ, start_response):
    headers = [('Content-type', 'text/html')]
    try:
        path = environ.get('PATH_INFO', None)
        if not path:
            raise NameError
        func, args = resolve_path(path)
        status = "200 OK"
        body = func(*args)
    except NameError:
        status = "404 Not Found"
        body = "<h1>Not Found</h1>"
    except Exception:
        status = "500 Internal Server Error"
        body = "<h1>Internal Server Error</h1>"
        print(traceback.format_exc())
    finally:
        headers.append(('Content-length',str(len(body))))
        start_response(status, headers)
        return [body.encode('utf8')]

    start_response(status, headers)
    return ["<h1>No Progress Yet</h1>".encode('utf8')]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
