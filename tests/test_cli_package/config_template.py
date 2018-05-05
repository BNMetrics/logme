ver10_config = {
            'level': 'DEBUG',
            'formatter': '{asctime} - {name} - {levelname} - {message}',
            'StreamHandler': {
                'active': True,
                'level': 'DEBUG',
            },
            'FileHandler': {
                'active': False,
                'level': 'DEBUG',
                'filename': 'mylogpath/foo.log',
            },
            'NullHandler': {
                'active': False,
                'level': 'NOTSET'
            },
        }

ver11_config = {
            'level': 'DEBUG',
            'formatter': '{asctime} - {name} - {levelname} - {message}',
            'stream': {
                'type': 'StreamHandler',
                'active': True,
                'level': 'DEBUG',
            },
            'file': {
                'type': 'FileHandler',
                'active': False,
                'level': 'DEBUG',
                'filename': 'mylogpath/foo.log',
            },
            'null': {
                'type': 'NullHandler',
                'active': False,
                'level': 'NOTSET'
            },
        }