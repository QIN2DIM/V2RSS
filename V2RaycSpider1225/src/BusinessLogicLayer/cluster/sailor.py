# TODO 该模块存在大量exec用法，请勿随意改动相关文件名或函数名
__all__ = ['manage_task']

import random

from src.BusinessCentralLayer.middleware.redis_io import RedisClient
from src.BusinessCentralLayer.middleware.work_io import Middleware
from src.BusinessCentralLayer.setting import CRAWLER_SEQUENCE, REDIS_SECRET_KEY, SINGLE_TASK_CAP, ENABLE_DEPLOY, \
    SINGLE_DEPLOYMENT, logger
from src.BusinessLogicLayer.cluster.cook import ActionShunt
from src.BusinessLogicLayer.cluster.slavers.actions import __entropy__
from src.BusinessLogicLayer.plugins.accelerator import ShuntRelease


def _is_overflow(task_name: str, rc=None):
    """
    判断当前缓存是否已达单机采集极限
    @param task_name: class_
    @param rc: RedisClient Object Driver API
    @return:
        --stop: 停止任务同步并结束本轮采集任务
        --offload：停止任务同步并开始执行采集任务
        --continue：继续同步任务
    """

    # TODO 将缓存操作原子化
    cap: int = SINGLE_TASK_CAP

    # 获取当前仓库剩余
    storage_remain: int = rc.__len__(REDIS_SECRET_KEY.format(f'{task_name}'))

    # 获取本机任务缓存
    cache_size: int = Middleware.poseidon.qsize()

    # 判断任务队列是否达到满载状态或已溢出
    if storage_remain >= cap:
        logger.warning(f'<TaskManager> OverFlow || 任务溢出<{task_name}>({storage_remain}/{cap})')
        return 'stop'

    # 判断缓冲队列是否已达单机采集极限
    # 未防止绝对溢出，此处限制单机任务数不可超过满载值的~x％
    # x = 1 if signal collector else x = 1/sum (Number of processes)
    elif storage_remain + cache_size > round(cap * 0.8):
        # 若已达或超过单机采集极限，则休眠任务
        logger.info(f'<TaskManager> BeatPause || 节拍停顿<{task_name}>({storage_remain + cache_size}/{cap})')
        return 'offload'

    # 否则可以继续同步任务
    else:
        return 'continue'


def _update_entropy(rc=None):
    # 组合entropy标注数据
    try:
        atomic_queue = []
        for i in __entropy__:
            work_filed = [f"{j[0].upper()}" for j in i['hyper_params'].items() if j[-1]]
            work_filed = "&".join(work_filed).strip()
            atomic_item = f"|{work_filed}| {i['name']}"
            atomic_queue.append(atomic_item)
        # 更新列表
        if rc is None:
            rc = RedisClient()
        rc.get_driver().set(name=REDIS_SECRET_KEY.format("__entropy__"), value="$".join(atomic_queue))
    except Exception as e:
        logger.exception(e)


def _sync_actions(
        class_: str,
        mode_sync: str = None,
        only_sync=False,
        beat_sync=True,
):
    """

    @param class_:
    @param mode_sync:  是否同步消息队列。False：同步本机任务队列，True：同步Redis订阅任务
    @param only_sync:
    @param beat_sync:
    @return:
    """
    logger.info(f"<TaskManager> Sync{mode_sync.title()} || 正在同步<{class_}>任务队列...")

    # ================================================
    # 节拍停顿 原子同步
    # ================================================
    rc = RedisClient()
    _state = _is_overflow(task_name=class_, rc=rc)
    if _state == 'stop':
        return _state

    # ================================================
    # 更新任务信息
    # ================================================
    _update_entropy(rc=rc)

    sync_queue: list = ActionShunt(class_, silence=True, beat_sync=beat_sync).shunt()
    random.shuffle(sync_queue)

    # ================================================
    # $执行核心业务
    # ================================================
    if mode_sync == 'upload':

        # fixme:临时方案:解决链接溢出问题
        if round(rc.__len__(REDIS_SECRET_KEY.format(class_)) * 1.25) > SINGLE_TASK_CAP:
            logger.warning("<TaskManager> UploadHijack -- 连接池任务即将溢出，上传任务被劫持")
            return None

        # 持续实例化采集任务
        for _ in range(sync_queue.__len__()):

            rc.sync_message_queue(mode='upload', message=class_)

            # 节拍同步线程锁
            if only_sync:
                logger.warning("<TaskManager> OnlySync -- 触发节拍同步线程锁，仅上传一枚原子任务")
                break
        logger.success("<TaskManager> UploadTasks -- 任务上传完毕")
    elif mode_sync == 'download':
        async_queue: list = []

        while True:

            # 获取原子任务
            atomic = rc.sync_message_queue(mode='download')

            # 若原子有效则同步数据
            if atomic and atomic in CRAWLER_SEQUENCE:

                # 判断同步状态
                # 防止过载。当本地缓冲任务即将突破容载极限时停止同步
                # _state 状态有三，continue/offload/stop
                _state = _is_overflow(task_name=atomic, rc=rc)
                if _state != 'continue':
                    return _state

                if async_queue.__len__() == 0:
                    async_queue = ActionShunt(atomic, silence=True, beat_sync=beat_sync).shunt()
                    random.shuffle(async_queue)

                # 将执行语句推送至Poseidon本机消息队列
                Middleware.poseidon.put_nowait(async_queue.pop())

                logger.info(f'<TaskManager> offload atomic<{atomic}>({Middleware.poseidon.qsize()})')

                # 节拍同步线程锁
                if only_sync:
                    logger.warning(f"<TaskManager> OnlySync -- <{atomic}>触发节拍同步线程锁，仅下载一枚原子任务")
                    return 'offload'

            # 否则打印警告日志并提前退出同步
            else:
                # logger.warning(f"<TaskManager> SyncFinish -- <{atomic}>无可同步任务")
                return 'offload'
    elif mode_sync == 'force_run':
        for slave_ in sync_queue:

            # force_run ：适用于单机部署或单步调试下
            # 需要确保无溢出风险，故即使是force_run的启动模式，任务执行数也不应逾越任务容载数
            _state = _is_overflow(task_name=class_, rc=rc)
            if _state != 'continue':
                return _state

            # 将执行语句推送至Poseidon本机消息队列
            Middleware.poseidon.put_nowait(slave_)

            # 在force_run模式下仍制约于节拍同步线程锁
            # 此举服务于主机的订阅补充操作
            # 优先级更高，不受队列可用容载影响强制中断同步操作
            if only_sync:
                logger.warning(f"<TaskManager> OnlySync -- <{class_}>触发节拍同步线程锁，仅下载一枚原子任务")
                return 'stop'

        return 'offload'


@logger.catch()
def manage_task(
        class_: str = 'v2ray',
        only_sync=False,
        startup=None,
        beat_sync=True,
        force_run=None
) -> bool:
    """
    加载任务
    @param force_run: debug模式下的强制运行，可逃逸队列满载检测
    @param startup:创建协程工作空间，并开始并发执行队列任务。
    @param only_sync:节拍同步线程锁。当本机任务数大于0时，将1枚原子任务推送至Poseidon协程空间。
    @param class_: 任务类型,必须在 crawler seq内,如 ssr,v2ray or trojan。
    @param beat_sync:
    @return:
    """

    # ----------------------------------------------------
    # 参数审查与转译
    # ----------------------------------------------------

    # 检查输入
    # 若申请执行的任务类型不在本机授权范围内则结束本次任务
    if class_ not in CRAWLER_SEQUENCE or not isinstance(class_, str):
        return False

    # 检查采集器权限
    # 审核采集权限，允许越权传参。当手动指定参数时，可授予本机采集权限，否则使用配置权限
    local_work: bool = startup if startup else ENABLE_DEPLOY.get('tasks').get('collector')

    # 强制运行：指定参数优先级更高，若不指定则以是否单机部署模式决定运行force_run是否开启
    # 默认单机模式下开启force_run
    # 若未传参时也未定义部署形式（null），则默认不使用force_run
    force_run = force_run if force_run else SINGLE_DEPLOYMENT

    # ----------------------------------------------------
    # 解析同步模式
    # ----------------------------------------------------
    # 以本机是否有采集权限来区分download 以及upload两种同步模式
    mode_sync = "download" if local_work else "upload"

    # 以更高优先级的`force_run` 替代传统同步模式，执行强制采集方案
    mode_sync = "force_run" if force_run else mode_sync

    # ----------------------------------------------------
    # 同步消息（任务）队列
    # ----------------------------------------------------
    # 当本机可采集时，将任务同步至本机执行，若消息队列为空则
    # 若本机不可采集，则生成任务加入消息队列
    response: str or bool = _sync_actions(
        class_=class_,
        only_sync=only_sync,
        beat_sync=beat_sync,
        mode_sync=mode_sync,
    )

    # ----------------------------------------------------
    # 初始化协程空间（执行任务）
    # ----------------------------------------------------

    # 若本机开启了采集器权限则创建协程空间
    # 若从control-deploy进入此函数，则说明本机必定具备创建协程空间权限
    if force_run:
        if response == 'offload' and Middleware.poseidon.qsize() > 0:
            logger.info(f'<TaskManager> ForceRun || <{class_}>采集任务启动')
            ShuntRelease(work_queue=Middleware.poseidon).interface()
        logger.success(f'<TaskManager> ForceWorkFinish || <{class_}>采集任务结束')
        return True

    # if 'force_run' is False and the node has the permissions of collector
    if local_work:
        # if task queue can be work
        if response == 'offload' and Middleware.poseidon.qsize() > 0:
            logger.info(f'<TaskManager> Run || 采集任务启动')
            ShuntRelease(work_queue=Middleware.poseidon).interface()
        logger.success(f'<TaskManager> Finish || 采集任务结束')
        return True
    else:
        # logger.warning(f"<TaskManager> Hijack<{class_}> || 当前节点不具备采集权限")
        return False


if __name__ == '__main__':
    # _sync_actions('ssr', only_sync=True, mode_sync='upload')
    # manage_task('v2ray')
    _update_entropy()
