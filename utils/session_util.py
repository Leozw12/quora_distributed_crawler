import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def build_session_with_retry(retries=5, backoff_factor=1.5, status_forcelist=(403, 404, 429, 500, 502, 503, 504), session=None):
    """构建具有重试机制的请求会话
    
    Args:
        retries (int, optional): 重试次数，默认为 3.
        backoff_factor (float, optional): 重试间隔的倍数，默认为 1.5.
        status_forcelist (tuple[int], optional): 重试的 HTTP 状态码列表，默认为 (500, 502, 503, 504).
        session (requests.Session, optional): 要使用的会话对象，默认为 None，会创建一个新的会话.

    Returns:
        requests.Session: 具有重试机制的请求会话对象.
    """
    session = session or requests.Session()
    
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=['POST']
    )

    adapter = HTTPAdapter(max_retries=retry)

    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
