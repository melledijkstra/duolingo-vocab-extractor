import json

import requests as req


def get_lexem_data(lexem_id=None, from_language_id='en'):
    def __get_phrases(alternative_forms):
        phrases = []
        for form in alternative_forms:
            phrases.append({
                'text': form['text'],
                'tts': form['tts'],
                'translation_text': form['translation_text'],
            })
        return phrases

    data = req.get('https://www.duolingo.com/api/1/dictionary_page', {
        'lexeme_id': lexem_id,
        'from_language_id': from_language_id,
    }).json()

    return {
        'word': data['word'],
        'lexem_id': data['lexeme_id'],
        'image': data['lexeme_image'],
        'tts': data['tts'],
        'phrases': __get_phrases(data['alternative_forms']),
    }


def get_translations(term, from_language_id='en'):
    data = req.get('https://duolingo-lexicon-prod.duolingo.com/api/1/search', {
        'query': term,
        'exactness': 1,
        'languageId': 'zh',
        'uiLanguageId': from_language_id
    }).json()

    for result in data['results']:
        if result['exactMatch'] is True:  # we only allow exact matches
            return result['lexemeId'], result['translations'][from_language_id]
    return '', []  # no exact match is found


def get_everything(term, from_language_id='en'):
    lexem_id, translations = get_translations(term, from_language_id)
    try:
        lexem_data = get_lexem_data(lexem_id)
    except:
        lexem_data = {}
    info = {
        'lexem_id': lexem_id,
        'term': term,
        'translations': translations,
        **lexem_data,
    }
    return info


if __name__ == '__main__':
    print(get_everything('四'))
    exit()
    # here the dictionary gets loaded that was extracted previously
    with open('duolingo-chinese-dictionary.json', 'r') as fp:
        dictionary = json.load(fp)  # type: dict

    lexicon = {}

    i = 0
    n = len(dictionary)
    for exercise, terms in dictionary.items():
        print(f'{i / n * 100:.0f}%\t| Exercise: {exercise} - Terms: {len(terms)} terms\n\t', end='')
        term_datas = []
        for term in terms:
            print(f'{term} • ', end='')
            term_datas.append(get_everything(term))
        lexicon[exercise] = term_datas
        print()
        i += 1

    with open('duolingo-chinese-lexicon.json', 'w') as fp:
        json.dump(lexicon, fp)
