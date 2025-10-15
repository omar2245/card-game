CARDS_DATABASE = {
    "ACT-US-02": {
        "id": 8,
        "name": "美日韓聯合軍演",
        "card_number": "ACT-US-02",
        "card_type": "ACTION",
        "country": "US",
        "rp_point": 3,
        
        # 骰子設定
        "requires_dice_roll": True,
        "dice_sides": 10,  # 10面骰
        "usage_frequency": "每回合",
        
        # 卡片描述
        "description": "「自由刀刃」(Freedom Edge)系列演習由美國、日本與南韓三國國防部長於2024年6月新加坡香格里拉對話期間首次宣布...",
        
        "short_description": "美日韓三國同意同步使用聯合軍演行動始生效",
        
        # 骰子效果對照表
        "dice_effects": {
            "0": {
                "result": "演習整合失敗，美日韓同盟信譽受挫",
                "ip_change": -1
            },
            "1-4": {
                "result": "演習成效普通，維持現狀",
                "ip_change": 0
            },
            "5-7": {
                "result": "演習成功，美日韓聯戰機制強化",
                "ip_change": 1
            },
            "8-9": {
                "result": "演習成功，美日韓同盟有效提升",
                "ip_change": 2
            }
        },
        
        "image_url": "game_cards_zh/ACT-US-02.png"
    }
}

def get_card_by_number(card_number):
    """根據卡號取得卡片資料"""
    return CARDS_DATABASE.get(card_number)

def get_dice_effect(card_number, dice_result):
    """根據骰子結果取得效果"""
    card = get_card_by_number(card_number)
    if not card or not card.get('requires_dice_roll'):
        return None
    
    effects = card.get('dice_effects', {})
    
    # 找出對應的效果範圍
    for range_key, effect in effects.items():
        if '-' in range_key:
            # 範圍格式：例如 "1-4"
            start, end = map(int, range_key.split('-'))
            if start <= dice_result <= end:
                return effect
        else:
            # 單一數字：例如 "0"
            if dice_result == int(range_key):
                return effect
    
    return None