import json

BUILDING_TAB = [{
    "buildingid": "471",
    "building": "16栋A区"
},
    {
    "buildingid": "472",
    "building": "16栋B区"
},
    {
    "buildingid": "451",
    "building": "17栋"
},
    {
    "buildingid": "141",
    "building": "弘毅轩1栋A区"
},
    {
    "buildingid": "148",
    "building": "弘毅轩1栋B区"
},
    {
    "buildingid": "197",
    "building": "弘毅轩2栋A区1-6楼"
},
    {
    "buildingid": "201",
    "building": "弘毅轩2栋B区"
},
    {
    "buildingid": "205",
    "building": "弘毅轩2栋C区"
},
    {
    "buildingid": "206",
    "building": "弘毅轩2栋D区"
},
    {
    "buildingid": "155",
    "building": "弘毅轩3栋A区"
},
    {
    "buildingid": "183",
    "building": "弘毅轩3栋B区"
},
    {
    "buildingid": "162",
    "building": "弘毅轩4栋A区"
},
    {
    "buildingid": "169",
    "building": "弘毅轩4栋B区"
},
    {
    "buildingid": "450",
    "building": "留学生公寓"
},
    {
    "buildingid": "176",
    "building": "敏行轩1栋A区"
},
    {
    "buildingid": "184",
    "building": "敏行轩1栋B区"
},
    {
    "buildingid": "513",
    "building": "敏行轩2栋A区"
},
    {
    "buildingid": "520",
    "building": "敏行轩2栋B区"
},
    {
    "buildingid": "85",
    "building": "行健轩1栋A区"
},
    {
    "buildingid": "92",
    "building": "行健轩1栋B区"
},
    {
    "buildingid": "99",
    "building": "行健轩2栋A区"
},
    {
    "buildingid": "106",
    "building": "行健轩2栋B区"
},
    {
    "buildingid": "113",
    "building": "行健轩3栋A区"
},
    {
    "buildingid": "120",
    "building": "行健轩3栋B区"
},
    {
    "buildingid": "127",
    "building": "行健轩4栋A区"
},
    {
    "buildingid": "134",
    "building": "行健轩4栋B区"
},
    {
    "buildingid": "57",
    "building": "行健轩5栋A区"
},
    {
    "buildingid": "64",
    "building": "行健轩5栋B区"
},
    {
    "buildingid": "71",
    "building": "行健轩6栋A区"
},
    {
    "buildingid": "78",
    "building": "行健轩6栋B区"
},
    {
    "buildingid": "1",
    "building": "至诚轩1栋A区"
},
    {
    "buildingid": "8",
    "building": "至诚轩1栋B区"
},
    {
    "buildingid": "15",
    "building": "至诚轩2栋A区"
},
    {
    "buildingid": "22",
    "building": "至诚轩2栋B区"
},
    {
    "buildingid": "29",
    "building": "至诚轩3栋A区"
},
    {
    "buildingid": "36",
    "building": "至诚轩3栋B区"
},
    {
    "buildingid": "43",
    "building": "至诚轩4栋A区"
},
    {
    "buildingid": "50",
    "building": "至诚轩4栋B区"
}]

building_names = dict()

for b in BUILDING_TAB:
    building_names[b['building']] = b['buildingid']

HELP = """电费查询&预警插件
可以手动查询电费，低电量余额时自动提醒（需要管理员设置）

用法：
    /查电费 <命令/楼栋名> [宿舍号]

例：
    /查电费 17栋 406
    /查电费 16栋A区 A201

可用命令：
    楼栋列表 - 列出所有可使用的楼栋名
    自动预警配置查询 - N/A
    重载 - 重载插件配置文件（管理员）
    推送 - 手动推送所有预警信息（管理员）"""

def load_binding_data(data_path: str) -> list[dict[str, str]]:
    try:
        with open(data_path, 'r', encoding='utf-8') as fp:
            return json.load(fp)
    except Exception:
        return None
    
def get_bid_by_bname(name: str) -> str:
    return building_names.get(name, '')