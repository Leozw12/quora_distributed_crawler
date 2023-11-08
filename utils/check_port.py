import socket


def check(port: int):
    """
    检查端口是否可用
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(('127.0.0.1', port))
        return True  # 端口被使用
    except (ConnectionRefusedError, TimeoutError):
        return False  # 端口未使用


def check_increment(port: int):
    """
    递增检查直到遇到可用端口

    Returns:
        int: Available port numbers
    """
    while True:
        if port <= 65535:
            if not check(port):
                break
            port += 1
        else:
            return None
    return port


if __name__ == '__main__':
    print(check_increment(65535))
