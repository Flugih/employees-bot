import logging.config
import os


class LoggerManager:
    def __init__(self):
        from infrastructure import Config # temp

        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        self.config = Config()

        log_dir = "./logs"
        os.makedirs(log_dir, exist_ok=True)

    def setup_logging(self):
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                },
                'simple': {
                    'format': '%(asctime)s - %(message)s'
                },
            },
            'handlers': {
                'file': {
                    'level': 'DEBUG',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'detailed',
                    'filename': './logs/bot.log',
                    'maxBytes': 5 * 1024 * 1024,  # 5 MB
                    'backupCount': 5,
                    'encoding': 'utf-8',
                    'mode': 'w',
                },
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',
                    'stream': 'ext://sys.stdout',
                },
            },
            'loggers': {
                '': {
                    'handlers': ['file', 'console'],
                    'level': self.config.LOG_LEVEL_ROOT,
                    'propagate': False,
                },
                'user_actions': {
                    'handlers': ['file', 'console'],
                    'level': self.config.LOG_LEVEL_USER_ACTIONS,
                    'propagate': False,
                },
                'pyrogram': {
                    'handlers': ['file'],
                    'level': self.config.LOG_LEVEL_PYROGRAM,
                    'propagate': False,
                },
            },
        }

        logging.config.dictConfig(logging_config)
