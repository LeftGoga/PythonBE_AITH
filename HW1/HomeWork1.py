import json
from urllib.parse import parse_qs


def fibonacci(n):
    if not isinstance(n, float):
        raise SyntaxError()
    if n < 0:
        raise ValueError()
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)


def factorial(n):

    if n < 0:
        raise ValueError()
    elif n == 0:
        return 1
    else:
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result


def mean(numbers):

    if not numbers:
        raise ValueError()
    return sum(numbers) / len(numbers)


async def send_response(send, status, body):
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            [b'content-type', b'application/json'],
        ]
    })
    await send({
        'type': 'http.response.body',
        'body': body.encode('utf-8'),
    })


async def app(scope, receive, send):

    query_string = scope.get('query_string', b'').decode('utf-8')
    query_params = parse_qs(query_string)
    try:
        if scope["path"].startswith("/fibonacci/"):

            if not scope["path"].split("/")[-1].lstrip('-+').isnumeric():
                raise SyntaxError()

            n = float(scope["path"].split("/")[-1])

            result = fibonacci(n)
            body = json.dumps({"result": result})
            await send_response(send,200, body)
            return

        elif scope["path"].startswith("/factorial"):

            if not query_params.get('n'):
                raise SyntaxError()
            if not query_params.get('n', [''])[0].lstrip('-+').isnumeric():
                raise SyntaxError()
            n = int(query_params.get('n', [''])[0])

            result = factorial(n)
            body = json.dumps({"result": result})
            await send_response(send,200, body)
            return

        elif scope["path"].startswith("/mean"):
            request = await receive()
            body = request['body'].decode('utf-8')
            print(body, type(body))

            if not body:
                raise SyntaxError
            try:
                json.loads(body)

            except:
                raise SyntaxError

            nums = json.loads(body)
            if not isinstance(nums, list) or not all(isinstance(x, (int, float)) for x in nums):
                raise SyntaxError()

            result = mean(nums)
            response = json.dumps({'result': result})
            await send_response(send, 200, response)
            return

        else:
            status = 404
            body = b"Error 404"

    except SyntaxError:
        status = 422
        body = b"Error 422"

    except ValueError:
        status = 400
        body = b"Error 400"

    await send(
        {
                "type": "http.response.start",
                "status": status,
                "headers": [[b"content-type", b"text/plain"],],
        }
        )
    await send(
            {
                "type": "http.response.body",
                "body": body,
                "more_body": False,
            }
        )
if __name__ == "__main__":
    print(mean("test"))