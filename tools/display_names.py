"""Explicit UI names for distinct modifiers sharing native localisation.

Keep the stable registry and its source/format/icon bindings unchanged.
"""
DISPLAY_NAMES = {
    'global_building_slots': {
        'simp_chinese': '地区最大工厂数（固定值）',
        'english': 'Max Factories in a State (Flat)',
    },
    'army_org': {
        'simp_chinese': '陆军师组织度（固定值）',
        'english': 'Division Organization (Flat)',
    },
    'experience_gain_army_factor': {
        'simp_chinese': '陆军经验增长（百分比）',
        'english': 'Army Experience Gain (Percentage)',
    },
    'experience_gain_navy_factor': {
        'simp_chinese': '海军经验增长（百分比）',
        'english': 'Navy Experience Gain (Percentage)',
    },
    'experience_gain_air_factor': {
        'simp_chinese': '空军经验增长（百分比）',
        'english': 'Air Experience Gain (Percentage)',
    },
    'max_dig_in_factor': {
        'simp_chinese': '堑壕上限（百分比）',
        'english': 'Max Entrenchment (Percentage)',
    },
    'encryption_factor': {
        'simp_chinese': '旧版加密（百分比）',
        'english': 'Legacy Encryption (Percentage)',
    },
    'decryption_factor': {
        'simp_chinese': '旧版解密（百分比）',
        'english': 'Legacy Decryption (Percentage)',
    },
    'conscription_factor': {
        'simp_chinese': '可征募人口（比例加成）',
        'english': 'Recruitable Population (Factor)',
    },
    'autonomy_manpower_share_from_subjects': {
        'simp_chinese': '宗主国对附属国的人力要求',
        'english': 'Subject Manpower Requirement (Overlord)',
    },
}


def metric_display_name(record, language='simp_chinese', fallback=None):
    return DISPLAY_NAMES.get(record['key'], {}).get(language, fallback or record['name'])
