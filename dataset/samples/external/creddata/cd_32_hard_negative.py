def __init__(self, username, password, token=None, cookies=None, appid=None, plugin_token=None, ifencodepwd=False,
             login=True, checkssl=False):
    """
    :param username: 你的微信公众平台账户用户名
    :param password: 你的微信公众平台账户密码
    :param token: 直接导入的 ``token`` 值, 该值需要在上一次该类实例化之后手动进行缓存并在此传入, 如果不传入, 将会在实例化的时候自动获取
    :param cookies: 直接导入的 ``cookies`` 值, 该值需要在上一次该类实例化之后手动进行缓存并在此传入, 如果不传入, 将会在实例化的时候自动获取
    :param appid: 直接导入的 ``appid`` 值, 该值需要在上一次该类实例化之后手动进行缓存并在此传入, 如果不传入, 将会在调用 stat_ 开头的方法(统计分析类)时自动获取
    :param plugin_token: 直接导入的 ``plugin_token`` 值, 该值需要在上一次该类实例化之后手动进行缓存并在此传入, 如果不传入, 将会在调用 stat_ 开头的方法(统计分析类)时自动获取
    :param ifencodepwd: 密码是否已经经过编码, 如果密码已经经过加密, 此处为 ``True`` , 如果传入的密码为明文, 此处为 ``False``
    :param login: 是否在初始化过程中尝试登录 (推荐此处设置为 ``False``, 然后手动执行登录以方便进行识别验证码等操作, 此处默认值为 ``True`` 为兼容历史版本
    :param checkssl: 是否检查 SSL, 默认为 False, 可避免 urllib3 的 InsecurePlatformWarning 警告
    """
    if not checkssl:
        disable_urllib3_warning()  # 可解决 InsecurePlatformWarning 警告

    self.__username = username
    if ifencodepwd:
        self.__password = password
    else:
        self.__password = hashlib.md5(password).hexdigest()
    self.__cookies = cookies
    self.__lastmsgid = 0
    self.__token = token

    self.__ticket = None
    self.__ticket_id = None
    self.__fakeid = None

    self.__appid = appid
    self.__plugin_token = plugin_token

    if not self.__token or not self.__cookies:
        self.__token = ''
        self.__cookies = ''
        self.__appid = ''
        self.__plugin_token = ''
        if login:
            self.login()
