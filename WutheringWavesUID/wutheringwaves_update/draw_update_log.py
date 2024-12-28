import subprocess
from pathlib import Path
from typing import Union, List

from PIL import Image, ImageDraw

from gsuid_core.logger import logger
from gsuid_core.utils.error_reply import UPDATE_HINT
from gsuid_core.utils.image.convert import convert_img
from ..utils.fonts.waves_fonts import waves_font_origin
from ..utils.image import get_waves_bg

R_PATH = Path(__file__).parent
TEXT_PATH = R_PATH / 'texture2d'

gs_font_30 = waves_font_origin(30)
black_color = (24, 24, 24)

log_config = {
    'key': '✨🐛🎨⚡🍱♻️',
    'num': 18,
}

log_map = {'✨': 'feat', '🐛': 'bug', '🍱': 'bento', '⚡️': 'zap', '🎨': 'art'}


async def draw_update_log_img(
    level: int = 0,
    repo_path: Union[str, Path, None] = None,
) -> Union[bytes, str]:
    log_list = await update_from_git(repo_path, log_config)
    if len(log_list) == 0:
        return UPDATE_HINT

    log_title = Image.open(TEXT_PATH / 'log_title.png')

    img = get_waves_bg(950, 20 + 475 + 80 * len(log_list))
    img.paste(log_title, (0, 0), log_title)
    img_draw = ImageDraw.Draw(img)
    img_draw.text(
        (475, 432), 'WWUID 更新记录', black_color, gs_font_30, 'mm'
    )

    for index, log in enumerate(log_list):
        for key in log_map:
            if log.startswith(key):
                log_img = Image.open(TEXT_PATH / f'{log_map[key]}.png')
                break
        else:
            log_img = Image.open(TEXT_PATH / 'other.png')

        log_img_text = ImageDraw.Draw(log_img)
        if ')' in log:
            log = log.split(')')[0] + ')'
        log = log.replace('`', '')
        log_img_text.text((120, 40), log[1:], black_color, gs_font_30, 'lm')

        img.paste(log_img, (0, 475 + 80 * index), log_img)

    img = await convert_img(img)
    return img


async def update_from_git(
    repo_path: Union[str, Path, None] = None,
    log_config: dict = {
        'key': '✨🐛',
        'num': 7,
    },
    is_update: bool = True,
) -> List[str]:
    if repo_path is None:
        repo_path = Path(__file__).parents[2]
    try:
        # 获取提交记录
        process = subprocess.run(
            ['git', 'log', '--pretty=format:%s', '-40'],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            check=True
        )

        # 处理提交信息
        commits = process.stdout.split('\n')
        log_list = []

        # 筛选包含关键字的提交信息
        for commit in commits:
            if commit:  # 确保不是空字符串
                for key in log_config['key']:
                    if key in commit:
                        log_list.append(commit)
                        if len(log_list) >= log_config['num']:
                            return log_list

        return log_list

    except subprocess.CalledProcessError as e:
        logger.warning(f'Git log failed: {e.stderr}')
        return []
    except Exception as e:
        logger.warning(f'Get logs failed: {e}')
        return []
