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
        self.mapping_df.to_excel("mapping_with_cases.xlsx", index=False)
        return

    def update_test_cases(self, index, processed_answer: dict):
        row = self.mapping_df.iloc[index]
        # logger.info(processed_answer)
        self.mapping_df.at[index, "answer"] = processed_answer
        if (
            isinstance(processed_answer, dict)
            and "msf_input" in processed_answer
            and "msf_output" in processed_answer
        ):
            input_signals = processed_answer["msf_input"]
            output_signals = processed_answer["msf_output"]

            num_test_cases = 0
            if isinstance(input_signals, dict):
                for signal_values in input_signals.values():
                    if isinstance(signal_values, list):
                        num_test_cases = max(num_test_cases, len(signal_values))
                        break

            if num_test_cases == 0 and isinstance(output_signals, dict):
                for signal_values in output_signals.values():
                    if isinstance(signal_values, list):
                        num_test_cases = max(num_test_cases, len(signal_values))
                        break

            msf_input = str(row["msf_input"]) if not pd.isna(row["msf_input"]) else ""
            msf_output = (
                str(row["msf_output"]) if not pd.isna(row["msf_output"]) else ""
            )

            matching_input_signals = {}
            if isinstance(input_signals, dict):
                for signal_name, values in input_signals.items():
                    if signal_name in msf_input:
                        matching_input_signals[signal_name] = values
            else:
                logger.warning(f"输入信号不是字典类型，而是 {type(input_signals)}")

            matching_output_signals = {}
            if isinstance(output_signals, dict):
                for signal_name, values in output_signals.items():
                    if signal_name in msf_output:
                        matching_output_signals[signal_name] = values
            else:
                logger.warning(f"输出信号不是字典类型，而是 {type(output_signals)}")

            if not matching_input_signals and not matching_output_signals:
                logger.warning(f"第 {index} 行没有匹配的信号")

            input_signal_order = []
            if isinstance(input_signals, dict):
                for signal_name in input_signals.keys():
                    if (
                        signal_name in msf_input
                        and signal_name in matching_input_signals
                    ):
                        input_signal_order.append(signal_name)

                input_signal_order.sort(key=lambda x: msf_input.find(x))

            output_signal_order = []
            if isinstance(output_signals, dict):
                for signal_name in output_signals.keys():
                    if (
                        signal_name in msf_output
                        and signal_name in matching_output_signals
                    ):
                        output_signal_order.append(signal_name)

                output_signal_order.sort(key=lambda x: msf_output.find(x))

            input_test_groups = []
            for test_idx in range(num_test_cases):
                signal_values = []
                for signal_name in input_signal_order:
                    values = matching_input_signals[signal_name]
                    if isinstance(values, list) and test_idx < len(values):
                        signal_values.append(f"{values[test_idx]}")
                if signal_values:
                    input_test_groups.append(",".join(signal_values))

            if input_test_groups:
                self.mapping_df.at[index, "input"] = ";".join(input_test_groups)

            output_test_groups = []
            for test_idx in range(num_test_cases):
                signal_values = []
                for signal_name in output_signal_order:
                    values = matching_output_signals[signal_name]
                    if isinstance(values, list) and test_idx < len(values):
                        signal_values.append(f"{values[test_idx]}")
                if signal_values:
                    output_test_groups.append(",".join(signal_values))

            if output_test_groups:
                self.mapping_df.at[index, "output"] = ";".join(output_test_groups)
        else:
            logger.warning(
                f"答案格式与期望不符,无法更新DataFrame。答案类型: {type(processed_answer)}"
            )
        return
