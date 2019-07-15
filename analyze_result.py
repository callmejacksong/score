import json

import numpy as np
from functools import reduce


def classify_size(w, h):
    area = w*h
    if area > 480*360:
        return 2
    elif area >= 200*150:
        return 1
    else:
        return 0


def detail_score(detail, max_value):
    zerofill_detail = detail
    # while len(zerofill_detail) < 5:
    #     zerofill_detail.append(0)
    np_detail = np.array(zerofill_detail, np.longdouble)
    np_max_value_detail = np.array(
        [max_value for x in zerofill_detail], dtype=np.longdouble)
    np_factor = np.linspace(1, 100, len(zerofill_detail), dtype=np.longdouble)
    score = np.divide(np.sum(np.divide(np_detail, np_factor)),
                      np.sum(np.divide(np_max_value_detail, np_factor)))
    return np.longdouble(1) if score >= 1 else score


def analyze(keyword, gif_list, meta):
    count = len(gif_list)
    if count > 0:
        fenci_list=[]
        try:
            fenci_list = gif_list[0].get("fenciWords")
        except:
            fenci_list = json.loads(gif_list[0].get("fenciWords"))
            pass
        fenci_list.append(keyword)

        np_count = np.longdouble(count)
        count_score = np.divide(np_count, np.longdouble(100))
        anim_count = len(
            list(filter(lambda x: int(x['is_animated']) == 1, gif_list)))
        anim_ratio = np.divide(np.longdouble(anim_count), np.longdouble(
            count)) if count != 0 else np.longdouble(0)
        anim_detail = [x['is_animated'] for x in gif_list]
        anim_detail_score = detail_score(anim_detail, 1)
        size_detail = [classify_size(x['width'], x['height'])
                       for x in gif_list]
        size_detail_score = detail_score(size_detail, 2)
        size_adequate_count = sum([1 if x > 0 else 0 for x in size_detail])
        size_adequate_ratio = np.divide(
            np.longdouble(size_adequate_count), np_count)
        match_detail = [1 if sum(list(map(lambda i:1 if i.lower() in x['text'] else 0,fenci_list)))>0
                        else 0 for x in gif_list]
        match_count = reduce(
            lambda x, y: x+y, match_detail)
        match_ratio = np.divide(np.longdouble(match_count), np_count)

        match_detail_score = detail_score(match_detail, 1)
        if meta:
            meta_data_score = np.divide(np.longdouble(
                meta.get('isCore',0)*50+meta.get('maintain',0)*10+meta.get('weight',1)), 70)
        else:
            meta=""
            meta_data_score=np.longdouble(0)
        if meta_data_score > 1:
            meta_data_score = np.longdouble(1)

        quantity_score = count_score.astype(float)
        quality_score = np.multiply(np.multiply(
            anim_ratio, size_adequate_ratio), match_ratio).astype(float)
        distribution_score = np.multiply(np.multiply(
            anim_detail_score, size_detail_score), match_detail_score).astype(float)
        result_dict =  {
            'attr': {
                'quantity': {
                    'count': {
                        'value': count,
                        'score': count_score.astype(float),
                        'desc': '结果数量，大于100显示为100'
                    },
                    'score': quantity_score.astype(float),
                    'desc': '数量得分'
                },
                'quality': {
                    'anim_ratio': {
                        'score': anim_ratio.astype(float),
                        'desc': '动图占比'
                    },
                    'size_adequate_ratio': {
                        'score': size_adequate_ratio.astype(float),
                        'desc': '清晰度合适的图片占比'
                    },
                    'match_ratio': {
                        'score': match_ratio.astype(float),
                        'desc': 'text含有关键词的图片占比'
                    },
                    'score': quality_score.astype(float),
                    'desc': '质量得分'
                },
                'distribution': {
                    'anim_detail': {
                        'value': anim_detail,
                        'score': anim_detail_score.astype(float),
                        'desc': '动图分布'
                    },
                    'size_detail': {
                        'value': size_detail,
                        'score': size_detail_score.astype(float),
                        'desc': '清晰度分布'
                    },
                    'match_detail': {
                        'value': match_detail,
                        'score': match_detail_score.astype(float),
                        'desc': 'text含有关键词的图片分布'
                    },
                    'score': distribution_score.astype(float),
                    'desc': '分布情况得分'
                },
                'meta_data': {
                    'value': meta,
                    'score': meta_data_score.astype(float),
                    'desc': '关于这个词的其他信息'
                }
            },
            'score': {
                'value': np.sum(np.multiply(
                    [quality_score,
                     quantity_score,
                     distribution_score,
                     meta_data_score],
                    [30,
                     30,
                     20,
                     20])).astype(float),
                'desc': '总分数，几个分项分数乘以[30,30,20,20]的权重求和 '
            }
        }
        result_dict["fenci_result"]=fenci_list
        return result_dict
    else:
        return {}
