import logging, os, zipfile
from datetime import datetime
from utils.config_parser import Config
from logging.handlers import BaseRotatingHandler
from logging.handlers import TimedRotatingFileHandler
from logging import Logger as LoggingLogger


# Creating custom rotating funtion
def custom_rotate(self, source: str, dest: str):
    if callable(self.rotator):
        self.rotator(source, dest)

# Overwriting default rotate funtion
BaseRotatingHandler.rotate = custom_rotate


class DateFolderRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        self._file_name_template = args[0]
        base_file_name = self.create_path()

        super().__init__(base_file_name, **kwargs)


    def doRollover(self) -> None:
        self.baseFilename = self.create_path()

        return super().doRollover()


    def create_path(self):
        base_file_name = datetime.now().strftime(self._file_name_template)
        base_path_list = base_file_name.split('/')
        dir_path = '/'.join(base_path_list[:-1])
        
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        return base_file_name


class Logger():
    _DEFAULT_LOG_NAME = 'log'
    _GLOBAL_LOG_NAME = 'full_log'
    _ROLLOVER_SUFFIX = '%Y-%m-%d'

    def get_logger(self, name: str, file_name: str='log', console: bool=True) -> LoggingLogger:
        self._console = console
        self._file_name = file_name
        self._logger = logging.getLogger(name)

        if not self._logger.hasHandlers():
            self._init_logger()

        return self._logger


    def _get_log_path(self, file_name: str) -> str:
        dir_path = Config().get('logger', 'dir')
        log_path = f"{dir_path}/{self._ROLLOVER_SUFFIX}/{file_name}.log"

        return log_path


    def _init_logger(self):
        self._log_format = logging.Formatter(Config().get('Logger', 'format'))

        self._init_console_logger()
        self._init_file_logger(file_name=self._file_name)
        self._init_file_logger(file_name=self._GLOBAL_LOG_NAME)

        self._logger.setLevel(Config().get('Logger', 'level'))


    def _init_console_logger(self):
        if self._console:
            s_handler = logging.StreamHandler()
            s_handler.setFormatter(self._log_format)
            self._logger.addHandler(s_handler)


    def _init_file_logger(self, file_name: str=""):
        log_path = self._get_log_path(file_name)
        r_handler = DateFolderRotatingFileHandler(log_path, when='midnight', interval=1)
        r_handler.setFormatter(self._log_format)
        self._logger.addHandler(r_handler)
        
    def init_no_rollover_file_logger(self):
        log_path = self.get_log_path()
        separate_log_without_rollover = Config().get('Logger', 'separate_log_without_rollover')
        
        # Separate log file with all logs and no rollovers
        if separate_log_without_rollover:
            t_log_path = f'{log_path}.full'
            full_handler = logging.FileHandler(t_log_path)
            full_handler.setFormatter(self._log_format)
            self._logger.addHandler(full_handler)
            
    def init_excluded_log_file_logger(self):
        log_path = self.get_log_path()
        
        # True if log should be excluded from file (separate file)
        if not self._exclude_log:
            t_log_path = f'{log_path}.excluded'
            exclude_handler = TimedRotatingFileHandler(t_log_path, when='midnight', interval=1, encoding="utf-8")
            exclude_handler.suffix = self._rollover_suffix
            exclude_handler.setFormatter(self._log_format)
            self._logger.addHandler(exclude_handler)
            
    def archive_log(self, folder_name: str) -> str:
        self.delete_old_archives()
        
        dir_path = Config().get('logger', 'dir')
        folder_path = f'{dir_path}/{folder_name}'
        archive_name = f'{dir_path}/{folder_name}_{datetime.now().strftime("%H-%M-%S")}.zip'

        archive = zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED)

        has_items = False
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                archive.write(file_path)
                has_items = True
                
        if not has_items:
            raise FileNotFoundError(f'Folder {folder_path} was not found')

        archive.close()
        
        return archive_name
    
    def delete_old_archives(self):
        dir_path = Config().get('logger', 'dir')
        
        for filename in os.listdir(dir_path):
            if filename.endswith(".zip"):
                file_path = os.path.join(dir_path, filename)
                os.remove(file_path)
