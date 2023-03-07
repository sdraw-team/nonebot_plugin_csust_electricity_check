from nonebot_plugin_apscheduler import scheduler
import nonebot
from nonebot import on_command
from nonebot.rule import Rule
from nonebot.adapters.onebot.v11.adapter import Message, MessageSegment
from nonebot.adapters.onebot.v11 import Message, MessageSegment, Bot, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
import aiohttp
import json
import re
import asyncio
from pathlib import Path

from .config import Config
from .data import load_binding_data, BUILDING_TAB, HELP, get_bid_by_bname


electricity_check = on_command(
    'eleccheck', rule=Rule(), aliases={'查电费'}, priority=5)

elec_check_config = Config.parse_obj(nonebot.get_driver().config.dict())

data_path = Path().absolute() / "data" / "eleccheck"

REQ_DATA = {"query_elec_roominfo": {"aid": "0030000000002501", "account": "251277", "room": {"roomid": "", "room": ""}, "floor": {
    "floorid": "", "floor": ""}, "area": {"area": "云塘校区", "areaname": "云塘校区"}, "building": {"buildingid": "451", "building": "17栋"}}}
API = 'http://yktwd.csust.edu.cn:8988/web/Common/Tsm.html'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50',
    'Referer': 'http://yktwd.csust.edu.cn:8988/web/common/checkEle.html?ticket=2E94FD6F19FB40558D53CC55AE4421E4&from=ehall&cometype=',
    'Content-Type': 'application/x-www-form-urlencoded'
}
RESULT_PATTERN = r'房间剩余电量([\d\.]+)'
re_result = re.compile(RESULT_PATTERN)

bindings = load_binding_data(str(data_path / 'bindings.json'))


async def reload_bindings():
    global bindings
    bindings = load_binding_data(str(data_path / 'bindings.json'))


async def batch_check():
    """批量检测低电量房间并推送到群聊
    """
    bot = nonebot.get_bot()
    if not bindings:
        return
    
    for binding_info in bindings:
        group = binding_info['group']
        rooms = binding_info['rooms']
        default_building = binding_info['building']
        result = []
        for r in rooms:
            rid = r['roomid']
            bname = r.get('building', default_building)
            bid = get_bid_by_bname(bname)
            try:
                remain = await get_electricity(building_id=bid, building_name=bname, roomid=rid)
            except Exception as e:
                print('获取信息出错：' + str(e))
            result.append({'roomid': rid, 'remain': remain, 'building': bname})
            await asyncio.sleep(0.5)

        msg = ['电量不足预警：\n']
        for res in result:
            elec = float(res['remain'])
            if elec <= 50:
                msg.append('\n{}{}剩余电量：{}'.format(
                    res['building'], res['roomid'], res['remain']))
        if len(msg) > 1:
            await bot.send_group_msg(group_id=group, message=Message(msg))

if bindings:
    scheduler.add_job(
        batch_check,
        'cron',
        hour=15,
        minute=0,
        second=0,
        id='batch_elec_check_and_push'
    )


async def get_electricity(building_id: str, building_name: str, roomid: str) -> str:
    """通过API获取电量信息

    Args:
        building_id (str): 
        building_name (str): 
        roomid (str): 

    Raises:
        IOError: 
        RuntimeError: 

    Returns:
        str: 
    """
    # 组织参数
    jsondata = REQ_DATA.copy()
    jsondata['query_elec_roominfo']['room']['roomid'] = roomid
    jsondata['query_elec_roominfo']['room']['room'] = roomid
    jsondata['query_elec_roominfo']['building']['buildingid'] = building_id
    jsondata['query_elec_roominfo']['building']['building'] = building_name
    payload = {
        "jsondata": json.dumps(jsondata),
        "funname": "synjones.onecard.query.elec.roominfo",
        "json": True
    }

    # 查询请求
    async with aiohttp.ClientSession() as session:
        async with session.post(url=API, data=payload, headers=HEADERS) as res:
            if res.status != 200:
                raise IOError('接口调用失败: Code ' + res.status)
            res_raw = await res.text()

    try:
        res_json = json.loads(res_raw)
    except json.decoder.JSONDecodeError:
        raise IOError('接口调用失败: ' + res_raw)

    if res_json['query_elec_roominfo']['retcode'] != '0':
        raise RuntimeError(
            '获取失败: ' + res_json['query_elec_roominfo']['errmsg'])

    msg = res_json['query_elec_roominfo']['errmsg'].strip()
    # 检查返回结果是否合法，并抽取电量数值
    match = re_result.match(msg)
    if not match:
        raise RuntimeError(
            '获取失败: ' + res_json['query_elec_roominfo']['errmsg'])

    elec_quantity = re_result.findall(msg)[0]
    return elec_quantity


async def building_list() -> list[str]:
    """获取所有楼栋名列表

    Returns:
        list[str]: 楼栋名列表
    """
    buildings = []
    for b in BUILDING_TAB:
        buildings.append(b['building'])
    return buildings


@electricity_check.handle()
async def elec_check_handler(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    if event.message_type != 'group':
        await matcher.finish()

    group = event.group_id
    # 白名单检查
    if str(group) not in elec_check_config.elec_check_enable:
        await matcher.finish()

    # 参数检查
    args = arg.extract_plain_text()
    if len(args) == 0:
        await matcher.finish(HELP)
    args = args.rsplit()

    if args[0] == '楼栋列表':
        buildings = await building_list()
        msg = '支持的所有楼栋名：\n' + '\n'.join(buildings)
        await matcher.finish(msg)
    if args[0] == '自动预警配置查询':
        await matcher.finish('该功能尚未开放')
    if args[0] == '重载':
        # TODO: 管理员权限检测
        await reload_bindings()
        await matcher.finish('插件配置已重载')
    if args[0] == '推送':
        # TODO: 管理员权限检测
        await batch_check()
        await matcher.finish('已推送所有预警')

    if len(args) < 2:
        await matcher.finish(HELP)

    building_name = args[0]
    roomid = args[1]
    building_id = get_bid_by_bname(building_name)
    if not building_id:
        await matcher.finish('参数错误：楼栋名不存在')

    try:
        electricity = await get_electricity(building_id=building_id,
                                            building_name=building_name,
                                            roomid=roomid)
    except Exception as e:
        await matcher.finish(str(e))

    await matcher.finish('{}{}剩余电量：{}'.format(building_name, roomid, electricity))
