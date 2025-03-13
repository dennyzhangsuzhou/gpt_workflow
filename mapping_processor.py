import pandas as pd
from loguru import logger


class MappingProcessor:
    def __init__(self):
        self.mapping_df = pd.DataFrame()
        try:
            self.mapping_df = pd.read_excel("mapping.xlsx")
        except FileNotFoundError as e:
            logger.error(f"找不到映射文件: {e}")
        except pd.errors.EmptyDataError as e:
            logger.error(f"Excel文件为空: {e}")
        except pd.errors.ParserError as e:
            logger.error(f"解析Excel文件时出错: {e}")
        except PermissionError as e:
            logger.error(f"没有权限读取文件: {e}")
        self.mapping_df["input"] = ""
        self.mapping_df["output"] = ""
        self.mapping_df["answer"] = ""

    def get_mapping_length(self):
        return len(self.mapping_df)

    def get_mapping_str(self, index):
        return f"input: {self.mapping_df.iloc[index]['msf_input']}\noutput: {self.mapping_df.iloc[index]['msf_output']}\nsignal_mapping: {self.mapping_df.iloc[index]['signal_mapping']}"  # pylint: disable=line-too-long

    def save_cases(self):
        self.mapping_df.to_excel("./data/mapping_with_cases.xlsx", index=False)
        return

    def update_test_cases(self, index, processed_answer: dict):
        #logger.info(processed_answer)
        self.mapping_df.at[index, "answer"] = processed_answer
        if isinstance(processed_answer, dict):
            self.mapping_df.at[index, "output"] = processed_answer.get("msf_output", "")
            self.mapping_df.at[index, "input"] = processed_answer.get("msf_input", "")
        return
