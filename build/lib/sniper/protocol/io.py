from loguru import logger
import os
import pandas as pd
from sniper.utils import Utils
from sniper.utils.expt import ModuleExt


class FileSystem:
    def __init__(self, base_path, dir_name):
        self.__base_path = base_path

        self.__dir_name = os.path.join(base_path, dir_name)
        if not os.path.exists(self.__dir_name):
            os.mkdir(self.__dir_name)

    def to_csv(self, df, file_name, mode='w'):
        if not file_name.endswith('.csv'):
            file_name = file_name + '.csv'
        abs_path = os.path.join(self.__dir_name, file_name)
        logger.info(f'下载 {abs_path} ...')
        # print(df)
        header = True
        if mode == 'a':
            header = False
        df.to_csv(abs_path, index=False, mode=mode, header=header)

    def read_csv(self, file_name_or_code):
        file_name_or_code = str(file_name_or_code)
        files = os.listdir(self.__dir_name)
        files = [file for file in files if file.find(file_name_or_code) >= 0]
        if not Utils.is_empty(files):

            abs_path = os.path.join(self.__dir_name, files[0])

            return pd.read_csv(abs_path)
        else:
            raise ModuleExt(f'没有找到{file_name_or_code}')
