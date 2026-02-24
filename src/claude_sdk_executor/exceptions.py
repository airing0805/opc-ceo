"""自定义异常类"""


class ExecutorError(Exception):
    """执行器基础异常"""
    pass


class SessionNotFoundError(ExecutorError):
    """会话不存在"""
    pass


class ExecutionFailedError(ExecutorError):
    """执行失败"""
    pass


class SDKNotInstalledError(ExecutorError):
    """SDK 未安装"""
    pass
