from logging import getLogger, basicConfig, DEBUG

basicConfig(
    filename="logger.log", level=DEBUG,
    format="{asctime} | {module:<12} | {lineno:<4} | "
           "{process:<6} | {threadName:<15} | {levelname:<5} | {message}",
    style='{'
)
logger = getLogger(__name__)