"""Validate and adapt supplied content without modifying source files."""
from __future__ import annotations
import json, re, sys
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
LETTERS = 'ABCD'
DIFFICULTY = {'easy': 1, 'medium': 2, 'hard': 3}

def require(ok, message):
    if not ok: raise ValueError(message)

def nonempty(value, location):
    require(isinstance(value,str) and bool(value.strip()), f'{location}: 需要非空文本')
    return value.strip()

def https_url(value, location):
    url = nonempty(value, location)
    parsed = urlparse(url)
    require(parsed.scheme == 'https' and bool(parsed.netloc), f'{location}: 需要 HTTPS 链接')
    return url

def read_rows(name):
    rows, ids = [], set()
    path = DATA / f'{name}.jsonl'
    for number,line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(),1):
        if not line.strip(): continue
        location=f'{path.name}:{number}'
        try: row=json.loads(line)
        except json.JSONDecodeError as exc: raise ValueError(f'{location}: JSON 格式错误：{exc.msg}') from exc
        require(isinstance(row,dict),f'{location}: 需要 JSON 对象')
        item_id=nonempty(row.get('id'),f'{location}.id')
        require(item_id not in ids,f'{location}: 重复 ID {item_id}')
        ids.add(item_id); rows.append(row)
    return rows

def get_topic_map(cards):
    path=DATA/'knowledge-map.json'
    if not path.exists(): return {}
    info=json.loads(path.read_text(encoding='utf-8-sig'))
    topics={}
    for category in info.get('categories',[]):
        title=nonempty(category.get('name'),'knowledge-map.category.name')
        for card_id in category.get('card_ids',[]):
            require(card_id not in topics,f'知识地图重复归类：{card_id}')
            topics[card_id]=title
    require(set(topics)<={x['id'] for x in cards},'知识地图引用了不存在的词卡')
    return topics

def normalize_cards(rows,topics):
    result,terms=[],set()
    for row in rows:
        loc=f"词卡 {row['id']}"; term=nonempty(row.get('word'),f'{loc}.word')
        require(term not in terms,f'词面重复：{term}');terms.add(term)
        require(row.get('category') in ('成语','实词'),f'{loc}.category 无效')
        require(row.get('difficulty') in DIFFICULTY,f'{loc}.difficulty 无效')
        collocations=row.get('collocations'); confusing=row.get('confusing_words');tags=row.get('tags')
        require(isinstance(collocations,list) and all(isinstance(x,str) for x in collocations),f'{loc}.collocations 无效')
        require(isinstance(confusing,list),f'{loc}.confusing_words 无效')
        require(isinstance(tags,list) and all(isinstance(x,str) for x in tags),f'{loc}.tags 无效')
        distinctions=[]
        for item in confusing:
            require(isinstance(item,dict),f'{loc}.confusing_words 需要对象')
            distinctions.append(nonempty(item.get('word'),f'{loc}.confusing_words.word')+'：'+nonempty(item.get('difference'),f'{loc}.confusing_words.difference'))
        result.append({'id':row['id'],'term':term,'kind':'idiom' if row['category']=='成语' else 'word',
            'definition':nonempty(row.get('definition'),f'{loc}.definition'),
            'usage':nonempty(row.get('context'),f'{loc}.context'),
            'collocations':collocations,'distinction':'\n'.join(distinctions),
            'example':nonempty(row.get('example'),f'{loc}.example'),
            'misuse_reason':nonempty(row.get('misuse'),f'{loc}.misuse'),
            'difficulty':DIFFICULTY[row['difficulty']],'tags':tags,'topic':topics.get(row['id'],'其他'),
            'source':{'title':'汉典词条或检索','url':https_url(row.get('source_url'),f'{loc}.source_url'),'locator':term}})
    return result

def normalize_comparisons(rows,cards):
    result=[]; by_term={x['term']:x for x in cards};missing=0;pairs=set()
    for row in rows:
        loc=f"辨析 {row['id']}";words=row.get('words')
        require(isinstance(words,list) and len(words)>=2 and all(isinstance(x,str) and x.strip() for x in words),f'{loc}.words 无效')
        require(len(set(words))==len(words),f'{loc}.words 有重复')
        key=tuple(sorted(words));require(key not in pairs,f'辨析对重复：{words}');pairs.add(key)
        if any(word not in by_term for word in words):missing+=1
        examples=row.get('examples');require(isinstance(examples,list) and len(examples)>=len(words),f'{loc}.examples 不足')
        linked=by_term.get(words[0]);url=linked['source']['url'] if linked else 'https://www.zdic.net/search?keyword='+quote(words[0])
        result.append({'id':row['id'],'terms':words,
            'shared':nonempty(row.get('similarity'),f'{loc}.similarity'),
            'difference':nonempty(row.get('key_difference'),f'{loc}.key_difference')+'\n'+nonempty(row.get('usage_difference'),f'{loc}.usage_difference'),
            'examples':[{'term':words[i],'sentence':nonempty(examples[i],f'{loc}.examples[{i}]')} for i in range(len(words))],
            'source':{'title':'汉典词义查询','url':url,'locator':words[0]}})
    return result,missing

def normalize_questions(rows,cards):
    result=[];by_id={x['id']:x for x in cards};stems=set();distribution=Counter()
    for number,row in enumerate(rows):
        loc=f"题目 {row['id']}";stem=nonempty(row.get('question'),f'{loc}.question')
        require(stem not in stems,f'题干重复：{row["id"]}');stems.add(stem)
        options=row.get('options');require(isinstance(options,dict) and set(options)==set(LETTERS),f'{loc}.options 需要 A、B、C、D')
        choices=[nonempty(options[letter],f'{loc}.options.{letter}') for letter in LETTERS]
        require(len(set(choices))==4,f'{loc}.options 有重复')
        original_answer=row.get('answer');require(original_answer in LETTERS,f'{loc}.answer 无效')
        analysis=nonempty(row.get('analysis'),f'{loc}.analysis')
        for letter in LETTERS:require(f'{letter}项' in analysis,f'{loc}.analysis 缺少 {letter} 项解析')
        endings=re.findall(r'本题选([A-D])',analysis)
        require(endings and endings[-1]==original_answer,f'{loc}.analysis 与答案不一致')
        refs=row.get('related_card_ids');require(isinstance(refs,list),f'{loc}.related_card_ids 无效')
        for ref in refs:require(ref in by_id,f'{loc} 引用不存在的词卡 {ref}')
        target=number%4;old_answer=LETTERS.index(original_answer)
        old_order=[index for index in range(4) if index!=old_answer];old_order.insert(target,old_answer)
        prefix=analysis.rsplit('本题选',1)[0]
        matches=list(re.finditer(r'([A-D])项',prefix))
        require(len(matches)==4,f'{loc}.analysis 选项解析分段失败')
        old_explanations={}
        for index,match in enumerate(matches):
            end=matches[index+1].start() if index+1<len(matches) else len(prefix)
            old_explanations[match.group(1)]=prefix[match.end():end].strip('，, ；;。').removesuffix('故').rstrip('。；; ')
        explanations=[old_explanations[LETTERS[old]] for old in old_order]
        distribution[LETTERS[target]]+=1
        result.append({'id':row['id'],'stem':stem,'choices':[choices[i] for i in old_order],
            'answer':target,'explanation':'考查点：'+nonempty(row.get('knowledge_point'),f'{loc}.knowledge_point'),
            'choice_explanations':explanations,
            'tested_terms':[by_id[ref]['term'] for ref in refs],
            'knowledge_point':nonempty(row.get('knowledge_point'),f'{loc}.knowledge_point')})
    return result,distribution

def prepare():
    raw={kind:read_rows(kind) for kind in ('cards','comparisons','questions')}
    topics=get_topic_map(raw['cards']);cards=normalize_cards(raw['cards'],topics)
    comparisons,unlinked=normalize_comparisons(raw['comparisons'],cards)
    questions,distribution=normalize_questions(raw['questions'],cards)
    summary={'cards':len(cards),'comparisons':len(comparisons),'questions':len(questions),
        'comparison_unlinked':unlinked,'question_without_cards':sum(not x['tested_terms'] for x in questions),
        'answer_distribution':dict(distribution),'topics':len(set(x['topic'] for x in cards))}
    return {'cards':cards,'comparisons':comparisons,'questions':questions},summary

def main():
    try:
        _,summary=prepare();print('内容结构校验通过：'+json.dumps(summary,ensure_ascii=False))
        print('提示：结构校验不证明释义和答案的事实准确性，请保留人工审稿记录。')
        return 0
    except (ValueError,OSError,json.JSONDecodeError) as exc:
        print(f'内容校验失败：{exc}',file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())

