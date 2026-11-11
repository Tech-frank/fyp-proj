def try_again(self, key=None):
    """ Отправить запрос заново с ответом капчи

    :param key: ответ капчи
    """

    if key:
        self.key = key

        self.kwargs.update({
            'captcha_sid': self.sid,
            'captcha_key': self.key
        })

    return self.func(*self.args, **self.kwargs)
