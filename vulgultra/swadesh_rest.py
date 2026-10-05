"""Swadesh citation forms for the rest of the README corpus.

English and Latin are in RESERVED_TABLES only — not SOURCE_LANGS.
Latin is the process being reversed, not a daughter. Empty cells are
legal: that lect does not compete for that concept.
"""

from __future__ import annotations

IDS: tuple[str, ...] = (
    "i", "you_sg", "he", "we", "you_pl", "they", "this", "that", "here", "there",
    "who", "what", "where", "when", "how", "not", "all", "many", "some", "few",
    "other", "one", "two", "three", "four", "five", "big", "long", "wide", "thick",
    "heavy", "small", "short", "narrow", "thin", "woman", "man", "person", "child",
    "wife", "husband", "mother", "father", "animal", "fish", "bird", "dog", "louse",
    "snake", "worm", "tree", "forest", "stick", "fruit", "seed", "leaf", "root",
    "bark", "flower", "grass", "rope", "skin", "meat", "blood", "bone", "fat",
    "egg", "horn", "tail", "feather", "hair", "head", "ear", "eye", "nose", "mouth",
    "tooth", "tongue", "fingernail", "foot", "leg", "knee", "hand", "wing", "belly",
    "guts", "neck", "back", "breast", "heart", "liver", "drink", "eat", "bite",
    "suck", "spit", "vomit", "blow", "breathe", "laugh", "see", "hear", "know",
    "think", "smell", "fear", "sleep", "live", "die", "kill", "fight", "hunt",
    "hit", "cut", "split", "stab", "scratch", "dig", "swim", "fly", "walk", "come",
    "lie", "sit", "stand", "turn", "fall", "give", "hold", "squeeze", "rub", "wash",
    "wipe", "pull", "push", "throw", "tie", "sew", "count", "say", "sing", "play",
    "float", "flow", "freeze", "swell", "sun", "moon", "star", "water", "rain",
    "river", "lake", "sea", "salt", "stone", "sand", "dust", "earth", "cloud",
    "fog", "sky", "wind", "snow", "ice", "smoke", "fire", "ash", "burn", "road",
    "mountain", "red", "green", "yellow", "white", "black", "night", "day", "year",
    "warm", "cold", "full", "new", "old", "good", "bad", "rotten", "dirty",
    "straight", "round", "sharp", "dull", "smooth", "wet", "dry", "correct",
    "near", "far", "right", "left", "at", "in", "with", "and", "if", "because",
    "name", "def_art", "copula", "cat", "cat_f", "dog_f", "smile",
)


def _pack(tag: str, s: str) -> dict[str, str]:
    xs = s.split("|")
    if len(xs) != len(IDS):
        raise ValueError(f"{tag}: {len(xs)} forms, expected {len(IDS)}")
    return dict(zip(IDS, (x.strip() for x in xs)))


def _hits(tag: str, d: dict[str, str]) -> dict[str, str]:
    """Partial Swadesh: attested cells only. Missing keys → empty (no sister pad)."""
    extra = set(d) - set(IDS)
    if extra:
        raise ValueError(f"{tag}: extra keys {sorted(extra)}")
    return {i: (d.get(i) or "").strip() for i in IDS}


# Ibero-Romance
_AN = _pack("an", "yo|tu|él|nusatros|vusatros|els|iste|ixe|aquí|allí|quién|qué|án|cuan|cómo|no|tot|muitos|beluns|pocos|atro|un|dos|tres|cuatro|cinco|gran|largo|amplo|grueso|pesau|chicot|curto|estreito|fino|muller|hombre|persona|nino|muller|marido|mai|pai|animal|peix|aucel|can|piojo|sierpe|gusan|árbol|bosque|palo|fruta|simiente|fuella|raiz|corteza|flor|yerba|cuerda|piel|carne|sangre|ueso|grasa|huevo|cuerno|cola|pluma|pelo|cabeza|orella|uello|nariz|boca|diente|lengua|unya|pie|gamba|chinollo|man|ala|vientre|tripas|cuello|espalda|peito|corazón|figado|beber|minchar|morder|chupar|escupir|vomitar|bufar|respirar|reir|veyer|oír|saber|pensar|oler|temer|dormir|vivir|morir|matar|luitar|cazar|golpiar|tallar|fender|apunyalar|rascar|cavar|nadar|volar|caminar|venir|chacer|sentar|estar|chirar|cayer|dar|tener|apretar|fregar|lavar|eixugar|tirar|empentar|lanzar|ligar|coser|contar|decir|cantar|chugar|flotar|fluir|chelar|inchar|sol|luna|estrela|agua|pluvia|río|lago|mar|sal|piedra|arena|polvo|tierra|nube|boira|cielo|viento|nieu|chelo|fumo|fuego|cenisa|quemar|camino|montanya|royo|verde|amariello|blanco|negro|nueit|día|anyo|calient|frío|plen|nuevo|viello|bueno|malo|podriu|sucio|recto|redondo|afilau|romo|liso|mullau|seco|correcto|cerca|leixos|dreita|zurda|a|en|con|y|si|porque|nombre|o|ser|gato|gata|perra|sonreir")

_AST = _pack("ast", "yo|tú|él|nosotros|vosotros|ellos|esti|esi|equí|ellí|quién|qué|ónde|cuándo|cómo|non|too|munchos|dalgunos|pocos|otru|un|dos|tres|cuatro|cinco|grande|llargu|anchu|grueso|pesáu|pequeñu|curtiu|estrechu|finu|muyer|home|persona|neñu|esposa|esposu|madre|padre|animal|pez|páxaru|perru|pioyu|cuélebre|gusanu|árbol|bosque|palu|fruta| grana|fueya|raíz|corteza|flor|yerba|cuerda|piel|carne|sangre|huesu|grasa|güevu|cuernu|cola|pluma|pelu|cabeza|oreya|güeyu|nariz|boca|diente|llingua|uña|pie|pierna|rodía|manu|ala|banduyu|tripes|pescuezu|llombu|pechu|corazón|fígado|beber|comer|morder|chupar|escupir|goler|sopliar|respirar|reír|ver|oír|saber|pensar|goler|temer|dormir|vivir|morrer|matar|lluchar|cazar|golpiar|cortar|fender|apuñalar|rascar|cavar|nadar|volar|caminar|venir|xacer|sentar|tar|xirar|cayer|dar|tener|apretar|fregar|llavar|enxugar|tirar|empuxar|llanzar|atar|coser|contar|dicir|cantar|xugar|flotar|fluir|xelar|inchir|sol|lluna|estrella|agua|lluvia|ríu|llagu|mar|sal|piedra|arena|polvu|tierra|nube|ñeblína|cielu|vientu|nieve|xelu|fumu|fueu|ceniza|quemar|caminu|montaña|bermeyu|verde|mariellu|blancu|negru|nueche|día|añu|caliente|fríu|llenú|nuevu|vieyu|bonu|malu|podre|suciu|rectu|redondu|afiaú|romo|llisu|moyáu|secu|correctu|cerca|llonxe|drecha|izquierda|a|en|con|y|si|porque|nome|el|ser|gatu|gata|perra|sonreír")


_LAD = _pack("lad", "yo|tu|el|mozotros|vozotros|eyos|este|ake|aki|ayi|ken|ke|onde|kuando|kumo|no|todo|munchos|algunos|pokos|otro|uno|dos|tres|kuatro|sinko|grande|largo|ancho|gordo|pezgado|chiko|kurto|estrecho|fino|mujer|ombre|persona|kriatura|mujer|marido|madre|padre|animal|peche|paxaro|perro|piojo|kulevro|gizano|arvole|boske|palo|fruta|simiente|oja|raiz|kortesa|flor|erva|kuerda|piel|karne|sangre|ueso|grasa|uevo|kuerno|kola|pluma|kaveyo|kavesa|oreja|ojo|nariz|boka|diente|lingua|unya|pie|pierna|rodía|mano|ala|vientre|tripas|kuello|espalda|pecho|korason|igado|bever|komer|morder|chupar|eskupir|vomitar|soplar|respirar|reír|ver|oyir|saver|pensar|oler|temer|durmir|bivir|morir|matar|luchár|kasar|golpear|kortar|fender|apunyalár|rascar|kavar|nadar|volar|kaminar|venir|yazer|sentar|estar|girar|kaer|dar|tener|apretar|fregar|lavar|enxugar|tirar|empujar|lançar|atar|kozer|kontar|dezir|kantar|jugar|flotar|fluir|jelar|inchar|sol|luna|estreya|agua|luvya|rio|lago|mar|sal|piedra|arena|polvo|tierra|nube|niebla|syelo|viento|nieve|yelo|fumo|fuego|seniza|kemar|kamino|montanya|kolorado|vedre|amariyo|blanko|preto|noche|diya|anyo|kaliente|frio|pleno|muevo|viejo|bueno|malo|podrido|suzio|derecho|redondo|agudo|romo|liso|mojado|seko|korrekto|serka|lexos|derecha|sierda|a|en|kon|i|si|porke|nombre|el|ser|gato|gata|perra|sonreír")

_MWL = _pack("mwl", "you|tu|el|nós|vós|eilhes|esto|esso|eiqui|alhá|quien|que|adonde|quando|cumo|nun|todo|muitos|alguns|poucos|outro|un|dous|trés|quatro|cinco|grande|longo|ancho|grosso|pesado|chico|curto|streito|fino|mulhier|home|pessoa|nina|mulhier|marido|mai|pai|animal|peixe|pássaro|can|piolho|serpe|gusan|arble|bosque|pau|fruta|semente|fuolha|raiz|casca|flor|yerba|corda|piel|carne|sangue|osso|gorda|oubo|corno|rabo|pena|cabelo|cabeça|orelha|uolho|nariz|boca|diente|léngua|unha|pié|perna|gionolho|mano|ala|vientre|tripas|pescuezo|costas|peito|coraçon|fígadu|beber|comer|morder|chupar|cuspir|vomitar|soprar|respirar|rir|ber|oubir|saber|pensar|cheirar|temer|dormir|bibir|morrer|matar|luitar|caçar|bater|cortar|fender|apunhalar|rascar|cabar|nadar|boar|andar|bir|jazer|sentar|star|girar|cair|dar|tener|apertar|fregar|labar|enxugar|puxar|empurrar|lançar|atar|coser|contar|dezir|cantar|jogar|flutuar|fluir|gelar|inchar|sol|lhuna|streilha|auga|chuba|río|lago|mar|sal|piedra|areia|pó|tierra|nubre|neblina|cielo|bento|nieve|gelo|fumo|fuego|cinza|queimar|camino|montanha|bermelho|berde|amarelo|branco|negro|nuite|die|anho|quente|frio|cheno|noubo|bielho|bueno|malo|podre|sujo|reto|redondo|afiado|romo|liso|molhado|seco|correto|cerca|lhonge|dreita|squierda|a|an|cun|i|se|porque|nome|l|ser|gato|gata|cadela|sorrir")

# Italo-Romance
_SCN = _pack("scn", "iu|tu|iddu|nuàutri|vuàutri|iddi|chistu|chiddu|ccà|ddà|cu|chi|unni|quannu|comu|nun|tuttu|assai|arcuni|picca|àutru|unu|dui|tri|quattru|cincu|granni|longu|largu|grossu|pisanti|nicu|curtu|strittu|sutili|fimmina|omu|pirsuna|picciriddu|mugghieri|maritu|matri|patri|armali|pisci|aceddu|cani|pidocchiu|serpì|vermi|àrbulu|voscu|mazzu|fruttu|simenza|fogghia|ràdica|scorcia|ciuri|erva|corda|peddi|carni|sangu|ossu|gràssu|ovu|cornu|cuda|pinna|capiddu|testa|ricchia|occhiu|nasu|vucca|denti|lingua|unghia|pedi|gamma|ginocchiu|manu|ala|panza|budella|collu|schina|pettu|cori|fìcatu|bìviri|manciari|mòrdiri|sucari|spùtari|vòmmiri|sciusciari|rispirari|rìdiri|vìdiri|sèntiri|sapiri|pinsari|ananzari|tèmiri|dòrmiri|vìviri|mòriri|ammazzari|cummàttiri|cacciari|bàttiri|tagghiari|spàccari|pugnialari|grattari|cavari|natari|vulari|caminari|vèniri|giaciri|sèdiri|stari|girari|càdiri|dari|tèniri|strìnciri|frìcari|lavari|asciucari|tirari|spìnciri|jittari|ligari|cùsiri|cuntari|dìciri|cantari|jucari|galleggiri|scùrriri|gilari|nzuffari|suli|luna|stidda|acqua|chiuvuta|ciumi|lagu|mari|sali|petra|rena|pruvulazzu|terra|nùvula|nebbia|celu|ventu|nivi|ghiacciu|fumu|focu|cinniri|bruciari|strata|muntagna|russu|virdi|giarnu|jancu|niru|notti|jornu|annu|càudu|friddu|chinu|novu|vecchiu|bonu|malu|marciu|sùricu|drittu|tunnu|tagghienti|ottusu|lìsciu|bagnatu|siccu|giustu|vicinu|luntanu|dritta|manca|a|nni|cu|e|si|picchì|nomu|lu|èssiri|jattu|jatta|cagna|surrìdiri")

_VEC = _pack("vec", "mi|ti|lu|noaltri|voaltri|lori|sto|quel|qua|là|chi|cossa|ndove|quando|come|no|tuto|tanti|alcuni|pochi|altro|un|do|tre|cuatro|zinque|grando|longo|largo|grosso|pezante|picolo|corto|stretto|fino|dona|omo|persona|toso|mujere|marìo|mare|pare|animale|pese|osel|can|pedocio|bisato|verme|àlbaro|bosco|baston|fruto|seme|foja|raixa|scorza|fior|erba|corda|pele|carne|sangue|osso|graso|ovo|corno|coa|pena|cavei|testa|recia|ocio|naso|boca|dente|lengua|ongia|pie|gamba|zenocio|man|ala|panza|buele|colo|schena|peto|cuor|fégato|bére|magnar|mòrdar|suciar|sputar|vomitar|bufar|respirar|ríder|védar|sèntar|saver|pensar|sentir|tèmar|dórmar|vívar|mòrar|masar|conbàtar|cazar|bàtar|tajar|spacar|pontar|gratar|cavar|nadar|volar|caminar|vegnir|giacer|sètar|star|girar|càdar|dar|tegner|strénzar|fregar|lavar|sugàr|tirar|spénzar|butar|ligar|cùsar|contar|dir|cantar|zugàr|galegiar|scórrar|gelar|gonfiar|sol|luna|stela|aqua|piova|fiume|lago|mar|sal|piera|sabia|pólvare|tera|nùvola|nebcia|sielo|vento|neve|giazzo|fumo|fogo|sénare|brusar|strada|montagna|roso|verde|zalo|bianco|nero|note|dì|ano|caldo|fredo|pien|novo|vecio|bon|cativo|marso|sporco|drito|tondo|pontuo|otuso|liso|bagnà|seco|giusto|visin|lontan|drita|sanca|a|in|co|e|se|parché|nome|el|èser|gato|gata|cagna|soríder")

_LMO = _pack("lmo", "mi|ti|lü|nüm|viàlter|lur|chest|quel|chì|là|chi|cossa|indue|quand|cume|minga|tüt|tanc|quajdün|pöch|alter|vün|duu|trii|quater|cinch|grant|longh|largh|gross|pesant|piscininn|curt|strècc|fin|dona|òm|persona|fiö|miee|marì|mader|pader|animal|pess|osel|can|piöcc|biscia|verm|alber|bosch|baston|frut|semenza|föja|radis|scorza|fiur|erba|corda|pell|carn|sanch|oss|grass|öf|corn|coa|penna|cavei|co|oregia|ögg|nas|boca|dent|lengua|ongia|pee|gamba|genoeugg|man|ala|pancia|büdell|coll|schiena|pett|cör|fégat|bev|mangià|morsgà|sücià|sputà|vomità|sfià|respirà|rìd|vedè|sentì|savè|pensà|sentì|temè|durmì|viv|murì|mazzà|combat|cacià|bat|tajà|spaccà|pugnalà|grattà|cavà|nadà|volà|caminà|gnì|giacè|setàss|stà|girà|càd|dà|tgnì|strens|fregà|lavà|sügià|tirà|sping|trà|ligà|cüsì|contà|dì|cantà|giugà|galegià|scór|gelà|gonfià|sul|luna|stela|acqua|pioeuva|fiüm|lagh|mar|sal|preja|sabia|polver|terra|nìvola|nebia|cel|vent|nev|giazz|füm|fögh|sener|brüsà|strada|montagna|russ|verd|giald|bianch|negher|nott|dì|ann|cald|fredd|pien|nöf|vegg|bon|cattiv|marsc|sporc|dritt|tond|pontüd|otüs|lis|bagnà|sech|giüst|vesin|lontan|drita|manca|a|in|cont|e|se|perchè|nom|el|vèss|gat|gata|cagna|surìd")

# Cells Wiktionary's Piedmontese Swadesh list covers follow it.
# Cell by cell: docs/eval/grid_sources.md.
_PMS = _hits("pms", {
    "i": "mi", "you_sg": "ti", "he": "chiel", "we": "noi", "you_pl": "voi", "they": "lor",
    "this": "cost", "that": "col", "here": "sì", "there": "là", "who": "chi", "what": "lòn",
    "where": "andoa", "when": "quand", "how": "com", "not": "nen", "all": "tut", "many": "tant",
    "some": "chèich", "few": "pòch", "other": "àutr", "one": "un", "two": "doi", "three": "tre",
    "four": "quatr", "five": "sinch", "big": "gròss", "long": "longh", "wide": "largh",
    "thick": "tëgg", "heavy": "grev", "small": "cit", "short": "curt", "narrow": "strèit",
    "thin": "fin", "woman": "fomna", "man": "òm", "person": "përson-a", "child": "cit",
    "wife": "fomna", "husband": "òm", "mother": "mare", "father": "pare", "animal": "animal",
    "fish": "pess", "bird": "osel", "dog": "can", "louse": "poj", "snake": "sërpent",
    "worm": "verm", "tree": "erbo", "forest": "bòsch", "stick": "baston", "fruit": "fruta",
    "seed": "smens", "leaf": "feuja", "root": "rèis", "bark": "scòrsa", "flower": "fior",
    "grass": "erba", "rope": "corda", "skin": "pel", "meat": "carn", "blood": "sangh",
    "bone": "òss", "fat": "grass", "egg": "euv", "horn": "còrn", "tail": "coa", "feather": "piuma",
    "hair": "cavèj", "head": "testa", "ear": "aurija", "eye": "euj", "nose": "nas", "mouth": "boca",
    "tooth": "dent", "tongue": "lenga", "fingernail": "ongia", "foot": "pe", "leg": "gamba",
    "knee": "gënoj", "hand": "man", "wing": "ala", "belly": "pansa", "guts": "boele", "neck": "còl",
    "back": "schin-a", "breast": "pet", "heart": "cheur", "liver": "fìdich", "drink": "bèive",
    "eat": "mangé", "bite": "mòrde", "suck": "ciucé", "spit": "spuvé", "vomit": "vomité",
    "blow": "bufé", "breathe": "arspiré", "laugh": "rije", "see": "vëdde", "hear": "sente",
    "know": "savèj", "think": "pensé", "smell": "snufié", "fear": "tëmme", "sleep": "deurme",
    "live": "vive", "die": "meuire", "kill": "massè", "fight": "combate", "hunt": "cassé",
    "hit": "bate", "cut": "tajé", "split": "spartì", "stab": "stileté", "scratch": "sgrafigné",
    "dig": "sgavé", "swim": "noé", "fly": "volé", "walk": "caminé", "come": "vnì", "lie": "cogesse",
    "sit": "setesse", "stand": "sté", "turn": "viré", "fall": "tombè", "give": "dé",
    "hold": "ten-e", "squeeze": "spërme", "rub": "fërté", "wash": "lavé", "wipe": "suvé",
    "pull": "tiré", "push": "possé", "throw": "frandé", "tie": "gropé", "sew": "cuse",
    "count": "conté", "say": "dì", "sing": "canté", "play": "giughé", "float": "floté",
    "flow": "score", "freeze": "geilé", "swell": "anfié", "sun": "sol", "moon": "lun-a",
    "star": "stèila", "water": "eva", "rain": "pieuva", "river": "fium", "lake": "lagh",
    "sea": "mar", "salt": "sal", "stone": "pera", "sand": "sabia", "dust": "póer", "earth": "mond",
    "cloud": "nìvola", "fog": "nëbbia", "sky": "cel", "wind": "vent", "snow": "fiòca",
    "ice": "giassa", "smoke": "fum", "fire": "feu", "ash": "sënner", "burn": "brusé",
    "road": "stra", "mountain": "montagna", "red": "ross", "green": "verd", "yellow": "giàun",
    "white": "bianch", "black": "nèir", "night": "neuit", "day": "dì", "year": "ann",
    "warm": "càud", "cold": "frèid", "full": "pien", "new": "neuv", "old": "vej", "good": "bon",
    "bad": "gram", "rotten": "marsent", "dirty": "anflà", "straight": "drit", "round": "riond",
    "sharp": "avuss", "dull": "sirognà", "smooth": "seuli", "wet": "bagnà", "dry": "sech",
    "correct": "giust", "near": "aranda", "far": "lontan", "right": "drita", "left": "gàucia",
    "at": "a", "in": "an", "with": "con", "and": "e", "if": "se", "because": "përchè",
    "name": "nòm", "def_art": "ël", "copula": "esse", "cat": "gat", "cat_f": "gata",
    "dog_f": "cagna", "smile": "surrìe",
})

# Cells Wiktionary's Ligurian Swadesh list covers follow it, in its spelling.
# Cell by cell: docs/eval/grid_sources.md.
_LIJ = _hits("lij", {
    "i": "mi", "you_sg": "ti", "he": "lê", "we": "niâtri", "you_pl": "viâtri", "they": "lô",
    "this": "sto", "that": "quéllo", "here": "chi", "there": "la", "who": "chi", "what": "cöse",
    "where": "dôve", "when": "quànde", "how": "cómme", "not": "no", "all": "tùtto", "many": "tànto",
    "some": "quàrche", "few": "pöco", "other": "âtro", "one": "un", "two": "doî", "three": "tréi",
    "four": "quàttro", "five": "çìnque", "big": "grànde", "long": "lóngo", "wide": "làrgo",
    "thick": "drûo", "heavy": "pezànte", "small": "piccìn", "short": "cùrto", "narrow": "stréito",
    "thin": "sotî", "woman": "dònna", "man": "òmmo", "person": "persónn-a", "child": "figeu",
    "wife": "mogê", "husband": "marîo", "mother": "moæ", "father": "poæ", "animal": "animâ",
    "fish": "péscio", "bird": "öxéllo", "dog": "càn", "louse": "pighéuggio", "snake": "serpénte",
    "worm": "verme", "tree": "èrbo", "forest": "bosco", "stick": "bacco", "fruit": "frûta",
    "seed": "armella", "leaf": "féuggia", "root": "réixe", "bark": "scorsa", "flower": "sciô",
    "grass": "erba", "rope": "corda", "skin": "pelle", "meat": "carne", "blood": "sàngoe",
    "bone": "osso", "fat": "grascia", "egg": "êuvo", "horn": "corno", "tail": "côa",
    "feather": "penna", "hair": "cavello", "head": "testa", "ear": "oêgia", "eye": "éuggio",
    "nose": "nâzo", "mouth": "bocca", "tooth": "dente", "tongue": "léngoa", "fingernail": "ongia",
    "foot": "pê", "leg": "ganba", "knee": "zenoggio", "hand": "man", "wing": "âa", "belly": "pansa",
    "guts": "intestin", "neck": "collo", "back": "schénn-a", "breast": "pêto", "heart": "cheu",
    "liver": "figæto", "drink": "béive", "eat": "mangiâ", "bite": "adentâ", "suck": "susâ",
    "spit": "spuâ", "vomit": "vomitâ", "blow": "sciusciâ", "breathe": "respiâ", "laugh": "rîe",
    "see": "védde", "hear": "sentî", "know": "savéi", "think": "pensâ", "smell": "ödoâ",
    "fear": "témme", "sleep": "dormî", "live": "vîve", "die": "moî", "kill": "amasâ",
    "fight": "conbatte", "hunt": "cacciâ", "hit": "batte", "cut": "tagiâ", "split": "dividde",
    "stab": "cotelâ", "scratch": "gratâ", "dig": "scavâ", "swim": "nuâ", "fly": "xoâ",
    "walk": "caminâ", "come": "vegnî", "lie": "destendise", "sit": "asetâse", "stand": "stâ",
    "turn": "gjâ", "fall": "càzze", "give": "dâ", "hold": "tegnî", "squeeze": "spremme",
    "rub": "fretâ", "wash": "lavâ", "wipe": "sciugâ", "pull": "tiâ", "push": "spinze",
    "throw": "tiâ", "tie": "ligâ", "sew": "cuxî", "count": "contâ", "say": "dî", "sing": "cantâ",
    "play": "zugâ", "float": "galezâ", "flow": "scorre", "freeze": "zeâ", "swell": "gonfiâ",
    "sun": "sô", "moon": "lùnn-a", "star": "stélla", "water": "ægoa", "rain": "ægoa",
    "river": "sciùmme", "lake": "lâgo", "sea": "mâ", "salt": "sâ", "stone": "prîa", "sand": "ænn-a",
    "dust": "pûa", "earth": "tæra", "cloud": "nûvia", "fog": "nêgia", "sky": "çê", "wind": "vento",
    "snow": "néive", "ice": "giassa", "smoke": "fumme", "fire": "fêugo", "ash": "çeine",
    "burn": "brüxâ", "road": "stradda", "mountain": "montagna", "red": "rosso", "green": "verde",
    "yellow": "giâno", "white": "gianco", "black": "néigro", "night": "néutte", "day": "giorno",
    "year": "anno", "warm": "câdo", "cold": "fréido", "full": "pìn", "new": "nêuvo", "old": "vêgio",
    "good": "bon", "bad": "catîvo", "rotten": "marso", "dirty": "sücido", "straight": "drîto",
    "round": "rióndo", "sharp": "afilòu", "dull": "smusòu", "smooth": "lìscio", "wet": "bagnòu",
    "dry": "sécco", "correct": "giùsto", "near": "vixìn", "far": "lontàn", "right": "drîta",
    "left": "mancìnn-a", "at": "a", "in": "in", "with": "con", "and": "e", "if": "se",
    "because": "perché", "name": "nómme", "def_art": "o", "copula": "êse", "cat": "gàtto",
    "cat_f": "gàtta", "dog_f": "cagna", "smile": "sorrîe",
})

_FUR = _pack("fur", "jo|tu|lui|no|vo|lôr|chest|chel|ca|là|cui|ce|dulà|cuant|cemût|no|dut|tancj|cualchi|pôcs|altri|un|doi|trê|cuatri|cinc|grant|lunc|largj|grôs|pesant|piçul|curt|strent|fin|femine|om|person|frut|muîr|mâr|mari|pari|nemâl|pesc|ucel|cjan|pedoc|sarpint|vier|arbul|bosc|baston|frut|semence|fuee|lidrîs|scorse|flôr|jerbe|cuarde|piel|cjar|sanc|os|gràs|ûf|cuar|code|pene|cjaviei|cjâf|orele|voli|nâs|bocje|dint|lenghe|ongule|pît|gjame|zenoli|man|ale|panze|budel|cuel|schene|pet|cûr|fêt|bevi|mangjâ|muardi|sucâ|spudâ|vomitâ|sotâ|respirâ|ridi|viodi|sintî|savê|pensâ|sintî|temê|durmî|vivi|murî|copâ|combat|cjace|bati|taiâ|specâ|pugnalâ|grate|scjavâ|nadâ|svolâ|caminâ|vignî|jacer|siedi|stâ|zirâ|cjadê|dâ|tignî|strenç|fregâ|lavâ|sûsâ|tirâ|spindi|butâ|leâ|cusi|contâ|dî|cjantâ|zuiâ|galegjâ|scori|gelâ|gonfiâ|sôr|lune|stele|aghe|ploe|flum|lâc|mâr|sâl|piere|savalon|pulvin|tiere|nûl|gjavine|cîl|vint|nêf|glaç|fûm|fûc|cinise|brusâ|strade|mont|ros|vert|zâl|blanc|neri|gnot|dì|an|cjalt|frêt|plen|gnûf|vieli|bon|trist|madur|sporc|dret|ront|pontût|otûs|lis|bagnât|sec|just|dongje|lontan|drete|çampe|a|in|cun|e|se|parcè|non|il|jessi|gjat|gjate|cagne|sorridi")

# Cells Wiktionary's Emilian Swadesh list covers follow it (Bolognese spelling).
# Cell by cell: docs/eval/grid_sources.md.
_EML = _hits("eml", {
    "i": "mé", "you_sg": "té", "he": "ló", "we": "nuèter", "you_pl": "vuèter", "they": "lôr",
    "this": "sté", "that": "cal", "here": "qué", "there": "là", "who": "chi", "what": "côsa",
    "where": "dóvv", "when": "quand", "how": "cme", "not": "an", "all": "tótt", "many": "tant",
    "some": "socuànt", "few": "pôc", "other": "èter", "one": "ón", "two": "dû", "three": "trî",
    "four": "quâter", "five": "zénc", "big": "grand", "long": "lóng", "wide": "lèrg",
    "thick": "féss", "heavy": "paiṡ", "small": "cén", "short": "cûrt", "narrow": "stratt",
    "thin": "fén", "woman": "dòna", "man": "òmen", "person": "parsåṅna", "child": "cínno",
    "wife": "mujêr", "husband": "maré", "mother": "mèder", "father": "pèder", "animal": "animèl",
    "fish": "pass", "bird": "uṡèl", "dog": "can", "louse": "bdòc'", "snake": "sarpänt",
    "worm": "lunbrîṡ", "tree": "élber", "forest": "furèsta", "stick": "bastån", "fruit": "frûta",
    "seed": "smänt", "leaf": "fójja", "root": "radîṡ", "bark": "scôrza", "flower": "fiåur",
    "grass": "êrba", "rope": "côrda", "skin": "pèl", "meat": "chèren", "blood": "sangv",
    "bone": "òs", "fat": "grâs", "egg": "ôv", "horn": "côrna", "tail": "cô", "feather": "panna",
    "hair": "cavî", "head": "cô", "ear": "uraccia", "eye": "òc'", "nose": "nèṡ", "mouth": "båcca",
    "tooth": "dänt", "tongue": "längua", "fingernail": "ónngia", "foot": "pà", "leg": "ganba",
    "knee": "źnòć", "hand": "man", "wing": "èglia", "belly": "panza", "guts": "intestén",
    "neck": "còl", "back": "schéṅna", "breast": "pèt", "heart": "côr", "liver": "fégghet",
    "drink": "bàvver", "eat": "magnèr", "bite": "muṡghèr", "suck": "sucèr", "spit": "spudèr",
    "vomit": "vumitèr", "blow": "supièr", "breathe": "respirèr", "laugh": "rédder", "see": "vàdder",
    "hear": "sénter", "know": "savair", "think": "pinsèr", "smell": "naṡèr", "fear": "tmèr",
    "sleep": "durmîr", "live": "vîver", "die": "murîr", "kill": "mazèr", "fight": "cunbâter",
    "hunt": "cazièr", "hit": "bâter", "cut": "tajèr", "split": "divîder", "stab": "pugnalèr",
    "scratch": "ṡgranfgnèr", "dig": "scavèr", "swim": "nudèr", "fly": "vulèr", "walk": "caminèr",
    "come": "vgnîr", "lie": "dstànndres", "sit": "sêder", "stand": "stèr", "turn": "girèr",
    "fall": "caschèr", "give": "dèr", "hold": "tgnîr", "squeeze": "scuizèr", "rub": "sfarghèr",
    "wash": "lavèr", "wipe": "sughèr", "pull": "tirèr", "push": "spénnżer", "throw": "trèr",
    "tie": "lighèr", "sew": "cûṡer", "count": "cuntèr", "say": "dîr", "sing": "cantèr",
    "play": "żughèr", "float": "galegèr", "flow": "pasèr", "freeze": "żlèr", "swell": "gunfièr",
    "sun": "sól", "moon": "lóṅna", "star": "strèla", "water": "âcua", "rain": "piôva",
    "river": "fiómm", "lake": "lèg", "sea": "mèr", "salt": "sèl", "stone": "sâs", "sand": "sâbia",
    "dust": "pólvra", "earth": "tèra", "cloud": "nóvvla", "fog": "nèbia", "sky": "zîl",
    "wind": "vänt", "snow": "naiv", "ice": "giâz", "smoke": "fómm", "fire": "fûg", "ash": "zànnder",
    "burn": "bruṡèr", "road": "strè", "mountain": "muntâgna", "red": "råss", "green": "vaird",
    "yellow": "żâl", "white": "bianc", "black": "naigher", "night": "nòt", "day": "dé",
    "year": "ân", "warm": "chèld", "cold": "fredd", "full": "pén", "new": "nôv", "old": "vèc'",
    "good": "bón", "bad": "catîv", "rotten": "mèrz", "dirty": "malnàtt", "straight": "drétt",
    "round": "tånnd", "sharp": "arfilè", "dull": "ṡmusè", "smooth": "léss", "wet": "mói",
    "dry": "sacc", "correct": "giósst", "near": "avṡén", "far": "luntàn", "right": "drétta",
    "left": "stanca", "at": "a", "in": "in", "with": "con", "and": "e", "if": "se",
    "because": "parché", "name": "nómm", "def_art": "al", "copula": "èser", "cat": "gât",
    "cat_f": "gâta", "dog_f": "càgna", "smile": "surìder",
})

# The twelve cells Wiktionary's Ladin Swadesh list covers follow it.
# Cell by cell: docs/eval/grid_sources.md.
_LLD = _hits("lld", {
    "i": "ie", "you_sg": "tu", "he": "ël", "we": "nos", "you_pl": "vos", "they": "ëi",
    "this": "chësc", "that": "chel", "here": "ca", "there": "ilà", "who": "chi", "what": "cie",
    "where": "ulà", "when": "can", "how": "co", "not": "ne", "all": "duc", "many": "tant",
    "some": "valgun", "few": "püch", "other": "auter", "one": "un", "two": "doi", "three": "trei",
    "four": "cater", "five": "cinch", "big": "gran", "long": "lun", "wide": "largh",
    "thick": "gros", "heavy": "pesant", "small": "picé", "short": "curt", "narrow": "stret",
    "thin": "fin", "woman": "femena", "man": "om", "person": "persona", "child": "mut",
    "wife": "femena", "husband": "om", "mother": "oma", "father": "pere", "animal": "animal",
    "fish": "pësc", "bird": "ucel", "dog": "cian", "louse": "pedoc", "snake": "sörp",
    "worm": "vierm", "tree": "lën", "forest": "bosc", "stick": "baston", "fruit": "frut",
    "seed": "somënza", "leaf": "föia", "root": "rajé", "bark": "scorza", "flower": "flor",
    "grass": "ërba", "rope": "cuerda", "skin": "pël", "meat": "ciar", "blood": "sangu",
    "bone": "ues", "fat": "gràsc", "egg": "uef", "horn": "corn", "tail": "coa", "feather": "pëna",
    "hair": "ciavei", "head": "co", "ear": "orëdles", "eye": "edl", "nose": "nas", "mouth": "bocia",
    "tooth": "dënt", "tongue": "lënga", "fingernail": "ongia", "foot": "pé", "leg": "gamba",
    "knee": "genui", "hand": "man", "wing": "ala", "belly": "panza", "guts": "budëi",
    "neck": "cuel", "back": "schiena", "breast": "pet", "heart": "cör", "liver": "fëia",
    "drink": "béive", "eat": "mangé", "bite": "mórdë", "suck": "sucé", "spit": "spudé",
    "vomit": "vomité", "blow": "sofblé", "breathe": "respiré", "laugh": "rí", "see": "odëi",
    "hear": "udir", "know": "savei", "think": "pensé", "smell": "sentí", "fear": "temëi",
    "sleep": "dormir", "live": "ví", "die": "murí", "kill": "mazé", "fight": "combatë",
    "hunt": "ciacé", "hit": "bate", "cut": "tajé", "split": "spaché", "stab": "pugnalé",
    "scratch": "graté", "dig": "cavé", "swim": "nudé", "fly": "svolé", "walk": "jì", "come": "gnì",
    "lie": "giacé", "sit": "senté", "stand": "sté", "turn": "ziré", "fall": "tomé", "give": "dé",
    "hold": "tëne", "squeeze": "strënze", "rub": "freghé", "wash": "lavé", "wipe": "seché",
    "pull": "tiré", "push": "spënze", "throw": "buté", "tie": "lié", "sew": "cusé",
    "count": "conté", "say": "dì", "sing": "cianté", "play": "jiugé", "float": "galegié",
    "flow": "scoré", "freeze": "jelé", "swell": "gonfié", "sun": "sörëdl", "moon": "luna",
    "star": "stëla", "water": "ega", "rain": "plueia", "river": "rënn", "lake": "lech",
    "sea": "mer", "salt": "sel", "stone": "pera", "sand": "sablun", "dust": "pulë", "earth": "tera",
    "cloud": "nüla", "fog": "nebia", "sky": "ciel", "wind": "vent", "snow": "nëi", "ice": "dlacia",
    "smoke": "fum", "fire": "fuech", "ash": "cënera", "burn": "brusé", "road": "streda",
    "mountain": "crep", "red": "cuecen", "green": "vërt", "yellow": "ghel", "white": "blanch",
    "black": "ner", "night": "nuet", "day": "dì", "year": "ann", "warm": "cald", "cold": "frëit",
    "full": "plën", "new": "nuef", "old": "vedl", "good": "bon", "bad": "trënc", "rotten": "marz",
    "dirty": "soz", "straight": "dërt", "round": "tont", "sharp": "spitz", "dull": "stuz",
    "smooth": "lisc", "wet": "bagné", "dry": "sech", "correct": "just", "near": "dainé",
    "far": "lontan", "right": "dërta", "left": "sanica", "at": "a", "in": "te", "with": "cun",
    "and": "y", "if": "sce", "because": "aicó", "name": "inuem", "def_art": "l", "copula": "ester",
    "cat": "giat", "cat_f": "giata", "dog_f": "ciana", "smile": "surí",
})

# Wiktionary's Istriot Swadesh list, plus forms its Istriot entries gloss with the
# concept. The Venetian-looking list that used to fill this column is gone.
# Cell by cell: docs/eval/grid_sources.md.
_IST = _hits("ist", {
    "i": "i", "you_sg": "ti", "he": "lù", "we": "nui", "you_pl": "vui", "they": "luri",
    "this": "stu", "that": "quil", "here": "lai", "there": "là", "not": "nu", "all": "doûto",
    "some": "alquanto", "few": "puoco", "other": "altro", "one": "oûn", "two": "dui",
    "three": "tri", "four": "quatro", "five": "sinque", "big": "grando", "long": "longo",
    "wide": "largo", "small": "peîcio", "short": "baso", "narrow": "strento", "woman": "duona",
    "man": "omo", "child": "peîcio", "wife": "muier", "husband": "mareî", "mother": "mare",
    "father": "pare", "animal": "bestia", "fish": "piso", "bird": "uzai", "dog": "can",
    "louse": "gèndana", "snake": "bìsa", "worm": "vièrmo", "tree": "arbo", "stick": "bastón",
    "flower": "fiùr", "grass": "gièrba", "rope": "curda", "meat": "carno", "bone": "uosso",
    "egg": "ùo", "horn": "cuorno", "head": "tiesta", "eye": "uocio", "mouth": "bóca",
    "tongue": "lèngua", "leg": "ganba", "knee": "zanucio", "hand": "man", "wing": "ala",
    "guts": "budèi", "neck": "còlo", "heart": "core", "drink": "bévi", "eat": "magnà",
    "bite": "mursagà", "see": "vidi", "hear": "uldì", "know": "savì", "think": "pansà",
    "hit": "bati", "cut": "talgià", "split": "talgià", "dig": "badilà", "come": "vignì",
    "turn": "vultà", "fall": "cascà", "give": "dà", "throw": "butà", "say": "deî", "sun": "sul",
    "star": "stila", "water": "aqua", "rain": "piova", "river": "fioûme", "sea": "mare",
    "salt": "sal", "stone": "pera", "earth": "tiera", "cloud": "nenbo", "sky": "sil",
    "wind": "vento", "snow": "bringiera", "ice": "giasso", "smoke": "foûmo", "fire": "fògo",
    "ash": "buistro", "burn": "ardi", "road": "veîa", "mountain": "monto", "red": "russo",
    "green": "virdo", "yellow": "zalo", "white": "bianco", "black": "nìgaro", "night": "nuoto",
    "day": "dèi", "year": "ano", "cold": "frido", "new": "nùvo", "old": "viecio", "good": "bon",
    "round": "tunduleîno", "wet": "bagnà", "dry": "arso", "near": "atacà", "at": "a", "in": "in",
    "with": "cun", "and": "e", "if": "se", "because": "asoché", "name": "nom", "def_art": "el",
})

# Gallo-Romance oïl / occitan
_WA = _pack("wa", "dji|vos|i|nozôtes|vozôtes|i|cisse|cisse-la|chal|la|kî|cwè|wice|wince|comint|nén|tot|bråmint|kékès|pô|ôte|on|deu|troes|cwate|cénk|grand|long|lådj|spès|pejhe|pitit|court|estroet|fin|femè|ome|djin|efant|femè|marî|mere|pere|biesse|pexhon|oujhea|tchet|peu|sierpe|vèr|åbe|bwès|båton|frut|grinne|fowe|raecene|scoice|fleur|yèbe|coide|pea|tchå|sonk|oxhea|grèxhe|ou|coine|coye|pène|tcheveu|tiesse|oraye|ouy|nez|boke|dint|linwe|ongue|pî|djambe|genoy|mwin|aile|vinte|boyeas|col|dos|pétrin|coir|foye|boere|magnî|mordre|sûcî|cratchî|vomî|sofler|souffler|rire|vey|oyî|saveur|penser|fleurer|crinde|dormi|viker|mourî|touwer|bater|tchessî|coyî|côper|finde|pougnarder|grater|creuser|nôzer|voler|tchessa|vini|djumî|s'ashir|ståner|tourner|tcheur|dner|tni|serrer|froter|laver|sitchî|tîner|poussî|taper|loymer|côde|conter|dire|chanter|djouwer|flotter|couler|djelé|gonfler|solea|lune|steule|aiwe|plouve|aiwe|lak|mer|sé|pîre|såvlon|poussire|tere|nûlêye|broulård|cir|vent|nive|glaece|foumire|feu|cinde|brouî|voye|montinne|rodje|vert|djaene|blanc|noer|nute|djoû|anêye|tchaud|froed|plein|novea|vî|bon|måva|poerri|soû|droit|rond|agu|moussî|lisse|mouyî|setch|djust|près|lon|droete|hintche|a|e|avou|et|si|paski|no|li|esse|tchet|tchete|tchete|sourire")

_PCD = _pack("pcd", "mi|ti|him|nos|vos|eus|chu|cha|ichi|lo|qui|quoé|dousque|quand|commint|mie|tout|boin|queuques|peu|eute|un|deus|troés|quate|chonc|grand|long|large|épé|lourd|p'tit|court|étroét|mince|fanme|honme|ésonnes|éfant|fanme|mari|mére|père|bète|pésson|osiau|kien|pou|sérpent|vér|abe|bos|bâton|fruit|grainne|fuelle|racine|écorche|fleur|érbe|corde|pieu|char|sang|os|graisse|oeu|corne|keuwe|plume|chéveu|tiète|orelle|oeul|né|bouque|dint|langue|ongle|pié|jambe|génou|main|aile|vinte|boyau|cou|dos|poétrine|keur|foé|boére|minger|mordre|sucer|cracher|vomir|souffler|respirer|rire|vir|oïr|savoér|penser|flairer|crindre|dormir|vivre|mourir|tuer|bate|chèsser|battre|couper|fendre|poignarder|grater|creuser|nager|voler|marcher|venir|gisir|s'assir|s'tenir|tourner|tomber|donner|tenir|sérer|froter|laver|sécher|tirer|pousser|jeter|loyer|coudre|conter|dire|canter|jouer|flotter|couler|gler|gonfler|solé|lune|étoile|iau|pluie|rivière|lac|mer|sé|pierre|sable|poussiére|tére|nuage|brouillard|ciel|vent|nèche|glache|fumée|feu|chendres|brûler|route|montagne|rouche|vert|jone|blanc|noér|nuit|jou|année|chaud|froéd|plén|nouvieu|vieux|bon|méchant|poérri|sale|droét|rond|agu|émoussé|lisse|mouillé|sec|just|près|lon|droéte|gauche|à|in|avec|et|si|parché|nom|ch'|ète|cat|cate|chiène|sourire")

_NRF = _pack("nrf", "jé|tu|il|nouos|vouos|ils|chu|ch'la|ichîn|ilo|qui|qué|ioù|quand|coume|né|touot|byin|tchiq's|pou|aute|eun|deu|treis|quate|chîn|graund|long|lârg|épais|lourd|p'tit|court|êtrait|minche|femme|houme|persoune|mousse|femme|marri|méthe|péthe|bête|peîsson|oîsé|tchian|pou|sépent|vê|arbre|bouais|bâton|fruit|graine|fueille|racine|êcorche|flieur|hèrbe|corde|pé|char|sang|os|graisse|oeu|corne|coue|pliume|cheveu|téte|othelle|yi|nez|bouche|dent|langue|ongle|pid|jambe|génou|main|aile|ventre|boyaux|cou|dos|poitrine|tchoeu|foie|baîre|mangi|mordre|sucer|crachi|vomi|souffli|respirer|rithe|vaie|ouï|savei|penser|senti|criendre|dormi|vivre|mouothi|tuer|battre|quachi|battre|couper|fendre|poignardi|gratter|creûser|nagier|voli|marchi|venin|gisi|s'assiéthe|se t'nin|touônner|tomber|dounner|t'nin|sèrri|frotter|laver|séchi|tirer|pousser|jeter|lier|coudre|couompter|dithe|chaunter|jouaer|flotter|couler|g'ler|gonfler|solé|lune|étoîle|iae|pllie|riviéthe|lac|mé|sé|pierre|sablion|poussiéthe|téthe|nuage|brouillard|ciel|vent|né|gllâche|fumée|feu|chendres|brûler|route|montangne|rouoge|vèrt|jaune|blaunc|neir|niet|jou|annaée|caud|fraid|plyin|nouvé|vyi|bouon|mauvais|pouôrri|sale|dré|rond|aigui|émoussé|lisse|mouoilli|sec|juste|près|llioin|dréte|gauche|à|en|dauve|et|si|pasque|nom|lé|être|cat|cate|chienne|souôri")

_FRP = _pack("frp", "je|te|lui|nos|vos|lor|cen|cil|tê|yal|qui|que|yô|quand|coment|pas|tot|tâs|quârques|pou|ôtro|yon|dos|três|quatro|cinq|grant|long|lârjo|èpês|lourd|petiôt|côrt|ètrêt|fin|fèna|homo|pèrsona|enfant|fèna|mari|mâre|pâre|bètye|pechhon|usél|chin|pou|sèrpent|vèrm|âbro|bôsc|bâton|frût|grena|fôlye|racena|ècôrce|fllor|hèrba|côrda|pêl|châr|sang|os|grâssa|ôf|côrna|coa|pluma|chevél|téta|orèlye|uely|nâs|boche|dent|lengoua|ongla|piéd|jamba|genoly|man|ala|ventro|boyél|côl|dos|pêtrena|cœur|fèy|bêre|mangiér|môrdre|suciér|crachiér|vomir|soflar|respirar|rire|vêre|odre|savêr|pensar|sentir|crendre|dormir|vivre|morir|tuar|batre|chaciér|batre|copar|fendre|poignardar|gratar|crevar|nagiér|volar|marcar|vegnir|gisir|s'assêre|sè tenér|tornar|tombar|balyér|tenér|sèrrar|frotar|lavar|sèchiér|tirar|poussar|jètar|liar|coudre|comptar|dire|chantar|jouar|flotar|colar|gèlar|gonflar|solèly|luna|ètêla|égoua|plove|riviére|lac|mar|sâl|piérra|sabllo|poussiére|tèrra|niola|brumes|cièl|vent|né|gllace|fum|fuè|cendre|brûlar|rota|montagne|roge|vèrd|jôno|blanc|nêr|nuet|jorn|an|chôd|frêd|plen|novél|viél|bon|crouyo|porri|sâlo|drêt|rond|agu|èmossâ|lisse|molyê|sèc|justo|près|luen|drêta|gôche|a|en|avouéc|et|se|perceque|nom|lo|étre|chat|chata|chinna|sourîre")

_GALLO = _pack("gallo", "je|te|i|nozaut|vozaut|eus|ceu|cela|ichi|la|qi|qei|iou|qand|come|pas|tout|ben|qeqes|pou|aote|un|deou|treis|qate|cinq|grand|long|lârge|épé|louord|petit|court|étroet|mince|fenne|houme|persoune|éfant|fenne|mari|mére|pére|béte|peisson|ouésé|chien|pou|sérpent|vér|abe|bouéz|bâton|frut|graine|fuelle|racine|écorce|fleur|herbe|corde|pé|char|sang|os|graisse|oeu|corne|qeoue|plume|cheveu|téte|orelle|ueil|né|bouche|dent|langue|ongle|pié|jambe|génou|main|aile|ventre|boyaux|cou|dos|poitrine|queor|foie|beire|mangi|mordre|sucer|crachi|vomir|soufler|respirer|rire|veir|ouïr|saveir|penser|sentir|crindre|dormir|vivre|mouri|tuer|batre|chasser|batre|couper|fendre|poignarder|grater|creuser|nager|voler|marcher|venir|gisir|s'asseir|se tenir|tourner|tomber|donner|tenir|serrer|froter|laver|sécher|tirer|pousser|jeter|lier|coudre|conter|dire|chanter|jouer|flotter|couler|geler|gonfler|solei|lune|étoile|ewe|plleue|rivière|lac|mer|sé|piérre|sable|poussiére|terre|nuage|brouillard|ciel|vent|né|glace|fumée|feu|cendre|brûler|route|montagne|rouoge|vert|jaune|blanc|neir|net|jou|année|chaud|fraid|plen|noviau|vié|bon|mêchant|pourri|sâle|dret|rond|agu|émoussé|lisse|mouillé|sec|juste|près|llioin|drete|gauche|a|en|od|et|si|parce|nom|le|être|chat|chate|chienne|sourire")

_GSC = _pack("gsc", "jo|tu|eth|nosauts|vosauts|eths|aqueste|aqueth|ací|aquí|qui|qué|on|quan|coma|non|tot|plan|qualques|pau|aute|un|dus|tres|quatre|cinc|gran|long|larg|espés|pesuc|petit|cort|estret|prim|hemna|òme|persona|mainatge|molhèr|marit|mair|pair|animau|peish|aucèth|can|piolh|sèrp|vèrm|arbre|bòsc|baston|frut|gran|huelha|arrel|escòrça|flor|èrba|còrda|pèth|carn|sang|òs|grèish|uòu|còrn|coa|pluma|pèth|cap|auretha|uelh|nas|boca|dent|lenga|ongla|pè|cama|genolh|man|ala|ventre|tripas|còth|esquia|pitre|còr|gessèr|béver|minjar|mossegar|chucar|escopir|vomir|bufar|respirar|ríser|véder|ausir|saber|pensar|sentir|témer|dormir|víver|morir|tuar|luchar|caçar|tustar|talhar|héner|apunhalar|gratar|cavar|nadar|volar|caminar|víner|jaser|séder|estar|virar|cáder|dar|téner|prémer|fregar|lavar|eishugar|tirar|empénher|lançar|ligar|cósèr|comptar|díser|cantar|jugar|flotar|fluir|gelar|enflar|sorelh|lua|estela|aiga|pluja|arriu|lac|mar|sau|pèira|sabla|polvera|tèrra|nívol|bruma|cèu|vent|nèu|glaç|hum|huec|cendre|cremar|camin|montanha|roge|verd|jaune|blanc|negre|nueit|dia|an|caud|hred|plen|nau|vièlh|bon|marrit|porrit|salop|dret|redond|agut|emós|lis|molhat|sec|corrècte|près|lhen|dreta|esquèrra|a|en|damb|e|se|perqué|nom|eth|èster|gat|gata|canha|sorrisèr")

# Eastern / isolate / Latin
_EXT = _pack("ext", "yu|tú|él|nosotrus|vosotros|ellus|esti|esi|aquí|allí|quíen|qué|ondi|cuandu|cómmu|nu|tó|muchus|argunus|pocos|otru|un|dos|tres|cuatru|cincu|grandi|largu|anchu|gruesu|pesau|chiquinu|curtu|estrechu|finu|mujel|hombri|persona|niñu|esposa|esposu|mairi|pairi|animal|pez|páxaru|perru|pioju|culebra|gusanu|árbol|bosqui|palu|fruta|simienti|oja|raís|corteza|flor|yerba|cuerda|piel|carni|sangri|huesu|grasa|güevu|cuernu|cola|pluma|pelu|cabeza|oreja|oju|narís|boca|dienti|lengua|uña|pie|pierna|roilla|manu|ala|vientri|tripas|cuellu|espalda|pechu|corazón|hígado|bebel|comel|mordel|chupal|escupil|vomital|soplal|respiral|reíl|vel|oíl|sabel|pensal|olel|temel|dormil|vivil|moríl|matal|luchal|cazal|golpeal|cortal|fendel|apuñalal|rascal|caval|nadal|volal|caminal|venil|jacel|sental|estal|giral|cael|dal|tenel|apretal|fregal|laval|enxugal|tiral|empujal|lanzal|atal|cosel|contal|dicil|cantal|jugal|flotal|fluil|helal|inchal|sol|luna|estrella|água|luvia|ríu|lagu|mar|sal|piedra|arena|polvu|tierra|nubi|niebla|cielu|vientu|nievi|helu|humu|huegu|ceniza|quemal|caminu|montaña|colorau|verdi|amarillu|blancu|negru|nochi|día|añu|calienti|fríu|lenu|nuevu|vieju|güenu|malu|podri|suciu|retu|redondu|afiaú|romu|lisu|mojau|secu|correctu|cerca|lejos|derecha|izquierda|a|en|con|y|si|porque|nombril|el|sel|gatu|gata|perra|sonreíl")

_LA = _pack("la", "ego|tu|is|nos|vos|ei|hic|ille|hic|illic|quis|quid|ubi|quando|quomodo|non|omnis|multi|aliqui|pauci|alius|unus|duo|tres|quattuor|quinque|magnus|longus|latus|crassus|gravis|parvus|brevis|angustus|tenuis|femina|vir|homo|puer|uxor|maritus|mater|pater|animal|piscis|avis|canis|pediculus|serpens|vermis|arbor|silva|baculum|fructus|semen|folium|radix|cortex|flos|herba|funis|cutis|caro|sanguis|os|adeps|ovum|cornu|cauda|pluma|capillus|caput|auris|oculus|nasus|os|dens|lingua|unguis|pes|crus|genu|manus|ala|venter|viscera|collum|dorsum|pectus|cor|iecur|bibere|edere|mordere|sugere|spuere|vomere|flare|spirare|ridere|videre|audire|scire|cogitare|olfacere|timere|dormire|vivere|mori|occidere|pugnare|venari|ferire|secare|findere|confodere|scalpere|fodere|natare|volare|ambulare|venire|iacere|sedere|stare|vertere|cadere|dare|tenere|premere|fricare|lavare|tergere|trahere|pellere|iacere|ligare|suere|numerare|dicere|cantare|ludere|fluitare|fluere|gelare|tumescere|sol|luna|stella|aqua|pluvia|flumen|lacus|mare|sal|lapis|arena|pulvis|terra|nubes|nebula|caelum|ventus|nix|glacies|fumus|ignis|cinis|urere|via|mons|ruber|viridis|flavus|albus|niger|nox|dies|annus|calidus|frigidus|plenus|novus|vetus|bonus|malus|putridus|sordidus|rectus|rotundus|acer|hebes|levis|umidus|siccus|rectus|prope|procul|dextra|sinistra|ad|in|cum|et|si|quia|nomen|ille|esse|cattus|catta|canis|ridere")

_RM = _pack("rm", "jau|ti|el|nus|vus|els|quest|quel|qua|là|tgi|tge|nua|cura|co|betg|tut|blera|tscherts|paucs|auter|in|dus|trais|quater|tschun|grond|lung|lartg|grass|grev|pitg|curt|stretg|fin|dunna|um|persuna|uffant|dunna|umer|mamma|bab|animal|pesch|utschel|chaun|lidom|serp|vierm|ischi|guaud|bastun|fritg|sem|fegl|ragisch|scorsa|flur|erva|corda|pel|carn|sonc|ies|grass|ov|corn|guauda|plima|chavels|tgau|ureglia|egl|nas|bucca|dent|lingua|ungla|pe|comba|schanugl|maun|ala|venter|budels|culiez| uns|peiz|cor|gnirom|baiver|magliar|morder|sitschar|sputar|vomitar|suffers|respirar|rir|vesair|udir|saveir|pensar|sentir|temer|durmir|viver|murir|maffar|cumbatter|chatschar|batter|tagliar|spartir|pugnalar|grattar|chavar|nadar|volar|ir|vegnir|giacer|seser|star|voltar|cader|dar|tegner|smitgar|fritgar|lavar|sitgar|tirar|spinger|bittar|liar|cuser|contar|dir|cantar|giugar|flottar|sgular|gelar|unflar|sulegl|glina|staila|aua|plievgia|flum|lai|mar|sal|crap|sablun|polvra|terra|niv|nebla|tschiel|vent|naiv|glatsch|fum|fieu|tschendra|arder|via|muntogna|cotschen|verd|mellen|alv|nair|notg|di|onn|cauld|freid|plen|nov|vegl|bun|mal|marscha|suid|dretg|rund|spitg|stus|glisch|umid|sitg|correct|datiers|lunsch|dretga|sanestra|a|en|cun|e|sche|perquai|num|il|esser|gat|gata|chauna|smilegiar")

_SC = _pack("sc", "deo|tue|isse|nois|bois|issos|custu|cussu|inoghe|inie|chie|ite|inue|cando|comente|no|totu|medas|unos|pagos|ateru|unu|duos|tres|battor|chimbe|mannu|longu|largu|grussu|pesante|pitzinnu|curtzu|istrintu|finu|femina|omine|persone|pitzinnu|muzere|maridu|mama|babbu|animale|pische|puzone|cane|pioddu|serpe|rime|arbore|padente|palu|frutu|semene|fozza|raizina|iscorza|fiore|erba|fune|pedde|petta|sambene|ossu|grassu|ou|corru|coa|pinna|pilos|conca|origra|ogu|nasu|buca|dente|limba|unga|pe|anca|genugru|manu|ala|ventre|budellos|collu|spatas|pettu|coro|figadu|bier|mandicare|mòrdere|sutzare|isputare|vomitare|bufare|respirare|rìdere|bìdere|intèndere|ischire|pensare|sentire|tìmere|dormire|bìvere|mòrrere|ochìere|cumbattere|cassare|gòlghere|segare|findere|apunzare|carrigare|cavare|nadare|volare|caminare|bènnere|gjacare|sèdere|istare|girare|rùere|dare|tènnere|stringhere|fregare|lavare|sichire|tirare|ispìnghere|ghetare|ligare|cosire|contare|nàrrere|cantare|giogare|galleggiare|còrrere|gelare|gonfiare|sole|luna|isteddu|abba|proida|riumine|lagu|mare|sale|perda|rena|prùere|terra|nue|neula|chelu|bentu|nie|ghiacciu|fumo|foco|chinisa|brujare|via|montagna|ruju|birde|grogu|albu|nieddu|note|die|annu|caldu|fritu|prenu|nou|betzu|bonu|malu|pùtidu|làdu|deretu|tundu|aghudu|otusu|lisciu|mudu|sicu|giustu|achèdda|atèsu|dereta|manca|a|in|chin|e|si|ca|nùmene|su|èssere|gatu|gata|cana|sorrìere")

_RUP = _pack("rup", "eu|tine|năs|noi|voi|năsh|aistu|atsel|aoa|aclo|tsine|tse|iu|cându|cum|nu|tut|multsă|niscăts|putsăni|altu|un|doi|trei|patru|tsintsi|mari|lungu|largu|greasu|greu|njic|scurtu|strimtu|sutil|muljari|bărbat|persoană|ficior|sotsă|sot|mamă|tată|animal|pesku|pulj|căni|piduclju|sharpi|viermi|arburi|păduri|băts|fructu|sămintsă|frândză|rădătsină|scoarță|floari|earbă|frânghie|cheali|carni|sândzi|os|grăsimi|ou|cornu|coadă|peană|per|cap|ureaclji|oaclji|nari|gură|dinti|limbă|unghie|cicior|cicior|genuchi|mână|aripă|burtă|măruntaie|gushi|spati|sân|inimă|hicat|beau|măc|muscu|sug|scuip|vomit|suflu|respiru|râdu|ved|avdu|shtiu|gândescu|mirosescu|mi-e frică|dormu|trăescu|mor|ucid|luptu|avănescu|lovescu|talji|despic|înjunghii|zgârii|sap|înot|zbor|umblu|yin|zac|shed|stau|întorcu|cad|dau|tsăn|strângu|frec|spel|shterg|trag|impingu|arunc|leg|cos|număr|zic|cântu|gioc|plutescu|curgu|înghets|umflu|soari|lună|steauă|apă|ploai|arâu|lac|amari|sari|cheatră|nisip|praf|loc|nor|ceatsă|tser|vîntu|neauă|gheatsă|fum|foc|tseanushă|ard|cale|munti|arosh|veardi|galbin|albu|negru|noapti|dzuă|an|cald|aratsi|plin|nau|veclju|bun|arău|putred|murdar|ndreptu|rotund|ascutsit|tutsea|neted|ud|uscat|ndreptu|aproape|diparti|ndreapta|stânga|la|tu|cu|shi|ma|tră|numă|lu|hii|pisică|pisică|cătea|zâmbeascâ")

# Attested cells only; filled below from RUO_WIKT_SWADESH and RUO_WIKT_ENTRIES.
# The Daco-Romanian list that used to pad this column is gone.
_RUO = _hits("ruo", {})

# Wiktionary's Dalmatian Swadesh list, plus forms its Dalmatian entries gloss with
# the concept. Invented and respelled forms are gone.
# Cell by cell: docs/eval/grid_sources.md.
_DLM = _hits("dlm", {
    "i": "ju", "you_sg": "te", "he": "jal", "we": "nu", "you_pl": "voi", "they": "jali",
    "this": "cost", "that": "col", "here": "kauk", "there": "luk", "who": "ci", "what": "co",
    "where": "jo", "when": "cand", "how": "kal", "not": "na", "all": "tot", "many": "mult",
    "some": "certioin", "other": "jultro", "one": "ioin", "two": "doi", "three": "tra",
    "four": "quater", "five": "cionco", "big": "maur", "long": "luang", "wide": "luarg",
    "thick": "dais", "heavy": "pesunt", "small": "pedlo", "short": "kort", "woman": "dona",
    "man": "jomno", "person": "jomno", "child": "kratoir", "wife": "mulier", "husband": "marait",
    "mother": "njena", "father": "tuota", "animal": "biastia", "fish": "pasc", "bird": "paserain",
    "dog": "cun", "louse": "pedoklo", "snake": "serpiant", "worm": "viarm", "tree": "iuarbol",
    "forest": "buask", "stick": "stal", "fruit": "froit", "seed": "grun", "leaf": "fualja",
    "root": "radaica", "bark": "dermun", "flower": "fiaur", "grass": "iarba", "rope": "kanapial",
    "skin": "pial", "meat": "cuarne", "blood": "suang", "bone": "vuas", "fat": "gruas",
    "egg": "juv", "horn": "cuarno", "tail": "cauda", "feather": "paina", "hair": "pail",
    "head": "cup", "ear": "oracla", "eye": "uaclo", "nose": "nuos", "mouth": "buca",
    "tooth": "diant", "tongue": "langa", "fingernail": "jongla", "foot": "pi", "leg": "guonb",
    "knee": "denaklo", "hand": "mun", "wing": "jal", "belly": "viantro", "guts": "alaite",
    "neck": "cual", "back": "duas", "breast": "tat", "heart": "cur", "liver": "fecuat",
    "drink": "bar", "eat": "mancur", "bite": "moscuar", "suck": "zupigur", "spit": "spoit",
    "vomit": "gomituor", "blow": "sublar", "breathe": "fiutar", "laugh": "redro", "see": "vedar",
    "hear": "senter", "know": "sapar", "think": "piansar", "smell": "tufuor", "fear": "taimo",
    "sleep": "dormer", "live": "vivar", "die": "morer", "kill": "masuor", "fight": "cuombatter",
    "hunt": "capur", "hit": "botur", "cut": "taljur", "split": "spartar", "scratch": "gratuar",
    "dig": "pasnur", "fly": "svolur", "walk": "kaminur", "come": "venir", "sit": "sentur",
    "stand": "stur", "fall": "kadar", "give": "duor", "hold": "tenar", "squeeze": "shtrengar",
    "rub": "jongar", "wash": "lavuar", "pull": "strasinur", "throw": "truar", "tie": "liguar",
    "sew": "koser", "count": "embruar", "say": "dekro", "sing": "kantur", "play": "jukur",
    "freeze": "glazir", "sun": "saul", "moon": "loina", "star": "stala", "water": "aqua",
    "rain": "pluaia", "river": "floim", "lake": "lak", "sea": "mur", "salt": "suol",
    "stone": "pitra", "sand": "sablaun", "dust": "pulvro", "earth": "tiara", "cloud": "neo",
    "sky": "cil", "wind": "viant", "snow": "nai", "ice": "glas", "fire": "fuc", "ash": "kanaisa",
    "burn": "ardar", "road": "kale", "mountain": "muant", "red": "ros", "green": "vert",
    "yellow": "zuola", "white": "blanc", "black": "fosc", "night": "nuot", "day": "dai",
    "year": "jan", "warm": "cuald", "cold": "gelut", "full": "plain", "new": "nuf", "old": "vieclo",
    "good": "bun", "bad": "ri", "rotten": "muas", "dirty": "spuarc", "straight": "drat",
    "wet": "joit", "dry": "sak", "correct": "drat", "near": "alic", "far": "distuont",
    "right": "diastro", "left": "zuonca", "at": "a", "in": "in", "with": "kon", "and": "e",
    "if": "se", "because": "perko", "name": "naum", "def_art": "el", "cat": "cuot",
})

# Corsican: Appendix:Corsican_Swadesh_list first {{l|co|…}}; empty cells from Sicilian sister.
_CO = _pack("co", "eiu|tù|ellu|noi|voi|elli|questu|quellu|ccà|ci|chì|chè|duva|quandu|cumu|ùn|tuttu|assai|arcuni|picca|altru|unu|dui|trè|quattru|cinque|grande|lungu|largu|spessu|pesantu|picculu|cortu|strettu|magru|donna|omu|parsona|picciriddu|sposu|maritu|mamma|patri|animale|pesciu|ucellu|cani|pidocchiu|serpì|vermu|alberu|boscu|mazzu|fruttu|simenza|fodda|radica|scorcia|fiori|arba|corda|peddi|carni|sangui|ossu|grassu|ovu|cornu|coda|penna|capellu|testa|ricchia|ochju|nasu|bucca|denti|lingua|ugna|pedi|ghjamba|ghjinochju|mani|ala|ventre|budella|collu|spinu|pettu|cori|fegatu|bia|manghjà|mursicà|suchjà|stupà|vòmmiri|suffià|rispirari|rida|veda|senta|sapè|pinsà|annasà|teme|dorma|viva|mora|tumbà|cummàttiri|cacciari|batta|tonda|sparta|pugnialari|sgrinfià|cavari|nutà|vulari|marchjà|vena|chjinà|pasà|alzà|ghjirà|cascà|dà|tena|strìnciri|frìcari|lavà|asciucari|tirà|spìnciri|ghjittà|ligari|cusgà|cuntà|dì|cantà|ghjucà|galleggiri|scùrriri|gilari|gunfià|soli|luna|stella|acqua|pioghja|fiume|lagu|mari|sale|petra|rena|pruvulazzu|terra|nivulu|nebbia|celu|ventu|nevi|ghiacciu|fumu|focu|cinniri|brusgià|strata|monti|rossu|verdi|giaddu|albu|neru|notti|ghjornu|annu|caldu|fritu|chinu|novu|vechju|bonu|malu|marciu|sporcu|drittu|ritondu|affilatu|smussatu|lisciu|bagnatu|asciuttu|currettu|vicinu|lontanu|diritta|manca|à|in|cù|è|si|parchì|nomi|u|esse|ghjattu|ghjatta|cagna|surrisu")

# Megleno-Romanian: Appendix:Megleno-Romanian Swadesh list; empty cells from Aromanian.
_RUQ = _pack("ruq", "io|tu|iel|noi|voi|ieľ|tsist|tsel|ua|colo|cola|tse|iundi|cǫn|cum|nu|tot|muľts|niști|uneac|altu|un|doi|trei|patru|tsints|mari|lung|larg|gros|greu|mic|scurtu|strimt|subtzǫri|muľari|bărbat|uom|cupilaș|niveastă|bărbat|mamă|tată|animal|peaști|pulj|cǫini|piducľu|şarpi|ghermi|arbur|păduri|virdzeauă|plod|siminţă|frunză|corin|scoarță|floari|iarbă|funi|coajă|carni|sǫnzi|uos|grăsimi|uou|corn|coadă|peană|per|cap|ureacľă|uocľu|nas|gură|dinti|limbă|ungľă|pitšor|pitšor|zinucľu|mǫnă|iaripă|buric|matsi|gușă|gorb|chiept|ińamă|drob|beai|mănǫnc|muscu|sug|scup|vom|suflu|respiru|rǫd|ved|ud|știu|misles|miruses|ạnfric|dorm|trăies|mor|nec|bat|luves|ugudes|taľ|dispic|pung|zgair|sap|plivăies|părăies|amnu|vin|culc|șǫd|stau|ạnvărtes|cad|dau|tsǫn|string|frec|spel|șterg|trag|impingu|runc|leg|cos|numir|spun|cǫnt|joc|plivăies|cur|ạngľets|anflu|soari|lună|steauă|apu|ploaiă|vali|lac|mari|sari|rǫpă|pisoc|prau|pimint|nor|ceatsă|tser|vint|neauă|gľets|fum|foc|tșănușă|ardu|cåle|munti|roș|veardi|galbin|alb|negru|noapti|zuuă|an|cald|ratsi|ạmplin|nou|vecľu|bun|rǫu|putrid|murdar|ndreptu|gurguľat|tăľătos|tutsea|neted|vlajnic|uscat|ndreptu|prochiat|diparti|dirept|stǫng|la|ăn|cu|și|acu|că|numi|u|es|pisică|pisică|cătea|zâmbeascâ")

# Romagnol: Module:Swadesh/data/rgn (ìa, ti) + Kaikki unique glosses; other cells Emilian continuum.
_RGN = _pack("rgn", "ìa|ti|ló|nó|vó|låur|st|quèll|qué|lé|chi|che|dóvv|quand|come|an|tótt|tant|socuànt|pôc|èter|ón|du|trî|cvàtar|zénc|grãnd|lóng|lèrg|féss|paiṡ|znén|cûrt|stratt|alẓir|dòna|òmen|parsåṅna|babén|mujêr|marè|mèder|pê|animêl|pass|ușël|can|bdòcc|sarpänt|virman|âlber|furèsta|bastån|frûta|smänt|fója|radîṡ|scôrza|fiåur|érba|côrda|pèl|chêrna|sângv|òs|gras|öv|côrna|cô|panna|capèl|tèsta|uraccia|òc|nèṡ|båcca|dänt|längua|ónngia|pà|ganba|żnòc|man|èglia|panza|intestén|cöl|schéṅna|pèt|côr|fégghet|bàvver|magnèr|muṡghèr|sucèr|spudèr|trèr|supièr|respirèr|rédder|vàdder|sénter|savair|pinsèr|naṡèr|tamma|durmîr|stèr|murîr|amazèr|cunbâter|cazièr|culpîr|tajèr|divîder|pugnalèr|ṡgranfgnèr|scavèr|nudèr|vulèr|andèr|vgnîr|dstànndres|sêder|stèr|prilèr|caschèr|dèr|tgnîr|scuizèr|sfarghèr|lavèr|asughèr|tirèr|spénnżer|trèr|lighèr|cûṡer|cõnt|dîr|cantèr|żughèr|galegèr|pasèr|żlèr|gunfièr|sól|lóṅna|strèla|acva|piôva|fiũ|lèg|mêr|sêl|sâs|sâbia|pållver|tèra|nóvvla|nabbia|zîl|vänt|naiv|giâz|fọmm|fûg|zànnder|bruṡèr|strè|muntâgna|råss|vérd|ẓal|biânc|naigher|nòt|dè|ân|chèld|fradd|pi|nôv|vèc|bôn|catîv|mèrz|malnàtt|drétt|tånnd|afilê|ṡmusè|léss|mói|sècc|giósst|avṡén|luntàn|drétta|stanca|a|in|con|e|se|parché|nómm|e|èser|gàt|gàta|càgna|surrìder")


# Corsican: first citation form from Appendix:Corsican Swadesh list.
# Empty = appendix blank (no Italian pad).
_CO = _hits("co", {
    "i": "eiu", "you_sg": "tù", "he": "ellu", "we": "noi", "you_pl": "voi",
    "they": "elli", "this": "questu", "that": "quellu", "there": "ci",
    "who": "chì", "what": "chè", "where": "duva", "when": "quandu",
    "how": "cumu", "not": "ùn", "all": "tuttu", "other": "altru",
    "one": "unu", "two": "dui", "three": "trè", "four": "quattru",
    "five": "cinque", "big": "grande", "long": "lungu", "wide": "largu",
    "thick": "spessu", "heavy": "pesantu", "small": "picculu", "short": "cortu",
    "narrow": "strettu", "thin": "magru", "woman": "donna", "man": "omu",
    "person": "parsona", "child": "zitellu", "wife": "sposa", "husband": "maritu",
    "mother": "mamma", "father": "babbu", "animal": "animale", "fish": "pesciu",
    "bird": "ucellu", "dog": "cani", "worm": "vermu", "tree": "alberu",
    "forest": "boscu", "fruit": "fruttu", "leaf": "foglia", "root": "radica",
    "flower": "fiore", "grass": "erba", "rope": "corda", "skin": "pelle",
    "meat": "carne", "blood": "sangue", "bone": "ossu", "fat": "grassu",
    "tail": "coda", "feather": "penna", "hair": "capellu", "head": "testa",
    "eye": "ochju", "nose": "nasu", "mouth": "bocca", "tooth": "dente",
    "tongue": "lingua", "fingernail": "unghja", "foot": "pede", "leg": "ghjamba",
    "knee": "ghjinochju", "hand": "manu", "wing": "ala", "belly": "ventre",
    "neck": "collu", "back": "spinu", "breast": "pettu", "heart": "core",
    "liver": "fegatu", "drink": "beie", "eat": "manghjà", "bite": "mursicà",
    "suck": "suchjà", "spit": "stupà", "blow": "suffià", "laugh": "ride",
    "see": "vede", "hear": "sente", "know": "sapè", "think": "pinsà",
    "smell": "annasà", "sleep": "dorme", "live": "vive", "die": "more",
    "kill": "tumbà", "hit": "batte", "cut": "tonde", "split": "sparte",
    "scratch": "sgrinfià", "swim": "nutà", "walk": "marchjà", "come": "vene",
    "lie": "chjinà", "sit": "pusà", "stand": "alzà", "turn": "ghjirà",
    "fall": "cascà", "give": "dà", "hold": "tene", "wash": "lavà",
    "pull": "tirà", "throw": "ghjittà", "sew": "cusgà", "count": "cuntà",
    "say": "dì", "sing": "cantà", "play": "ghjucà", "swell": "gunfià",
    "sun": "sole", "moon": "luna", "star": "stella", "water": "acqua",
    "rain": "pioghja", "river": "fiume", "lake": "lagu", "sea": "mare",
    "salt": "sale", "stone": "petra", "earth": "terra", "cloud": "nulu",
    "sky": "celu", "wind": "ventu", "snow": "neve", "smoke": "fumu",
    "fire": "focu", "burn": "brusgià", "mountain": "monte", "red": "rossu",
    "green": "verde", "yellow": "giallu", "white": "biancu", "black": "neru",
    "night": "notte", "day": "ghjornu", "year": "annu", "warm": "caldu",
    "cold": "freddu", "new": "novu", "old": "vechju", "good": "bonu",
    "bad": "malu", "rotten": "marciu", "dirty": "sporcu", "straight": "drittu",
    "round": "rotondu", "sharp": "affilatu", "dull": "smussatu",
    "smooth": "lisciu", "wet": "bagnatu", "dry": "asciuttu",
    "correct": "ghjustu", "near": "vicinu", "far": "lontanu",
    "right": "dritta", "left": "manca", "at": "à", "in": "in", "with": "cù",
    "and": "è", "because": "perchì", "name": "nome",
})

# Romagnol: Kaikki exact-gloss hits only (rgn_words.json). No Emilian pad.
_RGN = _hits("rgn", {
    "he": "lò", "this": "ste", "that": "quèll", "one": "un", "two": "du",
    "three": "tri", "four": "cvàtar", "big": "grãnd", "long": "lóng",
    "small": "znén", "thin": "alẓir", "woman": "dòna", "man": "òm",
    "child": "babén", "wife": "mój", "husband": "marè", "father": "pê",
    "animal": "animêl", "bird": "uşël", "dog": "cân", "louse": "bdòcc",
    "worm": "virman", "forest": "sélva", "leaf": "fója", "root": "radìșa",
    "flower": "fiôr", "grass": "érba", "skin": "pël", "meat": "chêrna",
    "blood": "sângv", "fat": "gras", "egg": "öv", "tail": "côda",
    "hair": "cavèl", "eye": "òcc", "tooth": "dént", "foot": "pè",
    "hand": "mân", "neck": "cöl", "back": "schéna", "heart": "côr",
    "drink": "bé", "sleep": "durmì", "fall": "cadér", "wash": "lavêr",
    "tie": "lighêr", "say": "dì", "float": "galegêr", "sun": "sól",
    "rain": "piùva", "river": "fiũ", "sand": "sàbia", "sky": "cil",
    "wind": "vènt", "snow": "név", "smoke": "fọmm", "fire": "fóg",
    "ash": "zéndra", "red": "ròss", "green": "vérd", "yellow": "ẓal",
    "white": "biânc", "black": "négar", "night": "nòt", "day": "dè",
    "year": "ân", "full": "pi", "new": "nóv", "good": "bôn",
    "bad": "cativ", "straight": "drèt", "sharp": "afilê", "dry": "sècc",
    "in": "in", "if": "se", "name": "nóm", "def_art": "l'", "copula": "èssér",
})

# Megleno-Romanian: Appendix:Megleno-Romanian Swadesh list, first form.
# who: appendix duplicated "there"; use cari (ro.wiki / qualis).
_RUQ = _hits("ruq", {
    "i": "io", "you_sg": "tu", "he": "iel", "we": "noi", "you_pl": "voi",
    "they": "ielj", "this": "tsist", "that": "tsel", "here": "ua",
    "there": "colo", "who": "cari", "what": "tse", "where": "iundi",
    "when": "con", "how": "cum", "not": "nu", "all": "tot", "many": "mults",
    "some": "nisti", "few": "uneac", "other": "altu", "one": "un",
    "two": "doi", "three": "trei", "four": "patru", "five": "tsints",
    "big": "mari", "long": "lung", "wide": "larg", "thick": "gros",
    "heavy": "greu", "small": "mic", "narrow": "strimt", "thin": "subtzeri",
    "woman": "muljari", "man": "barbat", "person": "uom", "child": "fitsor",
    "wife": "niveasta", "husband": "barbat", "mother": "mama", "father": "tata",
    "fish": "peasti", "dog": "coini", "louse": "piduclju", "snake": "sarpi",
    "worm": "ghermi", "tree": "arbur", "forest": "paduri", "stick": "virdzeaua",
    "fruit": "plod", "seed": "siminta", "leaf": "frunza", "root": "corin",
    "flower": "floari", "grass": "iarba", "rope": "funi", "skin": "coaja",
    "meat": "carni", "blood": "sonzi", "bone": "uos", "fat": "grasimi",
    "egg": "uou", "horn": "corn", "tail": "coada", "feather": "peana",
    "hair": "per", "head": "cap", "ear": "ureaclja", "eye": "uoclju",
    "nose": "nas", "mouth": "gura", "tooth": "dinti", "tongue": "limba",
    "fingernail": "unglja", "foot": "pitsor", "leg": "pitsor",
    "knee": "zinuclju", "hand": "mona", "wing": "aripa", "belly": "foali",
    "guts": "matsi", "neck": "gusa", "back": "gorb", "breast": "chiept",
    "heart": "inama", "liver": "drob", "drink": "beai", "eat": "manonc",
    "suck": "sug", "spit": "scup", "vomit": "vom", "blow": "suflu",
    "laugh": "rod", "see": "ved", "hear": "ud", "know": "stiu",
    "think": "misles", "smell": "miruses", "fear": "anfric", "sleep": "dorm",
    "live": "traies", "die": "mor", "kill": "nec", "fight": "bat",
    "hunt": "luves", "hit": "ugudes", "cut": "talj", "split": "dispic",
    "stab": "pung", "scratch": "zgair", "dig": "sap", "swim": "plivaies",
    "fly": "paraies", "walk": "amnu", "come": "vin", "lie": "culc",
    "sit": "sod", "stand": "stau", "turn": "anvartes", "fall": "cad",
    "give": "dau", "hold": "tson", "squeeze": "string", "rub": "frec",
    "wash": "spel", "wipe": "sterg", "pull": "trag", "throw": "runc",
    "tie": "leg", "sew": "cos", "count": "numir", "say": "spun",
    "sing": "cont", "play": "joc", "float": "plivaies", "flow": "cur",
    "freeze": "anglets", "swell": "anflu", "sun": "soari", "moon": "luna",
    "star": "steaua", "water": "apu", "rain": "ploia", "river": "vali",
    "lake": "lac", "sea": "mari", "salt": "sari", "stone": "ropa",
    "sand": "pisoc", "dust": "prau", "earth": "pimint", "cloud": "nor",
    "sky": "tser", "wind": "vint", "snow": "neaua", "ice": "glets",
    "smoke": "fum", "fire": "foc", "ash": "tsanusa", "burn": "ardu",
    "road": "drum", "mountain": "munti", "red": "ros", "green": "veardi",
    "yellow": "galbin", "white": "alb", "black": "negru", "night": "noapti",
    "day": "zuua", "year": "an", "warm": "cald", "cold": "ratsi",
    "full": "amplin", "new": "nou", "old": "veclju", "good": "bun",
    "bad": "rou", "rotten": "putrid", "dirty": "murdar",
    "round": "gurguljat", "sharp": "taljatos", "wet": "vlajnic",
    "dry": "uscat", "near": "proapi", "far": "diparti", "right": "dirept",
    "left": "stong", "at": "la", "in": "an", "with": "cu", "and": "si",
    "if": "acu", "because": "ca", "name": "numi",
})

TABLES: dict[str, dict[str, str]] = {
    # Ibero (es/pt/gl live in romance_swadesh._ROWS / _EXTRA)
    "an": _AN, "ast": _AST, "ext": _EXT, "lad": _LAD, "mwl": _MWL,
    # Occitano / Oil / Arpitan
    "gsc": _GSC, "wa": _WA, "pcd": _PCD, "nrf": _NRF, "gallo": _GALLO, "frp": _FRP,
    # Gallo-Italian
    "lmo": _LMO, "pms": _PMS, "lij": _LIJ, "eml": _EML, "rgn": _RGN,
    # Italo-Dalmatian
    "scn": _SCN, "vec": _VEC, "co": _CO, "ist": _IST, "dlm": _DLM,
    # Rhaeto / Sardinian / Eastern
    "rm": _RM, "fur": _FUR, "lld": _LLD, "sc": _SC,
    "rup": _RUP, "ruo": _RUO, "ruq": _RUQ,
}

# ASJP 40-item ROMANIAN_MEGLENO (Capidan via ASJP v21).
# Most cells already match the appendix; path is the extra Capidan item.
TABLES["ruq"].update({"road": "drum"})

# Appendix:Istro-Romanian Swadesh list (en.wiktionary). First citation form.
# blood: user sănze (appendix sânže). Empty appendix cells stay empty.
RUO_WIKT_SWADESH = {
    "i": "jo",
    "you_sg": "tu",
    "he": "je",
    "we": "noj",
    "you_pl": "voj",
    "they": "jelj",
    "this": "sta",
    "that": "čela",
    "there": "kolo",
    "who": "čire",
    "what": "če",
    "where": "juvę",
    "when": "kân",
    "how": "kum",
    "not": "nu",
    "all": "tot",
    "many": "čudę",
    "other": "åt",
    "one": "ur",
    "two": "doj",
    "three": "trej",
    "four": "påtru",
    "five": "činč",
    "big": "måre",
    "long": "lung",
    "heavy": "grev",
    "small": "mik",
    "short": "skurt",
    "woman": "muljęre",
    "man": "om",
    "person": "om",
    "child": "fečor",
    "wife": "muljęre",
    "husband": "om",
    "mother": "måje",
    "father": "čåče",
    "fish": "ribę",
    "bird": "pulj",
    "dog": "kâre",
    "louse": "peduklju",
    "snake": "šerp",
    "worm": "ljermu",
    "tree": "stâblę",
    "forest": "boškę",
    "fruit": "frut",
    "leaf": "folje",
    "grass": "jårbę",
    "skin": "kože",
    "meat": "kårne",
    "blood": "sănze",
    "bone": "os",
    "egg": "ov",
    "hair": "per",
    "head": "kåp",
    "ear": "uręklje",
    "eye": "oklju",
    "nose": "nås",
    "mouth": "gurę",
    "tooth": "dint",
    "tongue": "limbę",
    "foot": "pičor",
    "leg": "pičor",
    "knee": "žerunklju",
    "hand": "mâr",
    "wing": "krelutę",
    "belly": "târbuh",
    "neck": "čerbiče",
    "back": "spåte",
    "breast": "kljept",
    "heart": "jirimę",
    "drink": "bę",
    "eat": "mâncå",
    "blow": "suflå",
    "see": "vedę",
    "hear": "åvzi",
    "know": "šti",
    "think": "misli",
    "sleep": "durmi",
    "live": "živi",
    "die": "muri",
    "kill": "učide",
    "fight": "båte",
    "hunt": "lovi",
    "cut": "taljå",
    "walk": "âmnå",
    "come": "veri",
    "sit": "šedę",
    "stand": "stå",
    "turn": "turnå",
    "fall": "kadę",
    "give": "då",
    "say": "spure",
    "sing": "kântå",
    "play": "igręj",
    "sun": "sore",
    "moon": "lurę",
    "star": "stę",
    "water": "åpę",
    "rain": "ploje",
    "river": "potok",
    "sea": "måre",
    "salt": "såre",
    "stone": "ârpę",
    "earth": "pemint",
    "sky": "čer",
    "wind": "vint",
    "snow": "nę",
    "ice": "gljåcę",
    "fire": "fok",
    "ash": "čeruše",
    "burn": "årde",
    "road": "kåle",
    "mountain": "kodru",
    "red": "rojšu",
    "green": "zelen",
    "yellow": "žut",
    "white": "åb",
    "black": "negru",
    "night": "nopte",
    "day": "zi",
    "year": "ån",
    "warm": "kåd",
    "cold": "råče",
    "full": "pljir",
    "new": "nov",
    "old": "betâr",
    "good": "bur",
    "bad": "ręv",
    "dirty": "spork",
    "straight": "drit",
    "round": "tond",
    "wet": "ud",
    "near": "prope",
    "at": "la",
    "in": "ân",
    "with": "ku",
    "and": "ši",
    "if": "se",
    "because": "ke",
    "name": "lume",
}
TABLES["ruo"].update(RUO_WIKT_SWADESH)

# Cells the appendix leaves empty, attested elsewhere on Wiktionary with the
# sense. Each is traced in docs/sources_ruo.md.
RUO_WIKT_ENTRIES = {
    "thick": "gros",        # lemma entry, adjective "thick"
    "bite": "mučcå",        # translation under "bite"; also Saenko
    "hold": "țire",         # translation under "hold" (spelled ţire there)
    "hit": "båte",          # translation under "beat", sense "to hit"
    "copula": "fi",         # translation under "be"; fr.wiktionary entry
}
TABLES["ruo"].update(RUO_WIKT_ENTRIES)

# Saenko 2015, Istro-Romanian, in the spelling of his sources (the acute
# marks stress). Traced in docs/sources_ruo.md.
RUO_SAENKO = {
    "seed": "semínțę", "root": "córen", "bark": "córa", "fat": "måst", "horn": "corn",
    "tail": "códę", "feather": "pęna", "fingernail": "úngľe", "liver": "ficåț", "swim": "pliví",
    "fly": "letí", "lie": "začå", "sand": "salbún", "cloud": "oblåc", "smoke": "dim",
    "dry": "uscåt", "far": "lårgo", "thin": "supțíre",
}
TABLES["ruo"].update(RUO_SAENKO)


# Not a source. Same 213 rows, parked for a later English-as-source run.
_EN = _pack("en", "I|you|he|we|you|they|this|that|here|there|who|what|where|when|how|not|all|many|some|few|other|one|two|three|four|five|big|long|wide|thick|heavy|small|short|narrow|thin|woman|man|person|child|wife|husband|mother|father|animal|fish|bird|dog|louse|snake|worm|tree|forest|stick|fruit|seed|leaf|root|bark|flower|grass|rope|skin|meat|blood|bone|fat|egg|horn|tail|feather|hair|head|ear|eye|nose|mouth|tooth|tongue|fingernail|foot|leg|knee|hand|wing|belly|guts|neck|back|breast|heart|liver|drink|eat|bite|suck|spit|vomit|blow|breathe|laugh|see|hear|know|think|smell|fear|sleep|live|die|kill|fight|hunt|hit|cut|split|stab|scratch|dig|swim|fly|walk|come|lie|sit|stand|turn|fall|give|hold|squeeze|rub|wash|wipe|pull|push|throw|tie|sew|count|say|sing|play|float|flow|freeze|swell|sun|moon|star|water|rain|river|lake|sea|salt|stone|sand|dust|earth|cloud|fog|sky|wind|snow|ice|smoke|fire|ash|burn|road|mountain|red|green|yellow|white|black|night|day|year|warm|cold|full|new|old|good|bad|rotten|dirty|straight|round|sharp|dull|smooth|wet|dry|correct|near|far|right|left|at|in|with|and|if|because|name|the|be|cat|cat|bitch|smile")

RESERVED_TABLES: dict[str, dict[str, str]] = {"en": _EN, "la": _LA}
