import os

cash_fp = os.path.dirname(__file__) + '/cash.txt'


def __retrace__(task):
    """

    :param task: str:【返回】【退出】
    :return:
    """
    with open(cash_fp, 'w', encoding='utf-8') as f:
        f.write(task)
