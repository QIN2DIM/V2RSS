import requests


def get_header(use_faker=True) -> str:
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                             " Chrome/91.0.4472.164 Safari/537.36 Edg/91.0.864.71"}
    try:
        if use_faker:
            # from faker import Faker
            # import tempfile
            # from fake_useragent import UserAgent
            # from config import SERVER_PATH_DATABASE_HEADERS, SERVER_DIR_DATABASE, logger
            #
            # try:
            #     if SERVER_PATH_DATABASE_HEADERS not in os.listdir(tempfile.gettempdir()):
            #         os.system('copy {} {}'.format(
            #             os.path.join(SERVER_DIR_DATABASE, SERVER_PATH_DATABASE_HEADERS),
            #             os.path.join(tempfile.gettempdir(), SERVER_PATH_DATABASE_HEADERS)
            #         ))
            #     headers.update({"User-Agent": UserAgent().random})
            # except Exception as e:
            #     logger.exception(e)
            from faker import Faker
            headers.update({"User-Agent": Faker().user_agent()})

    finally:
        return headers['User-Agent']


def get_proxy(deployment=False) -> str or bool:
    """
    需要开启另一个项目，在本机生成代理，占用端口号为5555，使用HTTP通信
    @param deployment:
    @return:
    """
    proxy_pool_interface = 'http://127.0.0.1:5555/random'
    if deployment:
        try:
            return 'http://{}'.format(requests.get(proxy_pool_interface).text.strip())
        except requests.exceptions.RequestException:
            return False
