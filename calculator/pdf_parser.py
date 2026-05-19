"""PDF datasheet parameter extraction — multilingual (EN / DE / PT / ES / FR)."""

import re

NOT_FOUND = "not in the datasheet"

# ── Value normalisation (foreign-language values → English) ──────────────────
# Each entry maps a spec label to an ordered list of (regex, english_replacement).
# Applied AFTER extraction to translate things like "Grauguss" → "Cast Iron".
_VALUE_TRANSLATIONS: dict[str, list[tuple[str, str]]] = {
    "Motor Frame Material": [
        (r"grauguss|gusseisen|gjl[-\s]?\d|gg[-\s]?\d|guss[-\s]?eisen|fonte\s+cin\w*|ferro\s+fundido"
         r"|fundici[oó]n\s+gris|hierro\s+fundido|fundici[oó]n|fonte\s+maleável|cast\s+iron",
         "Cast Iron"),
        (r"alumin[iu]m(?:druckguss|legier\w*)?|alum[ií]n[io]+(?:\s+fundido|\s+alloy)?|aluminio",
         "Aluminium"),
        (r"stahl|acero(?!\s+inox)|a[çc]o(?!\s+inox)|steel",
         "Steel"),
        (r"acero\s+inox|a[çc]o\s+inox\w*|edelstahl|acier\s+inox\w*|stainless",
         "Stainless Steel"),
    ],
    "Cooling Method": [
        (r"ic\s*410|tenv|keine\s+externe\s+k[üu]hlung|eigenk[üu]hlung|selbst(?:ak\w+)?k[üu]hlung"
         r"|totalmente\s+cerrado\s+sin\s+ventilaci|cerrado\s+sin\s+ventil"
         r"|refrigera[çc][ãa]o\s+pr[oó]pria|autoventilad[oa]|totalmente\s+fechado"
         r"|refroidissement\s+par\s+propre|propre\s+refroid\w*|non.?ventil[eé]",
         "IC410 TENV"),
        (r"ic\s*411|tefc|fremdbell?[üu]ftung|fremdgek[üu]hlt|fremdk[üu]hlung"
         r"|ventila[çc][ãa]o\s+for[çc]ada|refrigera[çc][ãa]o\s+for[çc]ada"
         r"|ventilaci[oó]n\s+forzada|refrigeraci[oó]n\s+forzada"
         r"|refroidissement\s+forc[eé]|motoventil[eé]",
         "IC411 TEFC"),
        (r"ic\s*416|ic\s*81[67]|water[- ]cool\w*|wassergek[üu]hlt|k[üu]hlwasser"
         r"|resfriamento\s+(?:a\s+)?[áa]gua|refrigera[çc][ãa]o\s+(?:a\s+)?[áa]gua",
         "Water Cooled"),
    ],
}


def _normalize_value(field: str, value: str) -> str:
    """Translate extracted values from any supported language to English."""
    rules = _VALUE_TRANSLATIONS.get(field, [])
    for pattern, english in rules:
        if re.search(pattern, value, re.IGNORECASE):
            return english
    return value


# ── Clean value extractors ────────────────────────────────────────────────────
# Each entry maps a spec label to an ordered list of regex patterns.
# The first capture group () is used as the extracted value.
# If no group is present the full match is used.
# Patterns are applied case-insensitively to the original text.

SPEC_VALUE_PATTERNS: dict[str, list[str]] = {

    "Motor Frame Material": [
        # English labels
        r"frame\s+material\s*[:\-=]?\s*(cast\s+iron|alumin\w+|steel|gjl[-\s\d]*|gg[-\s\d]+\w*)",
        r"housing\s+material\s*[:\-=]?\s*(cast\s+iron|alumin\w+|steel|gjl[-\s\d]*|gg[-\s\d]+\w*)",
        r"carcas[s]?\s+material\s*[:\-=]?\s*(cast\s+iron|alumin\w+|steel|gjl[-\s\d]*|gg[-\s\d]+\w*)",
        # German
        r"(?:geh[äa]use|rahmen)(?:material|werkstoff)\s*[:\-=]?\s*(grauguss|gusseisen|alumin\w+|stahl|gjl[-\s\d]*|gg[-\s\d]+\w*)",
        r"(?:material|werkstoff)\s*[:\-=]?\s*(grauguss|gusseisen|alumin\w+|stahl|gjl[-\s\d]*|gg[-\s\d]+\w*)",
        # Portuguese
        r"material\s+da\s+car[cç]a[çs]a\s*[:\-=]?\s*(ferro\s+fundido|alum[ií]n[io]+|a[çc]o|gjl[-\s\d]*|gg[-\s\d]+\w*)",
        r"material\s+(?:do\s+)?(?:corpo|carca[çc]a)\s*[:\-=]?\s*(ferro\s+fundido|alum[ií]n[io]+|a[çc]o|gjl[-\s\d]*)",
        # Spanish
        r"material\s+de\s+la\s+carca[sz]a\s*[:\-=]?\s*(fundici[oó]n|hierro\s+fundido|alum[ií]n[io]+|acero|gjl[-\s\d]*)",
        r"material\s+(?:del\s+)?(?:cuerpo|carca[sz]a)\s*[:\-=]?\s*(fundici[oó]n|alum[ií]n[io]+|acero|gjl[-\s\d]*)",
        # French
        r"mat[eé]riau\s+(?:du\s+)?(?:carter|carcasse|corps)\s*[:\-=]?\s*(fonte|alumin[iu]m|acier|gjl[-\s\d]*)",
        # Direct value recognition (any language context)
        r"\b(cast\s+iron)\b",
        r"\b(gjl[-\s]?\d{1,3}[-\s]?\d*)\b",
        r"\b(gg[-\s]?\d{1,3})\b",
        r"\b(alumin[iu]m(?:\s+alloy)?)\b",
        r"\b(grauguss|gusseisen)\b",
        r"\b(ferro\s+fundido)\b",
        r"\b(fundici[oó]n(?:\s+gris)?)\b",
        r"\b(fonte(?:\s+grise)?)\b",
    ],

    "Input Flange": [
        # English / generic
        r"(?:input\s+)?flange[^0-9\n]{0,45}(1[4-9]\d)\b",
        r"(?:iec|b5|b14)\s*[-\s]*(1[4-9]\d)\b",
        r"(?:square\s+flange|□)[^0-9\n]{0,15}(1[4-9]\d)\b",
        r"flange\s*[:\-=]?\s*(?:ø|□)?\s*(1[4-9]\d)\b",
        # German: Flansch, Befestigungsflansch, Anbauflansch
        r"(?:befestigungs|an(?:bau|trieb)s?|eingangs)?flansch[^0-9\n]{0,30}(1[4-9]\d)\b",
        # Portuguese: Flange de montagem, Flange de entrada
        r"flange\s+de\s+(?:montagem|entrada|fixação)[^0-9\n]{0,25}(1[4-9]\d)\b",
        # Spanish: Brida de montaje, Brida de entrada
        r"brida(?:\s+de\s+(?:montaje|entrada))?[^0-9\n]{0,25}(1[4-9]\d)\b",
        # French: Bride d'entrée, Bride de montage
        r"bride(?:\s+d['e]\s+(?:entr[eé]e|montage))?[^0-9\n]{0,25}(1[4-9]\d)\b",
        # Generic size fallback
        r"\b(1[4-9]\d)\s*mm(?:\s+flange)?\b",
    ],

    "Output Shaft": [
        # English
        r"(?:output\s+)?shaft[^0-9\n]{0,45}((?:ø\s*)?\d{2}k\d\s*[×x]\s*\d{2,3})",
        r"\b(\d{2}k6\s*[×x]\s*\d{2,3})\b",
        r"\b(ø\s*\d{2}\s*[×x]\s*\d{2,3})\b",
        r"\b(\d{2}\s*[×x]\s*\d{2,3})\b(?=\s*(?:with\s+key|passfeder|\bkey\b|mm|\bwith\b))",
        # German: Abtriebswelle, Wellendurchmesser
        r"(?:abtriebs|antriebs)?welle[^0-9\n]{0,45}((?:ø\s*)?\d{2}k?\d?\s*[×x]\s*\d{2,3})",
        r"wellendurchmesser[^0-9\n]{0,20}((?:ø\s*)?\d{2})\b",
        # Portuguese: Eixo de saída, Eixo
        r"eixo\s+de\s+sa[íi]da[^0-9\n]{0,30}((?:ø\s*)?\d{2}k?\d?\s*[×x]\s*\d{2,3})",
        r"\beixo\b[^0-9\n]{0,30}((?:ø\s*)?\d{2}k?\d?\s*[×x]\s*\d{2,3})",
        # Spanish: Eje de salida
        r"eje\s+de\s+salida[^0-9\n]{0,30}((?:ø\s*)?\d{2}k?\d?\s*[×x]\s*\d{2,3})",
        r"\beje\b[^0-9\n]{0,30}((?:ø\s*)?\d{2}k?\d?\s*[×x]\s*\d{2,3})",
        # French: Arbre de sortie
        r"arbre\s+de\s+sortie[^0-9\n]{0,30}((?:ø\s*)?\d{2}k?\d?\s*[×x]\s*\d{2,3})",
        # Two-group fallback: captures diameter and length separately
        r"shaft[^0-9\n]{0,45}(?:ø\s*)?(\d{2})\s*[×x]\s*(\d{2,3})",
    ],

    "Cooling Method": [
        # IC codes (universal)
        r"\b(ic\s*4\d{2})\b",
        r"\b(tenv)\b",
        r"\b(tefc)\b",
        r"\b(ic\s*\d{3})\b",
        # English labels
        r"cooling\s+method\s*[:\-=]?\s*([^\n,;.(]{3,35})",
        r"cooling\s*[:\-=]\s*([^\n,;.(]{3,35})",
        # German: Kühlart, Kühlmethode, Kühlungsart
        r"k[üu]hlart\s*[:\-=]?\s*([^\n,;.(]{3,35})",
        r"k[üu]hlmethode\s*[:\-=]?\s*([^\n,;.(]{3,35})",
        r"k[üu]hlungsart\s*[:\-=]?\s*([^\n,;.(]{3,35})",
        r"(eigenk[üu]hlung|fremdbell?[üu]ftung|fremdgek[üu]hlt|k[üu]hlung)\b",
        # Portuguese: Tipo de resfriamento / refrigeração
        r"(?:tipo\s+de\s+)?(?:resfriamento|refrigera[çc][ãa]o)\s*[:\-=]?\s*([^\n,;.(]{3,35})",
        r"(?:forma\s+de\s+)?ventila[çc][ãa]o\s*[:\-=]?\s*([^\n,;.(]{3,35})",
        # Spanish: Tipo de refrigeración / enfriamiento
        r"(?:tipo\s+de\s+)?(?:refrigeraci[oó]n|enfriamiento)\s*[:\-=]?\s*([^\n,;.(]{3,35})",
        r"sistema\s+de\s+(?:refrigeraci[oó]n|ventilaci[oó]n)\s*[:\-=]?\s*([^\n,;.(]{3,35})",
        # French: Mode de refroidissement
        r"(?:mode\s+de\s+)?refroidissement\s*[:\-=]?\s*([^\n,;.(]{3,35})",
    ],

    "IP Rating": [
        # Universal: IP followed by two digits
        r"\b(ip\s*\d{2})\b",
        r"(?:protection|ingress)\s+(?:class\s+)?(?:ip\s*)?(\d{2})\b",
        r"ip[-\s]*(\d{2})\b",
        # German: Schutzart
        r"schutzart\s*[:\-=]?\s*ip\s*(\d{2})\b",
        r"schutzart\s*[:\-=]?\s*(\d{2})\b",
        # Portuguese: Grau de proteção
        r"grau\s+de\s+prote[çc][ãa]o\s*[:\-=]?\s*ip\s*(\d{2})\b",
        r"grau\s+de\s+prote[çc][ãa]o\s*[:\-=]?\s*(\d{2})\b",
        r"prote[çc][ãa]o\s*[:\-=]?\s*ip\s*(\d{2})\b",
        # Spanish: Grado de protección
        r"grado\s+de\s+protecci[oó]n\s*[:\-=]?\s*ip\s*(\d{2})\b",
        r"grado\s+de\s+protecci[oó]n\s*[:\-=]?\s*(\d{2})\b",
        # French: Degré de protection
        r"degr[eé]\s+de\s+protection\s*[:\-=]?\s*ip\s*(\d{2})\b",
        r"indice\s+de\s+protection\s*[:\-=]?\s*ip\s*(\d{2})\b",
    ],

    "Ambient Temperatures": [
        # Universal temperature range (works in any language context)
        r"([-−]\s*\d{1,3}\s*°?\s*c\s*(?:to|bis|à|até|hasta|à)\s*[+]?\s*\d{1,3}\s*°?\s*c)",
        r"([-−]\s*\d{1,3}\s*°?\s*c\s*(?:\.{2,3}|–|-)\s*[+]?\s*\d{1,3}\s*°?\s*c)",
        # English labels
        r"ambient\s+temp[^\n:]{0,25}[:\-=]?\s*([-−][^,;\n.]{5,45})",
        r"temperature\s+range[^\n:]{0,20}[:\-=]?\s*([-−\d][^,;\n.]{5,45})",
        # German: Umgebungstemperatur
        r"umgebungstemperatur\s*[:\-=]?\s*([-−\d][^,;\n.]{5,45})",
        r"betriebstemperatur(?:bereich)?\s*[:\-=]?\s*([-−\d][^,;\n.]{5,45})",
        # Portuguese: Temperatura ambiente
        r"temperatura\s+ambiente\s*[:\-=]?\s*([-−\d][^,;\n.]{5,45})",
        r"faixa\s+de\s+temperatura\s*[:\-=]?\s*([-−\d][^,;\n.]{5,45})",
        # Spanish: Temperatura ambiente
        r"temperatura\s+(?:ambiente|de\s+trabajo)\s*[:\-=]?\s*([-−\d][^,;\n.]{5,45})",
        r"rango\s+de\s+temperatura\s*[:\-=]?\s*([-−\d][^,;\n.]{5,45})",
        # French: Température ambiante
        r"temp[eé]rature\s+ambiante\s*[:\-=]?\s*([-−\d][^,;\n.]{5,45})",
        r"plage\s+de\s+temp[eé]rature\s*[:\-=]?\s*([-−\d][^,;\n.]{5,45})",
        # Fallback: capture only low end
        r"([-−]\s*\d{1,3}\s*°?\s*c)",
    ],

    "Voltages / Frequencies": [
        # Combined format (universal)
        r"(\d{3,4}\s*/\s*\d{3,4}(?:\s*/\s*\d{3,4})?\s*v[^\n,;.]{0,35}(?:50|60)\s*hz)",
        r"(\d{3,4}\s*/\s*\d{3,4}\s*v[^\n,;.]{0,25}hz)",
        # Individual voltage/frequency
        r"((?:400|480|690)\s*v[^\n,;.]{0,15}(?:50|60)\s*hz)",
        r"((?:50|60)\s*hz[^\n,;.]{0,15}(?:400|480|690)\s*v)",
        # English label
        r"supply\s+voltage[^\n:]{0,20}[:\-=]?\s*([\d/\s,v]+(?:50|60)\s*hz[^\n,;.]{0,15})",
        # German: Spannung, Nennspannung, Versorgungsspannung
        r"(?:netz|versorgungs|nenn)?spannung\s*[:\-=]?\s*([\d/\s,v]+(?:(?:50|60)\s*hz)?[^\n,;.]{0,25})",
        # Portuguese: Tensão, Tensão nominal, Tensão de alimentação
        r"tens[ãa]o\s+(?:nominal|de\s+alimenta[çc][ãa]o|de\s+rede)?\s*[:\-=]?\s*([\d/\s,v]+(?:(?:50|60)\s*hz)?[^\n,;.]{0,25})",
        # Spanish: Tensión, Tensión nominal, Tensión de alimentación
        r"tensi[oó]n\s+(?:nominal|de\s+alimentaci[oó]n|de\s+red)?\s*[:\-=]?\s*([\d/\s,v]+(?:(?:50|60)\s*hz)?[^\n,;.]{0,25})",
        # French: Tension, Tension nominale
        r"tension\s+(?:nominale|d['e]alimentation|réseau)?\s*[:\-=]?\s*([\d/\s,v]+(?:(?:50|60)\s*hz)?[^\n,;.]{0,25})",
        # Voltage only fallback
        r"((?:400|480|690)\s*/?(?:400|480|690)?\s*v\b)",
    ],

    "Efficiency Class": [
        # Universal: IE codes
        r"\b(ie\s*[2-4])\b",
        r"efficiency\s+class\s*[:\-=]?\s*(ie\s*[2-4])\b",
        # German: Wirkungsgradklasse, Effizienzklasse
        r"(?:wirkungsgrad|effizienz)klasse\s*[:\-=]?\s*(ie\s*[2-4])\b",
        # Portuguese: Classe de eficiência
        r"classe\s+de\s+efici[eê]ncia\s*[:\-=]?\s*(ie\s*[2-4])\b",
        # Spanish: Clase de eficiencia
        r"clase\s+de\s+eficiencia\s*[:\-=]?\s*(ie\s*[2-4])\b",
        # French: Classe de rendement / d'efficacité
        r"classe\s+(?:de\s+)?(?:rendement|efficacit[eé])\s*[:\-=]?\s*(ie\s*[2-4])\b",
    ],

    "Insulation Class": [
        # English
        r"insulation\s+class\s*[:\-=]?\s*([a-hA-H])\b",
        r"insul\.\s*class\s*[:\-=]?\s*([a-hA-H])\b",
        r"thermal\s+class\s*[:\-=]?\s*([a-hA-H\d]+)\b",
        r"\bclass\s+([a-hA-H])\b",
        r"\binsulation\b[^\n:]{0,25}[:\-=]\s*([a-hA-H])\b",
        # German: Isolierklasse, Wärmeklasse, Temperaturklasse
        r"isolierklasse\s*[:\-=]?\s*([a-hA-H])\b",
        r"w[äa]rmeklasse\s*[:\-=]?\s*([a-hA-H])\b",
        r"temperaturklasse\s*[:\-=]?\s*([a-hA-H])\b",
        # Portuguese: Classe de isolamento
        r"classe\s+de\s+isolamento\s*[:\-=]?\s*([a-hA-H])\b",
        r"isolamento\s+t[eé]rmico\s*[:\-=]?\s*([a-hA-H])\b",
        # Spanish: Clase de aislamiento
        r"clase\s+de\s+aislamiento\s*[:\-=]?\s*([a-hA-H])\b",
        r"aislamiento\s*[:\-=]?\s*([a-hA-H])\b",
        # French: Classe d'isolement, Classe thermique
        r"classe\s+d['e]isolement\s*[:\-=]?\s*([a-hA-H])\b",
        r"classe\s+thermique\s*[:\-=]?\s*([a-hA-H])\b",
    ],

    "Duty Cycle": [
        # Universal: S-codes
        r"\b(s\d\s*[-–]?\s*\d{1,3}\s*%)\b",
        r"\b(s[123456])\b",
        # English
        r"duty\s+cycle\s*[:\-=]?\s*([^\n,;.]{3,20})",
        r"intermittent[^\n,;.]{0,20}(\d{1,3}\s*%)",
        # German: Betriebsart, Einschaltdauer
        r"betriebsart\s*[:\-=]?\s*([^\n,;.]{3,20})",
        r"einschaltdauer\s*[:\-=]?\s*([^\n,;.]{3,20})",
        # Portuguese: Regime de serviço, Serviço
        r"regime\s+de\s+servi[çc]o\s*[:\-=]?\s*([^\n,;.]{3,20})",
        r"servi[çc]o\s*[:\-=]?\s*(s\d[^\n,;.]{0,15})",
        # Spanish: Régimen de servicio, Servicio
        r"r[eé]gimen\s+de\s+servicio\s*[:\-=]?\s*([^\n,;.]{3,20})",
        r"servicio\s*[:\-=]?\s*(s\d[^\n,;.]{0,15})",
        # French: Régime de service
        r"r[eé]gime\s+de\s+service\s*[:\-=]?\s*([^\n,;.]{3,20})",
    ],

    "Standstill Heater": [
        # Value recognition (any language)
        r"(24\s*vdc[^\n,;.]{0,25})",
        r"(24\s*v\s*dc[^\n,;.]{0,25})",
        r"(24\s*v\b[^\n,;.]{0,15})",
        # English labels
        r"heater\s*[:\-=]?\s*([^\n,;.]{3,35})",
        r"anti.?conden\w*\s*[:\-=]?\s*([^\n,;.]{3,35})",
        r"space\s+heat\w*\s*[:\-=]?\s*([^\n,;.]{3,35})",
        # German: Stillstandsheizung, Kondensationsheizung, Heizung
        r"stillstandsheizung\s*[:\-=]?\s*([^\n,;.]{3,35})",
        r"kondensationsheizung\s*[:\-=]?\s*([^\n,;.]{3,35})",
        r"heizpatrone\s*[:\-=]?\s*([^\n,;.]{3,35})",
        r"stillstands?heizung\b[^\n,;.]{0,15}([\d]+\s*v\w*)",
        # Portuguese: Aquecedor, Resistência de aquecimento
        r"aquecedor\s+(?:de\s+)?(?:standstill|repouso|parada)?\s*[:\-=]?\s*([^\n,;.]{3,35})",
        r"resist[eê]ncia\s+de\s+aquecimento\s*[:\-=]?\s*([^\n,;.]{3,35})",
        # Spanish: Calefactor, Resistencia calefactora
        r"calefactor\s+(?:de\s+parada)?\s*[:\-=]?\s*([^\n,;.]{3,35})",
        r"resist[eé]ncia\s+calefactora\s*[:\-=]?\s*([^\n,;.]{3,35})",
        r"anticondensaci[oó]n\s*[:\-=]?\s*([^\n,;.]{3,35})",
        # French: Réchauffeur, Résistance de chauffage
        r"r[eé]chauffeur\s+(?:d['e]arr[eê]t)?\s*[:\-=]?\s*([^\n,;.]{3,35})",
        r"r[eé]sistance\s+(?:de\s+)?chauffage\s*[:\-=]?\s*([^\n,;.]{3,35})",
    ],

    "Coating": [
        # Universal codes
        r"\b(c5[-\s]*h)\b",
        r"(en\s*12944[-\s]*\d*)",
        # English labels
        r"coating\s+class\s*[:\-=]?\s*([^\n,;.]{2,20})",
        r"paint\s+system\s*[:\-=]?\s*([^\n,;.]{3,30})",
        r"corrosion\s+(?:cat|protection)[^\n:]{0,20}[:\-=]?\s*([^\n,;.]{3,25})",
        # German: Beschichtung, Lackierung, Korrosionsschutz
        r"beschichtungsklasse\s*[:\-=]?\s*([^\n,;.]{2,20})",
        r"korrosionsschutzklasse\s*[:\-=]?\s*([^\n,;.]{2,20})",
        r"lackiersystem\s*[:\-=]?\s*([^\n,;.]{3,30})",
        r"korrosionsschutz\s*[:\-=]?\s*([^\n,;.]{3,25})",
        # Portuguese: Classe de revestimento, Proteção anticorrosiva
        r"classe\s+de\s+revestimento\s*[:\-=]?\s*([^\n,;.]{2,20})",
        r"prote[çc][ãa]o\s+anticorrosiva\s*[:\-=]?\s*([^\n,;.]{3,25})",
        r"sistema\s+de\s+pintura\s*[:\-=]?\s*([^\n,;.]{3,30})",
        # Spanish: Clase de recubrimiento, Protección anticorrosiva
        r"clase\s+de\s+recubrimiento\s*[:\-=]?\s*([^\n,;.]{2,20})",
        r"protecci[oó]n\s+anticorrosiva\s*[:\-=]?\s*([^\n,;.]{3,25})",
        r"sistema\s+de\s+pintura\s*[:\-=]?\s*([^\n,;.]{3,30})",
        # French: Classe de revêtement, Protection anticorrosion
        r"classe\s+de\s+rev[eê]tement\s*[:\-=]?\s*([^\n,;.]{2,20})",
        r"protection\s+anticorrosion\s*[:\-=]?\s*([^\n,;.]{3,25})",
        r"syst[eè]me\s+de\s+peinture\s*[:\-=]?\s*([^\n,;.]{3,30})",
    ],

    "Top Color": [
        r"\b(ral\s*\d{4})\b",
        r"colou?r\s*[:\-=]?\s*(ral\s*\d{4})",
        r"(?:paint|finish)[^\n:]{0,15}(ral\s*\d{4})",
        # German: Farbe, Farbton, Decklack
        r"farb(?:ton|e)?\s*[:\-=]?\s*(ral\s*\d{4})",
        r"decklack\s*[:\-=]?\s*(ral\s*\d{4})",
        # Portuguese: Cor, Cor de topo
        r"cor(?:\s+de\s+(?:topo|acabamento))?\s*[:\-=]?\s*(ral\s*\d{4})",
        r"pintura\s+(?:final|acabamento)\s*[:\-=]?\s*(ral\s*\d{4})",
        # Spanish: Color, Color final
        r"color(?:\s+(?:final|de\s+acabado))?\s*[:\-=]?\s*(ral\s*\d{4})",
        # French: Couleur, Teinte
        r"couleur(?:\s+(?:finale|de\s+finition))?\s*[:\-=]?\s*(ral\s*\d{4})",
        r"teinte\s*[:\-=]?\s*(ral\s*\d{4})",
    ],

    "Motor Certificate": [
        r"\b(dnv[-\s]?gl[\w\s]{0,15})\b",
        r"\b(dnv[\s\w]{0,10})\b",
        r"\b(abs\s+type[\s\w]{0,15})\b",
        r"\b(lloyd[s]?[\s\w]{0,10})\b",
        r"\b(atex[\s\w]{0,10})\b",
        r"type\s+approv\w*\s*[:\-=]?\s*([^\n,;.]{3,30})",
        r"certificat\w*\s*[:\-=]?\s*([^\n,;.]{3,30})",
        # German: Zulassung, Zertifikat
        r"zulassung\s*[:\-=]?\s*([^\n,;.]{3,30})",
        r"zertifikat\s*[:\-=]?\s*([^\n,;.]{3,30})",
        r"typenzulassung\s*[:\-=]?\s*([^\n,;.]{3,30})",
        # Portuguese: Certificado, Aprovação de tipo
        r"certificado\s*[:\-=]?\s*([^\n,;.]{3,30})",
        r"aprova[çc][ãa]o\s+(?:de\s+tipo)?\s*[:\-=]?\s*([^\n,;.]{3,30})",
        # Spanish: Certificado, Homologación
        r"homologaci[oó]n\s*[:\-=]?\s*([^\n,;.]{3,30})",
        # French: Certificat, Approbation de type
        r"certificat\s*[:\-=]?\s*([^\n,;.]{3,30})",
        r"approbation\s+de\s+type\s*[:\-=]?\s*([^\n,;.]{3,30})",
    ],

    "Weight": [
        # English / metric (any language uses kg)
        r"(?:weight|mass)\s*[:\-=]?\s*([\d.,]+)\s*kg",
        r"approx[.,]?\s*([\d.,]+)\s*kg",
        # German: Gewicht, Eigengewicht, Masse
        r"(?:eigen)?gewicht\s*[:\-=]?\s*([\d.,]+)\s*kg",
        r"(?:gesamt)?masse\s*[:\-=]?\s*([\d.,]+)\s*kg",
        r"ca\.\s*([\d.,]+)\s*kg",
        # Portuguese: Peso, Massa
        r"peso\s+(?:aprox\w*\.?)?\s*[:\-=]?\s*([\d.,]+)\s*kg",
        r"massa\s+(?:aprox\w*\.?)?\s*[:\-=]?\s*([\d.,]+)\s*kg",
        # Spanish: Peso, Masa
        r"peso\s+(?:aprox\w*\.?)?\s*[:\-=]?\s*([\d.,]+)\s*kg",
        r"masa\s*[:\-=]?\s*([\d.,]+)\s*kg",
        # French: Poids, Masse
        r"poids\s+(?:approx\w*\.?)?\s*[:\-=]?\s*([\d.,]+)\s*kg",
        r"masse\s*[:\-=]?\s*([\d.,]+)\s*kg",
        # Generic: any number followed by kg
        r"\b([\d.,]+)\s*kg\b",
    ],
}


def _extract_clean_value(text: str, field: str) -> str:
    """
    Return a short, clean extracted value for a spec field.
    Searches case-insensitively. Returns first capture group, normalised to English.
    """
    for pat in SPEC_VALUE_PATTERNS.get(field, []):
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            if m.lastindex and m.lastindex >= 2:
                val = " × ".join(g for g in m.groups() if g)
            elif m.lastindex:
                val = m.group(1)
            else:
                val = m.group(0)
            val = re.sub(r'\s+', ' ', val).strip().rstrip('.,;:')
            return _normalize_value(field, val)
    return NOT_FOUND


# ── Compliance rules ─────────────────────────────────────────────────────────
# Values are already normalised to English before compliance is checked.
_COMPLIANCE_RULES = [
    ('spec_frame_material',    'Motor Frame Material', 'Cast Iron (GJL / GG)',
     [r"cast\s*iron", r"gjl", r"gg[-\s]?\d+", r"cast", r"iron"]),
    ('spec_output_flange',     'Motor Flange — IEC90 B5', 'IEC90 B5 · Ø165 mm bolt circle',
     [r"165", r"iec\s*90", r"\bb5\b", r"160"]),
    ('spec_shaft',             'Output Shaft',         '32 × 50 mm',
     [r"32k6", r"32\s*[x×]\s*50", r"\b32\b"]),
    ('spec_cooling_method',    'Cooling Method',       'IC410 / TENV',
     [r"ic\s*410", r"ic410", r"\btenv\b", r"non.?ventilated", r"\b410\b"]),
    ('spec_ip_rating',         'IP Rating',            'IP66',
     [r"\bip\s*66\b", r"ip66", r"\b66\b"]),
    ('spec_ambient_temp',      'Ambient Temperature',  '−20°C low end, +45°C high end (or wider)',
     [r"-\s*20", r"−\s*20", r"−20"]),
    ('spec_heater',            'Standstill Heater',    '24 VDC',
     [r"24\s*v\s*dc", r"24\s*vdc", r"24\s*v\b"]),
    ('spec_coating',           'Coating',              'C5H / EN 12944-5',
     [r"c5[-\s]*h", r"en\s*12944", r"\bc5\b"]),
    ('spec_top_color',         'Top Color',            'RAL7035',
     [r"ral\s*7035", r"ral7035", r"7035"]),
    ('spec_voltage',           'Voltage / Frequency',  '400/690V 50Hz · 400/480/690V 60Hz',
     [r"400", r"690", r"480", r"50\s*hz", r"60\s*hz"]),
    ('spec_efficiency_class',  'Efficiency Class',     'IE2 or higher',
     [r"\bie[234]\b", r"ie\s*[234]"]),
    ('spec_insulation_class',  'Insulation Class',     'Class H',
     [r"\bclass\s*h\b", r"insul.*\s*h\b", r"thermal.*h\b", r"\bh\b"]),
]


def parse_datasheet(pdf_path: str) -> dict[str, str]:
    """Extract clean motor spec values from a PDF. Returns {label: value}."""
    try:
        import pdfplumber
    except ImportError:
        raise ImportError(
            "pdfplumber is required for PDF parsing.\n"
            "Install it with: pip install pdfplumber"
        )
    pages: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                pages.append(t)
    text = "\n".join(pages)
    return {field: _extract_clean_value(text, field) for field in SPEC_VALUE_PATTERNS}


def parse_text(text: str) -> dict[str, str]:
    """Extract clean spec values from pasted text."""
    return {field: _extract_clean_value(text, field) for field in SPEC_VALUE_PATTERNS}


# ── Numeric parameter extraction ─────────────────────────────────────────────

_NUM = r"([\d]+[.,][\d]*)"

# kNm pattern helper
_kNm = r"([\d]+[.,][\d]*)\s*(?:knm|kn\.?m)"

MOTOR_PARAM_PATTERNS: dict[str, list[str]] = {

    # ── Crane load ──────────────────────────────────────────────────────────
    "crane_torque_max": [
        # kNm first (unit detection in extract_motor_params)
        rf"(?:max(?:imum)?|peak|maximal[e]?)\s+(?:(?:slewing|swing|output|crane|abgabe)\s+)?(?:torque|moment|drehmoment)\s*[:\-=]\s*{_kNm}",
        rf"m[_\s]?max\s*[:\-=]\s*{_kNm}",
        rf"(?:slewing|swing)\s+torque\s*(?:max(?:imum)?)?\s*[:\-=]\s*{_kNm}",
        # German kNm: Maximales Schwenkmoment, Maximales Drehmoment
        rf"(?:max(?:imales?)?)\s+(?:schwenk|dreh|abgabe)?moment\s*[:\-=]\s*{_kNm}",
        rf"maximalmoment\s*[:\-=]\s*{_kNm}",
        # Portuguese kNm: Momento máximo, Torque máximo
        rf"(?:momento|torque|bin[áa]rio)\s+m[áa]ximo\s*[:\-=]\s*{_kNm}",
        rf"m[áa]x(?:imo)?\s+(?:de\s+)?(?:momento|torque)\s*[:\-=]\s*{_kNm}",
        # Spanish kNm: Momento máximo, Par máximo
        rf"(?:par|momento|torque)\s+m[áa]ximo\s*[:\-=]\s*{_kNm}",
        # French kNm: Couple maximum
        rf"couple\s+(?:maximal|maximum|maxi)\s*[:\-=]\s*{_kNm}",
        # Plain Nm fallback (large value)
        rf"(?:max(?:imum)?|peak)\s+(?:(?:slewing|swing|output)\s+)?(?:torque|moment)\s*[:\-=]\s*{_NUM}\s*nm(?!\s*m)",
        rf"m[_\s]?max\s*[:\-=]\s*{_NUM}\s*nm(?!\s*m)",
        rf"(?:max(?:imales?)?)\s+(?:schwenk|dreh)?moment\s*[:\-=]\s*{_NUM}\s*nm(?!\s*m)",
        rf"(?:momento|torque|bin[áa]rio)\s+m[áa]ximo\s*[:\-=]\s*{_NUM}\s*nm(?!\s*m)",
        rf"(?:par|moment)\s+(?:maximal|maximum)\s*[:\-=]\s*{_NUM}\s*nm(?!\s*m)",
    ],

    "crane_torque_nom": [
        # kNm first
        rf"(?:nom(?:inal)?|rated|nenn|continuous)\s+(?:(?:slewing|swing|output|crane|abgabe)\s+)?(?:torque|moment|drehmoment)\s*[:\-=]\s*{_kNm}",
        rf"m[_\s]?(?:nom|nenn)\s*[:\-=]\s*{_kNm}",
        rf"(?:slewing|swing)\s+torque\s*(?:nom(?:inal)?)?\s*[:\-=]\s*{_kNm}",
        # German kNm
        rf"nenn(?:schwenk|dreh|abgabe)?moment\s*[:\-=]\s*{_kNm}",
        rf"(?:nennmoment|nenndrehmoment)\s*[:\-=]\s*{_kNm}",
        # Portuguese kNm
        rf"(?:momento|torque|bin[áa]rio)\s+nominal\s*[:\-=]\s*{_kNm}",
        # Spanish kNm
        rf"(?:par|momento|torque)\s+nominal\s*[:\-=]\s*{_kNm}",
        # French kNm
        rf"couple\s+(?:nominal|nominale)\s*[:\-=]\s*{_kNm}",
        # Plain Nm fallback
        rf"(?:nom(?:inal)?|rated|nenn)\s+(?:(?:slewing|swing|output)\s+)?(?:torque|moment)\s*[:\-=]\s*{_NUM}\s*nm(?!\s*m)",
        rf"m[_\s]?(?:nom|nenn)\s*[:\-=]\s*{_NUM}\s*nm(?!\s*m)",
        rf"(?:nennmoment|nenndrehmoment)\s*[:\-=]\s*{_NUM}\s*nm(?!\s*m)",
        rf"(?:momento|torque|bin[áa]rio)\s+nominal\s*[:\-=]\s*{_NUM}\s*nm(?!\s*m)",
        rf"(?:par|moment)\s+(?:nominal)\s*[:\-=]\s*{_NUM}\s*nm(?!\s*m)",
    ],

    # ── Motor speed ──────────────────────────────────────────────────────────
    "motor_speed": [
        # English
        rf"(?:rated|synchronous|nominal|nenn)\s*(?:speed|drehzahl)\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        rf"n\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        rf"n_?(?:rated|nenn|1)\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        # German
        rf"nenndrehzahl\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        rf"betriebsdrehzahl\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        rf"drehzahl\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        # Portuguese
        rf"velocidade\s+nominal\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        rf"rota[çc][ãa]o\s+nominal\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        rf"velocidade\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        # Spanish
        rf"velocidad\s+nominal\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        rf"velocidad\s+de\s+(?:giro|rotaci[oó]n)\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        rf"velocidad\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        # French
        rf"vitesse\s+nominale\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1|tr/min)",
        rf"vitesse\s+de\s+rotation\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1|tr/min)",
        # Generic fallback: speed value + units
        rf"([1-9]\d{{2,3}})\s*(?:rpm|r/min|min-1)",
    ],

    # ── Motor rated torque ───────────────────────────────────────────────────
    "motor_rated_torque": [
        # English
        rf"(?:rated|nominal|nenn)\s*torque\s*[=:]\s*{_NUM}\s*nm",
        rf"m_?n\s*[=:]\s*{_NUM}\s*nm",
        rf"motor\s+torque\s*[=:]\s*{_NUM}\s*nm",
        rf"shaft\s+torque\s*[=:]\s*{_NUM}\s*nm",
        # German
        rf"nennmoment\s*[=:]\s*{_NUM}\s*nm",
        rf"nenndrehmoment\s*[=:]\s*{_NUM}\s*nm",
        rf"motormoment\s*[=:]\s*{_NUM}\s*nm",
        # Portuguese
        rf"bin[áa]rio\s+(?:nominal|nominale?)\s*[=:]\s*{_NUM}\s*nm",
        rf"torque\s+nominal\s*[=:]\s*{_NUM}\s*nm",
        rf"momento\s+nominal\s*[=:]\s*{_NUM}\s*nm",
        # Spanish
        rf"par\s+nominal\s*[=:]\s*{_NUM}\s*nm",
        rf"par\s+(?:de\s+)?(?:funcionamiento|trabajo)\s*[=:]\s*{_NUM}\s*nm",
        rf"torque\s+nominal\s*[=:]\s*{_NUM}\s*nm",
        # French
        rf"couple\s+nominal\s*[=:]\s*{_NUM}\s*nm",
        rf"couple\s+nominale?\s*[=:]\s*{_NUM}\s*nm",
    ],

    # ── Starting factor Ma/Mn ────────────────────────────────────────────────
    "starting_factor": [
        # Universal: Ma/Mn notation
        rf"ma\s*/\s*mn\s*[=:]\s*{_NUM}",
        rf"m_?a\s*/\s*m_?n\s*[=:]\s*{_NUM}",
        # English
        rf"starting\s+(?:torque\s+)?(?:ratio|factor|multiple)\s*[=:]\s*{_NUM}",
        rf"breakaway\s+(?:torque\s+)?(?:ratio|factor)\s*[=:]\s*{_NUM}",
        rf"locked\s+rotor\s+(?:torque\s+)?(?:ratio|factor)\s*[=:]\s*{_NUM}",
        # German: Anlaufmomentfaktor, Anlaufdrehmomentverhältnis
        rf"anlauf(?:moment)?faktor\s*[=:]\s*{_NUM}",
        rf"anlaufdrehmomentverhältnis\s*[=:]\s*{_NUM}",
        rf"anlaufmoment\s*[=:]\s*{_NUM}",
        # Portuguese: Fator de partida, Relação Ma/Mn
        rf"fator\s+de\s+partida\s*[=:]\s*{_NUM}",
        rf"bin[áa]rio\s+de\s+(?:partida|arranque)\s*/\s*(?:bin[áa]rio\s+nominal)\s*[=:]\s*{_NUM}",
        # Spanish: Factor de arranque, Relación de par de arranque
        rf"factor\s+de\s+arranque\s*[=:]\s*{_NUM}",
        rf"relaci[oó]n\s+(?:de\s+)?par\s+(?:de\s+arranque)?\s*[=:]\s*{_NUM}",
        # French: Facteur de démarrage
        rf"facteur\s+de\s+d[eé]marrage\s*[=:]\s*{_NUM}",
        rf"rapport\s+ma/mn\s*[=:]\s*{_NUM}",
    ],

    # ── Motor power ──────────────────────────────────────────────────────────
    "supplier_motor_power_kw": [
        # English
        rf"(?:rated|nominal|nenn)?\s*power\s*[=:]\s*{_NUM}\s*kw",
        rf"p\s*[=:]\s*{_NUM}\s*kw",
        # German
        rf"(?:nenn)?leistung\s*[=:]\s*{_NUM}\s*kw",
        rf"motorleistung\s*[=:]\s*{_NUM}\s*kw",
        # Portuguese
        rf"pot[eê]ncia\s+nominal\s*[=:]\s*{_NUM}\s*kw",
        rf"pot[eê]ncia\s*[=:]\s*{_NUM}\s*kw",
        # Spanish
        rf"potencia\s+nominal\s*[=:]\s*{_NUM}\s*kw",
        rf"potencia\s*[=:]\s*{_NUM}\s*kw",
        # French
        rf"puissance\s+nominale\s*[=:]\s*{_NUM}\s*kw",
        rf"puissance\s*[=:]\s*{_NUM}\s*kw",
        # Generic fallback
        rf"{_NUM}\s*kw(?!\s*h)",
    ],

    # ── Supplier motor rated torque ──────────────────────────────────────────
    "supplier_motor_rated_torque": [
        rf"(?:rated|nominal|nenn)\s*torque\s*[=:]\s*{_NUM}\s*nm",
        rf"m_?n\s*[=:]\s*{_NUM}\s*nm",
        rf"motor\s+(?:rated\s+)?torque\s*[=:]\s*{_NUM}\s*nm",
        rf"nennmoment\s*[=:]\s*{_NUM}\s*nm",
        rf"bin[áa]rio\s+nominal\s*[=:]\s*{_NUM}\s*nm",
        rf"par\s+nominal\s*[=:]\s*{_NUM}\s*nm",
        rf"couple\s+nominal\s*[=:]\s*{_NUM}\s*nm",
    ],

    # ── Supplier motor starting torque ───────────────────────────────────────
    "supplier_motor_starting_torque": [
        # English
        rf"starting\s+torque\s*[=:]\s*{_NUM}\s*nm",
        rf"m_?a\s*[=:]\s*{_NUM}\s*nm",
        rf"breakaway\s+torque\s*[=:]\s*{_NUM}\s*nm",
        rf"locked\s+rotor\s+torque\s*[=:]\s*{_NUM}\s*nm",
        # German
        rf"anzugsmoment\s*[=:]\s*{_NUM}\s*nm",
        rf"anlaufmoment\s*[=:]\s*{_NUM}\s*nm",
        rf"anzugsdrehmoment\s*[=:]\s*{_NUM}\s*nm",
        # Portuguese
        rf"bin[áa]rio\s+de\s+(?:partida|arranque)\s*[=:]\s*{_NUM}\s*nm",
        rf"torque\s+de\s+(?:partida|arranque)\s*[=:]\s*{_NUM}\s*nm",
        rf"momento\s+de\s+(?:partida|arranque)\s*[=:]\s*{_NUM}\s*nm",
        # Spanish
        rf"par\s+de\s+arranque\s*[=:]\s*{_NUM}\s*nm",
        rf"torque\s+de\s+arranque\s*[=:]\s*{_NUM}\s*nm",
        # French
        rf"couple\s+de\s+d[eé]marrage\s*[=:]\s*{_NUM}\s*nm",
    ],

    # ── Supplier gearbox rated torque ────────────────────────────────────────
    "supplier_gearbox_rated_torque": [
        # English
        rf"(?:gearbox|gear|output)\s+(?:rated\s+)?torque\s*[=:]\s*{_NUM}\s*nm",
        rf"t_?2\s*[=:]\s*{_NUM}\s*nm",
        rf"output\s+torque\s*[=:]\s*{_NUM}\s*nm",
        # German
        rf"abtriebsmoment\s*[=:]\s*{_NUM}\s*nm",
        rf"getriebeabtriebsmoment\s*[=:]\s*{_NUM}\s*nm",
        rf"(?:nenn)?drehmoment\s+(?:getriebe|abtrieb)\s*[=:]\s*{_NUM}\s*nm",
        # Portuguese
        rf"bin[áa]rio\s+(?:nominal\s+)?(?:da\s+caixa|do\s+redutor)\s*[=:]\s*{_NUM}\s*nm",
        rf"torque\s+(?:nominal\s+)?(?:da\s+caixa|do\s+redutor)\s*[=:]\s*{_NUM}\s*nm",
        # Spanish
        rf"par\s+(?:nominal\s+)?(?:del\s+reductor|de\s+salida)\s*[=:]\s*{_NUM}\s*nm",
        # French
        rf"couple\s+(?:nominal\s+)?(?:du\s+r[eé]ducteur|de\s+sortie)\s*[=:]\s*{_NUM}\s*nm",
    ],

    # ── Bevel gearbox ratio ──────────────────────────────────────────────────
    "supplier_bevel_ratio": [
        # English
        rf"(?:bevel|reduction|gear)\s+ratio\s*[=:]\s*{_NUM}(?:\s*:1)?",
        rf"i_?(?:bevel|b)\s*[=:]\s*{_NUM}",
        # German
        rf"(?:kegel|getriebe|untersetzungs)?übersetzung(?:sverhältnis)?\s*[=:]\s*{_NUM}",
        rf"übersetzung\s+(?:getriebe)?\s*[=:]\s*{_NUM}(?:\s*:1)?",
        # Portuguese/Spanish
        rf"rela[çc][ãa]o\s+de\s+(?:transmiss[ãa]o|redu[çc][ãa]o)\s*[=:]\s*{_NUM}(?:\s*:1)?",
        rf"relaci[oó]n\s+de\s+(?:transmisi[oó]n|reducci[oó]n)\s*[=:]\s*{_NUM}(?:\s*:1)?",
        # French
        rf"rapport\s+de\s+(?:r[eé]duction|transmission)\s*[=:]\s*{_NUM}(?:\s*:1)?",
    ],

    # ── Worm ratio ───────────────────────────────────────────────────────────
    "supplier_worm_ratio": [
        # English
        rf"worm\s+(?:gear\s+)?ratio\s*[=:]\s*{_NUM}",
        rf"i_?worm\s*[=:]\s*{_NUM}",
        # German
        rf"schnecken(?:rad)?(?:[üu]bersetzung)?\s*[=:]\s*{_NUM}",
        rf"schneckengetriebe(?:[üu]bersetzung)?\s*[=:]\s*{_NUM}",
        # Portuguese/Spanish
        rf"rela[çc][ãa]o\s+(?:da\s+)?(?:coroa\s+e\s+parafuso\s+sem\s+fim|sem\s+fim)\s*[=:]\s*{_NUM}",
        rf"relaci[oó]n\s+(?:del\s+)?(?:tornillo\s+sin\s+fin|husillo)\s*[=:]\s*{_NUM}",
        # French
        rf"rapport\s+(?:de\s+)?vis\s+sans\s+fin\s*[=:]\s*{_NUM}",
    ],

    # ── Gearbox output speed ─────────────────────────────────────────────────
    "gearbox_output_speed": [
        # English
        rf"output\s+speed\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        rf"n_?2\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        # German
        rf"abtriebsdrehzahl\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        rf"ausgangsdrehzahl\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        # Portuguese
        rf"velocidade\s+de\s+sa[íi]da\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        rf"velocidade\s+(?:de\s+saída\s+)?do\s+(?:redutor|motor)\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        # Spanish
        rf"velocidad\s+de\s+salida\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1)",
        # French
        rf"vitesse\s+de\s+sortie\s*[=:]\s*{_NUM}\s*(?:rpm|r/min|min-1|tr/min)",
    ],
}

MOTOR_PARAM_LABELS: dict[str, tuple[str, str]] = {
    "crane_torque_max":            ("Max crane torque M_max",         "Nm"),
    "crane_torque_nom":            ("Nominal crane torque M_Nenn",    "Nm"),
    "motor_speed":                 ("Motor speed",                    "rpm"),
    "motor_rated_torque":          ("Motor rated torque",             "Nm"),
    "starting_factor":             ("Starting factor Ma/Mn",          "×"),
    "supplier_motor_power_kw":     ("Motor power",                    "kW"),
    "supplier_motor_rated_torque": ("Motor rated torque (supplier)",  "Nm"),
    "supplier_motor_starting_torque": ("Motor starting torque",       "Nm"),
    "supplier_gearbox_rated_torque":  ("Gearbox rated torque",        "Nm"),
    "supplier_bevel_ratio":        ("Bevel ratio",                    ""),
    "supplier_worm_ratio":         ("Worm ratio",                     ""),
    "gearbox_output_speed":        ("Gearbox output speed",           "rpm"),
}

_CRANE_TORQUE_FIELDS = {"crane_torque_max", "crane_torque_nom"}


def extract_motor_params(text: str) -> dict[str, float | None]:
    """
    Extract numeric motor and crane parameters from text (any supported language).
    Crane torques stated in kNm are automatically converted to Nm.
    Returns field names matching DrivetrainForm fields.
    """
    text_lower = text.lower()
    result: dict[str, float | None] = {}
    for field, patterns in MOTOR_PARAM_PATTERNS.items():
        found = None
        for pat in patterns:
            m = re.search(pat, text_lower)
            if m:
                try:
                    val = float(m.group(1).replace(",", "."))
                    if field in _CRANE_TORQUE_FIELDS:
                        if re.search(r'knm|kn\.?m', m.group(0)):
                            val *= 1000
                    found = val
                    break
                except (ValueError, IndexError):
                    continue
        result[field] = found
    return result


def extract_motor_params_from_pdf(pdf_path: str) -> dict[str, float | None]:
    """Extract numeric motor/crane parameters from a PDF file."""
    try:
        import pdfplumber  # noqa: F401
    except ImportError:
        return {k: None for k in MOTOR_PARAM_PATTERNS}
    pages: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                pages.append(t)
    return extract_motor_params("\n".join(pages))


def specs_to_form_initial(specs: dict) -> dict:
    """Map extracted spec dict → MotorSpecsForm initial data (empty string for NOT_FOUND)."""
    mapping = {
        'Motor Frame Material':   'spec_frame_material',
        'Input Flange':           'spec_output_flange',
        'Output Shaft':           'spec_shaft',
        'Cooling Method':         'spec_cooling_method',
        'IP Rating':              'spec_ip_rating',
        'Ambient Temperatures':   'spec_ambient_temp',
        'Coating':                'spec_coating',
        'Top Color':              'spec_top_color',
        'Standstill Heater':      'spec_heater',
        'Insulation Class':       'spec_insulation_class',
        'Duty Cycle':             'spec_duty_cycle',
        'Motor Certificate':      'spec_motor_certificate',
        'Efficiency Class':       'spec_efficiency_class',
        'Voltages / Frequencies': 'spec_voltage',
    }
    initial = {}
    for pdf_label, form_field in mapping.items():
        val = specs.get(pdf_label, NOT_FOUND)
        initial[form_field] = '' if val == NOT_FOUND else val

    coating_val = specs.get('Coating', NOT_FOUND)
    initial['spec_painting'] = '' if coating_val == NOT_FOUND else coating_val

    weight_val = specs.get('Weight', NOT_FOUND)
    if weight_val != NOT_FOUND:
        try:
            initial['spec_weight_kg'] = float(weight_val.replace(',', '.'))
        except (ValueError, AttributeError):
            pass

    return initial


def check_compliance(form_data: dict) -> list[dict]:
    """
    Check form field values against required PF crane motor specs.
    Values are expected to already be normalised to English.
    Returns list of {label, required, found, status} where status ∈ PASS/FAIL/UNKNOWN.
    """
    results = []
    for field_key, label, required_display, patterns in _COMPLIANCE_RULES:
        value = (form_data.get(field_key) or '').strip()
        if not value:
            status = 'UNKNOWN'
        else:
            value_lower = value.lower()
            passed = any(re.search(p, value_lower) for p in patterns)
            status = 'PASS' if passed else 'FAIL'
        results.append({
            'label': label,
            'required': required_display,
            'found': value or '—',
            'status': status,
        })
    return results
