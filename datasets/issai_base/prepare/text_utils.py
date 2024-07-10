import re 
from num2words import num2words
from chars_maps import cyrillic_mapping, num_to_kazakh_ordinal, kazakh_chars
from kaz_numerals import KazNumerals


kaznumerals = KazNumerals()

months_pattern_f = re.compile(r'^(3[01]|[12][0-9]|[1-9])\s(қаңтар|ақпан|наурыз|сәуір|мамыр|маусым|шілде|тамыз|қыркүйек|қазан|қараша|желтоқсан)$')
months_pattern = re.compile(r'\b(3[01]|[12][0-9]|[1-9])\s(қаңтар|ақпан|наурыз|сәуір|мамыр|маусым|шілде|тамыз|қыркүйек|қазан|қараша|желтоқсан)')
hundreds_pattern_range = re.compile(r'\b\d{3}\b')
kazakh_letters = "[а-яА-ЯӘәҒғҚқҢңӨөҰұҮүҺһІі]+"
words_with_digits = re.compile(kazakh_letters+r"\d+|\d+"+kazakh_letters)
digits_with_ordinal_suffix = re.compile(r"\d+"+"-[{}]+".format(kaznumerals.ordinal))
digits_with_group_suffix = re.compile(r"\d+"+"-[{}]+".format(kaznumerals.group))


def process_wrong_chars(text, trash_symbols_pattern="\n|noise|ʨ|ɕ|»|–|«|—|̆|“|”|…|−|－|●"):
    processed_text = re.sub('–|—|−|－', '-', text)
    processed_text = re.sub(trash_symbols_pattern, '', text)
    return re.sub(r"\s+", ' ', processed_text).strip()


def _find_digit_space_months(text):
    # Find all matches of the pattern in the text
    return months_pattern.findall(text)

def _find_hundreds_digits(text):
    return hundreds_pattern_range.findall(text)

def _find_words_with_digits(text):
    return words_with_digits.findall(text)

def _find_suffixed_digit(text):
    return digits_with_group_suffix.findall(text) or digits_with_ordinal_suffix.findall(text)


def _replace_m(match):
    if months_pattern_f.fullmatch(match.group()):
        d, m = match.group().split()
        d = num_to_kazakh_ordinal[int(d)]
    return '{} {}'.format(d, m)

def _replace_h(match):
    h_num = match.group()
    h_num = num2words(h_num, lang="kz")
    return h_num

def _replace_ordinal_s(match):
    digit = int(re.sub("[^0-9]", '', match.group()))
    return num_to_kazakh_ordinal[digit]

def _replace_group_s(match):
    digit, suff = match.group().split("-")
    return num2words(digit, lang="kz")+suff

def _remove_digit(match):
    text = re.sub("\d", '', match.group())
    return text

nums = re.compile("\d+")
def replace_nums(match):
    return num2words(match.group(), lang="kz")


def normalize_nums(text):
    text = text.replace("2008", "екі мың сегізінші")
    if _find_digit_space_months(text):
        text = months_pattern.sub(_replace_m, text)
    if _find_hundreds_digits(text):
        text = hundreds_pattern_range.sub(_replace_h, text)
    if _find_words_with_digits(text):
        text = words_with_digits.sub(_remove_digit, text)
    if _find_suffixed_digit(text):
        text = digits_with_ordinal_suffix.sub(_replace_ordinal_s, text)
        text = digits_with_group_suffix.sub(_replace_group_s, text)
    text = nums.sub(replace_nums, text)
    return text 

def normalize_text(text, mapping=cyrillic_mapping):
    text = process_wrong_chars(text)
    text = normalize_nums(text)
    return ''.join(mapping.get(char, char) for char in text)

def contains_non_kazakh_chars(text):
    return any(char not in kazakh_chars for char in text)