def on_ws_connect(self, name=None):
    return self._create_registration_function(
        handler_type='on_ws_connect',
        name=name,
        registration_kwargs={'route_key': '$connect'},
    )
