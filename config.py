class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'db:job_delete_inactive',
            'args': (),
            'trigger': 'interval',
            'minutes': 30
        }
    ]

    SCHEDULER_API_ENABLED = True

    SECRET_KEY = 'super_secret_key_for_project_00023'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
