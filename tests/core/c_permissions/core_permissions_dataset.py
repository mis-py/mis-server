from fastapi import status

positive_get_permissions_dataset = [
    (
        {
            'status_code': status.HTTP_200_OK,
            'msg': 'Success',
            'result': {
                'total': 13, 'current': 1, 'size': 50, 'pages': 1,
                'items':
                    [
                        {'id': 1, 'scope': 'core:sudo', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 2, 'scope': 'core:users', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 3, 'scope': 'core:teams', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 4, 'scope': 'core:modules', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 5, 'scope': 'core:notifications', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 6, 'scope': 'core:logs', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 7, 'scope': 'core:tasks', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {'id': 8, 'scope': 'core:consumers', 'app': {'id': 1, 'name': 'core', 'enabled': True}},
                        {"id": 9, "scope": "core:permissions", "app": {"id": 1, "name": "core", "enabled": True}},
                        {"id": 10, "scope": "core:guardian", "app": {"id": 1, "name": "core", "enabled": True}},
                        {"id": 11, "scope": "core:jobs", "app": {"id": 1, "name": "core", "enabled": True}},
                        {"id": 12, "scope": "core:variables", "app": {"id": 1, "name": "core", "enabled": True}},
                        {"id": 13, "scope": "dummy:dummy", "app": {"id": 3, "name": "dummy", "enabled": True}}
                    ]
            },
            'status': True
        }
    ),
]

negative_get_permissions_dataset = []

positive_get_granted_permissions_dataset = [
    (
        {
            "user_id": 1
        },
        {
            'status_code': status.HTTP_200_OK,
            'msg': 'Success',
            'result': [
                {
                    'id': 1,
                    'permission': {
                        'id': 1,
                        'scope': 'core:sudo',
                        'app': {
                            'id': 1,
                            'name': 'core',
                            'enabled': True
                        }
                    },
                    'user': {
                        'id': 1,
                        'username': 'admin',
                        'position': None
                    },
                    'team': None
                }
            ],
            'status': True
        }
    ),
    (
        {
            "team_id": 1
        },
        {
            'status_code': status.HTTP_200_OK,
            'msg': 'Success',
            'result': [
                {
                    'id': 2,
                    'permission': {
                        'id': 1, 'scope': 'core:sudo', 'app': {'id': 1, 'name': 'core', 'enabled': True}
                    },
                    'user': None,
                    'team': {'id': 1, 'name': 'Superusers'},
                }
            ],
            'status': True
        }
    )
]

negative_get_granted_permissions_dataset = [
    (
        {
            "user_id": 9999
        },
        {
            "msg": "NotFound",
            "result": "User not found",
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND
        }
    ),
    (
        # wrong parameter name
        {
            "id": 1234
        },
        {
            "status_code": 400,
            "msg": "MISError",
            "result": "Use only one filter",
            "status": False
        }
    ),
    (
        {
            "team_id": 9999
        },
        {
            "msg": "NotFound",
            "result": "Team not found",
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND
        }
    )
]

positive_edit_granted_permissions_dataset = [
    (
        {
            "user_id": 1,
        },
        [
            {
                "permission_id": 11,
                "granted": True
            }
        ],
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {}
        }
    ),
(
        {
            "team_id": 1,
        },
        [
            {
                "permission_id": 11,
                "granted": True
            }
        ],
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {}
        }
    )
]

negative_edit_granted_permissions_dataset = [
    (
        # Not exist team
        {
            "user_id": 9999,

        },
        [
            {
                "permission_id": 1,
                "granted": True
            }
        ],
        {
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND,
            "msg": "NotFound",
            "result": "User not found"
        }
    ),(
        {
            "user_id": 1,
        },
        [
            {
                "permission_id": 0,
                "granted": True
            }
        ],
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {}
        }
    ),(
        # Not exist team
        {
            "team_id": 9999,

        },
        [
            {
                "permission_id": 1,
                "granted": True
            }
        ],
        {
            "status": False,
            "status_code": status.HTTP_404_NOT_FOUND,
            "msg": "NotFound",
            "result": "Team not found"
        }
    ),(
        {
            "team_id": 1,
        },
        [
            {
                "permission_id": 0,
                "granted": True
            }
        ],
        {
            "status": True,
            "status_code": status.HTTP_200_OK,
            "msg": "Success",
            "result": {}
        }
    )
]

get_permissions_dataset = positive_get_permissions_dataset + negative_get_permissions_dataset
get_granted_permissions_dataset = positive_get_granted_permissions_dataset + negative_get_granted_permissions_dataset
edit_granted_permissions_dataset = positive_edit_granted_permissions_dataset + negative_edit_granted_permissions_dataset
