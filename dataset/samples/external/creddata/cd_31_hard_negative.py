self.__conf = WechatConf(
    token=token,
    appid=appid,
    appsecret=appsecret,

    access_token=access_token,
    access_token_expires_at=access_token_expires_at,
    jsapi_ticket=jsapi_ticket,
    jsapi_ticket_expires_at=jsapi_ticket_expires_at,

    encrypt_mode='normal',

    partnerid=partnerid,
    partnerkey=partnerkey,
    paysignkey=paysignkey,
    checkssl=checkssl,
)
