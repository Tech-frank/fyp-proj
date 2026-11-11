def _clone_init_kwargs(self, *args, **kw):
    # Parent kwargs
    kwargs = super(Config, self)._clone_init_kwargs(*args, **kw)
    # Transmit our internal SSHConfig via explicit-obj kwarg, thus
    # bypassing any file loading. (Our extension of clone() above copies
    # over other attributes as well so that the end result looks consistent
    # with reality.)
    new_config = SSHConfig()
    # TODO: as with other spots, this implies SSHConfig needs a cleaner
    # public API re: creating and updating its core data.
    new_config._config = copy.deepcopy(self.base_ssh_config._config)
    return dict(kwargs, ssh_config=new_config)
