import logging

log = logging.getLogger(__name__)


def change_password(user, new_password, store):
    store.set_password(user.id, new_password)
    log.info("password changed for user %s", user.id)
    return True
