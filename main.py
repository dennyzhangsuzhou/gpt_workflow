from gpt import agent_run, sub_agent_name
from botforge import bot_forge
import time
from answer_processor import post_run
from mapping_processor import MappingProcessor
from loguru import logger

if __name__ == "__main__":
    agent_run()

    mapping_processor = MappingProcessor()
    total_time_costed = 0
    total_mapping_length = mapping_processor.get_mapping_length()
    for index in range(9):
        time.sleep(5)
        mapping_str = mapping_processor.get_mapping_str(index)
        start_time = time.time()
        answer = bot_forge.agent_invoke(sub_agent_name, sub_agent_name, mapping_str)
        elapsed_time = time.time() - start_time
        total_time_costed += elapsed_time
        if answer_data := post_run(answer):
            mapping_processor.update_test_cases(index, answer_data)
            logger.info(f"已处理第{index+1}行, 耗时: {elapsed_time:.2f} 秒")
        else:
            logger.warning(f"无法解析第{index+1}行模型返回的答案'{answer}'")
    mapping_processor.save_cases()
    logger.info(f"完成{total_mapping_length}行, 总耗时: {total_time_costed:.2f} 秒")
