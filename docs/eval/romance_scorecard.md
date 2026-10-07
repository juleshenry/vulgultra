<!-- GENERATED FILE: scripts/es_pt_beta.py; do not edit by hand. -->
<!-- source_lects: 36 (es, pt, gl, an, ast, ext, lad, mwl, oc, ca, gsc, fr, wa, pcd, nrf, gallo, frp, lmo, pms, lij, eml, rgn, it, scn, vec, co, ist, dlm, rm, fur, lld, sc, ro, rup, ruo, ruq) -->
<!-- concepts: 213 -->
<!-- candidates_sha256_16: de5c4f8133483c72 -->
<!-- lexicon_sha256_16: a21f0e21447a50da -->
<!-- lexicon_iterations: 499997 -->
<!-- Re-run scripts/run_vulgultra.py or this renderer to refresh. -->
# Vulgultra concept grid — 36 daughter lects

Lexicón de origen mixto: una forma Vulgultra por concepto, elegida
entre candidatos meaning-aligned de las hijas Romance, por rama:

- **ibero:** `es` Spanish, `pt` Portuguese, `gl` Galician, `an` Aragonese, `ast` Asturian, `ext` Extremaduran, `lad` Ladino, `mwl` Mirandese
- **occitano:** `oc` Occitan, `ca` Catalan, `gsc` Gascon
- **oil:** `fr` French, `wa` Walloon, `pcd` Picard, `nrf` Norman, `gallo` Gallo
- **arpitan:** `frp` Franco-Provençal
- **gallo_italian:** `lmo` Lombard, `pms` Piedmontese, `lij` Ligurian, `eml` Emilian, `rgn` Romagnol
- **italo_dalmatian:** `it` Italian, `scn` Sicilian, `vec` Venetan, `co` Corsican, `ist` Istriot, `dlm` Dalmatian
- **rhaeto:** `rm` Romansh, `fur` Friulian, `lld` Ladin
- **sardinian:** `sc` Sardinian
- **eastern:** `ro` Romanian, `rup` Aromanian, `ruo` Istro-Romanian, `ruq` Megleno-Romanian

(36 lects. Latin and English are reserved. ES/PT columns are inspection only.)

## Qué minimiza el SA

Primero se impone el corte legal de σ mínima; dentro de él, el recocido maximiza los segmentos de raíz

$$
E_{root} = -|\Phi_{root}|
E_{morph} = -|\Phi_{root} \cup \Phi_{ending}|
+ 200\sum_e \sigma(e) + 100000\cdot\mathrm{coll} + 2000\cdot\mathrm{viol} + 500\sum_{\mathrm{row}}\max(0,2-d)
$$

| término | peso | qué hace en la práctica |
|---|---:|---|
| **\|Φ_root\|** | −1 | sobre el corte de σ mínima, maximizar los segmentos IPA de las raíces; sin tope |
| σ desinencias | 200 | terminaciones 1σ |
| colisiones | 100000 | duro dentro de una fila |
| fonotáctica | 2000 | resto tras repair |
| distancia desinencias | 500 | dentro de una fila |

Orden: formas legales de σ mínima → maximizar la unión de segmentos IPA observados.

## Veredicto

Frente a **español** y **portugués** (las lenguas de inspección): el mixto tiene **224** sílabas de raíz vs ES 224 y PT 224, con **0** violaciones (ES 0, PT 0).

Frente a **francés**: always-fr suma 224σ con **0** violaciones. El mixto es igual de largo, con 0 violaciones. Italiano suma 224σ (0 viol.).

Calidad del optimizador: greedy-phones Σσ=224 |Φ|=61 E=16539; SA Σσ=224 |Φ|=62 E=16538 (acuerdo con greedy-phones 50/213). El shortest crudo llega a 224σ con 0 violaciones.

Desinencias seleccionadas después de fijar las raíces: tema nominal `lect:an`, tiempos verbales `prs=an/ca/co/ist/an/ist,pst=rm/eml/an/an/sc/an,fut=rm/ca/an/an/grid-inventory/an,subj=rm/gsc/ca/fr/sc/ca,theme_i=rm/ca/an/an/sc/an,theme_a=rm/ca/an/an/sc/an`. Cada tiempo es una fila; el SA de raíces no las mueve.

## Procedencia (raíces SA)

| fuente | raíces | % |
|---|---:|---:|
| `es` | 0 | 0.0% |
| `pt` | 5 | 2.3% |
| `gl` | 2 | 0.9% |
| `an` | 4 | 1.9% |
| `ast` | 1 | 0.5% |
| `ext` | 2 | 0.9% |
| `lad` | 1 | 0.5% |
| `mwl` | 2 | 0.9% |
| `oc` | 5 | 2.3% |
| `ca` | 5 | 2.3% |
| `gsc` | 4 | 1.9% |
| `fr` | 8 | 3.8% |
| `wa` | 18 | 8.5% |
| `pcd` | 15 | 7.0% |
| `nrf` | 8 | 3.8% |
| `gallo` | 10 | 4.7% |
| `frp` | 7 | 3.3% |
| `lmo` | 6 | 2.8% |
| `pms` | 7 | 3.3% |
| `lij` | 5 | 2.3% |
| `eml` | 8 | 3.8% |
| `rgn` | 3 | 1.4% |
| `it` | 0 | 0.0% |
| `scn` | 1 | 0.5% |
| `vec` | 3 | 1.4% |
| `co` | 0 | 0.0% |
| `ist` | 0 | 0.0% |
| `dlm` | 5 | 2.3% |
| `rm` | 12 | 5.6% |
| `fur` | 9 | 4.2% |
| `lld` | 9 | 4.2% |
| `sc` | 2 | 0.9% |
| `ro` | 9 | 4.2% |
| `rup` | 18 | 8.5% |
| `ruo` | 7 | 3.3% |
| `ruq` | 12 | 5.6% |
| **total** | 213 | 100% |

## Totales por política

Las terminaciones de SA se mantienen fijas en las políticas de raíz.
`greedy-phones` es la inicialización voraz por segmentos nuevos; SA recorre el mismo corte de σ mínima.

| política | Σσ raíces | media σ | viol | \|Φ\| | lects (dato) | E_end | E_coll | E_tact | E_dist | E_total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sa | 224 | 1.05 | 0 | 62 | 32 | 10600 | 0 | 6000 | 0 | 16538 |
| greedy-phones | 224 | 1.05 | 0 | 61 | 25 | 10600 | 0 | 6000 | 0 | 16539 |
| shortest | 224 | 1.05 | 0 | 43 | 22 | 10600 | 0 | 6000 | 0 | 16558 |
| always-es | 224 | 1.05 | 0 | 43 | 23 | 10600 | 0 | 6000 | 0 | 16558 |
| always-pt | 224 | 1.05 | 0 | 49 | 22 | 10600 | 0 | 6000 | 0 | 16552 |
| always-fr | 224 | 1.05 | 0 | 43 | 21 | 10600 | 0 | 6000 | 0 | 16558 |
| always-it | 224 | 1.05 | 0 | 43 | 22 | 10600 | 0 | 6000 | 0 | 16558 |
| always-ca | 224 | 1.05 | 0 | 43 | 22 | 10600 | 0 | 6000 | 0 | 16558 |
| always-ro | 224 | 1.05 | 0 | 46 | 22 | 10600 | 0 | 6000 | 0 | 16555 |
| always-gl | 224 | 1.05 | 0 | 43 | 22 | 10600 | 0 | 6000 | 0 | 16558 |
| always-oc | 224 | 1.05 | 0 | 42 | 23 | 10600 | 0 | 6000 | 0 | 16559 |
| init | 224 | 1.05 | 0 | 62 | 25 | 10600 | 0 | 6000 | 0 | 16539 |

Energía inicial reportada por el CLI Rust: **16539** (comparar con SA E_total = 16538).

## Acuerdo

- Conceptos: **213**
- ES y PT adaptados idénticos: 9/213
- SA = ES (ortografía Vulgultra): 7/213
- SA = PT: 10/213
- SA = FR: 23/213
- SA = IT: 0/213
- SA = shortest (crudo): 45/213
- SA = greedy-phones: 50/213
- SA ≠ greedy-phones: 163/213

## Frases de demostración

Con conjugación y concordancia. Artículo **o/a**. Copula 3sg **e**.
Verbo = tema + la fila de presente elegida. El objeto va en acusativo.

### El gato rojo sonríe.

PT: O gato vermelho sorri.

```
Vulgultra  o  gato  r⟨ɔ⟩so  son⟨ɾ⟩ey⟨ɾ⟩a
src    [pt]  [rm]  [rgn]  [lad]
es     el/la  gato  rojo  sonreír
pt     o  gato  vermelho  sorrir
σ      8
```

### El perro es grande.

PT: O cão é grande.

```
Vulgultra  o  ⟨c⟩ano  e  gr⟨ə̃⟩ndo
src    [pt]  [fur]  [pt]  [rgn]
es     el/la  perro  es  grande
pt     o  cão  é  grande
σ      6
```

### El agua es fría.

PT: A água é fria.

```
Vulgultra  a  yawa  e  fr⟨ɛ⟩yda
src    [pt]  [gallo]  [pt]  [pms]
es     el/la  agua  es  frío
pt     a  água  é  frio
σ      6
```

### Yo veo el sol.

PT: Eu vejo o sol.

```
Vulgultra  ⟨ʒ⟩⟨ə⟩  v⟨ɛ⟩⟨ʀ⟩o  o  solon
src    [frp]  [gallo]  [pt]  [vec]
es     yo  ver  el/la  sol
pt     eu  ver  o  sol
σ      6
```

### La mujer come pez.

PT: A mulher come peixe.

```
Vulgultra  a  f⟨ɛ⟩ma  m⟨ə⟩ka  peskon
src    [pt]  [wa]  [rup]  [fur]
es     el/la  mujer  comer  pez
pt     a  mulher  comer  peixe
σ      7
```

### El fuego es rojo.

PT: O fogo é vermelho.

```
Vulgultra  o  fuko  e  r⟨ɔ⟩so
src    [pt]  [fur]  [pt]  [rgn]
es     el/la  fuego  es  rojo
pt     o  fogo  é  vermelho
σ      6
```

### Nosotros damos agua.

PT: Nós damos água.

```
Vulgultra  nus  dem  yawan
src    [rm]  [lld]  [gallo]
es     nosotros  dar  agua
pt     nós  dar  água
σ      4
```

### El hombre es bueno.

PT: O homem é bom.

```
Vulgultra  o  ⟨ɔ⟩mo  e  bo
src    [pt]  [wa]  [pt]  [gl]
es     el/la  hombre  es  bueno
pt     o  homem  é  bom
σ      5
```

### La noche es negra.

PT: A noite é preta.

```
Vulgultra  a  n⟨ø⟩yta  e  n⟨ɛ⟩⟨ʀ⟩a
src    [pt]  [pms]  [pt]  [frp]
es     el/la  noche  es  negro
pt     a  noite  é  preto
σ      6
```

### Tú oyes el viento.

PT: Tu ouves o vento.

```
Vulgultra  t⟨ə⟩  ⟨õ⟩⟨ʀ⟩i  o  venon
src    [frp]  [wa]  [pt]  [gsc]
es     tú  oír  el/la  viento
pt     tu  ouvir  o  vento
σ      6
```

## Género (sustantivos pueden mezclar fuentes; verbos no)

Par masculino/femenino elegido por sílabas, independiente.
Ejemplo permitido: M `gat` [ca] + F `chatte` [fr].
El tema léxico del verbo es uno. Cada tiempo elige su propia fila de personas.

| glosa | M Vulgultra | src | σ | F Vulgultra | src | σ |
|---|---|---|---:|---|---|---:|
| gato | **gat** | `rm` | 1 | **kat** | `wa` | 1 |
| perro | **⟨c⟩an** | `fur` | 1 | **l⟨ɛ⟩x** | `wa` | 1 |

## Tabla por concepto

| glosa | es | pt | fr | it | ca | Vulgultra | src | σ | por qué | bin |
|---|---|---|---|---|---|---|---|---:|---|---|
| a | a | a | à | a | a | **⟨ə⟩** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| afilado | afilado | afiado | aigu | affilato | esmolat | **xpi⟨t͡s⟩** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | — |
| agua | agua | água | eau | acqua | aigua | **yaw** | `gallo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| ala | ala | asa | aile | ala | ala | **a** | `gl` | 1 | σ=1; desempate por segmentos del léxico global | — |
| algunos | algunos | alguns | quelques | alcuni | alguns | **k⟨ə⟩k** | `gallo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| allí | allí | ali | là | lì | allà | **la** | `gallo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| amarillo | amarillo | amarelo | jaune | giallo | groc | **⟨ʒ⟩ut** | `ruo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| ancho | ancho | largo | large | largo | ample | **lar⟨ɟ⟩** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | — |
| animal | animal | animal | animal | animale | animal | **by⟨ɛ⟩s** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| apretar | apretar | apertar | presser | spremere | prémer | **strenc** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | — |
| apuñalar | apuñalar | esfaquear | poignarder | pugnalare | apunyalar | **pung** | `ruq` | 1 | única legal a σ=1 | — |
| aquí | aquí | aqui | ici | qui | aquí | **kwa** | `vec` | 1 | σ=1; desempate por segmentos del léxico global | — |
| arena | arena | areia | sable | sabbia | sorra | **sab** | `pcd` | 1 | única legal a σ=1 | — |
| atar | atar | atar | lier | legare | lligar | **leg** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| año | año | ano | année | anno | any | **an** | `gsc` | 1 | σ=1; desempate por segmentos del léxico global | — |
| beber | beber | beber | boire | bere | beure | **b⟨ɛ⟩⟨ʀ⟩** | `gallo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| blanco | blanco | branco | blanc | bianco | blanc | **bla⟨ŋ⟩k** | `oc` | 1 | σ=1; desempate por segmentos del léxico global | — |
| boca | boca | boca | bouche | bocca | boca | **bux** | `nrf` | 1 | σ=1; desempate por segmentos del léxico global | — |
| bosque | bosque | floresta | forêt | foresta | bosc | **bu** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| bueno | bueno | bom | bon | buono | bo | **bo** | `gl` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| cabeza | cabeza | cabeça | tête | testa | cap | **kap** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| caer | caer | cair | tomber | cadere | caure | **kad** | `ruq` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| caliente | caliente | quente | chaud | caldo | calent | **kald** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| caminar | caminar | andar | marcher | camminare | caminar | **ir** | `rm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| camino | camino | estrada | route | strada | camí | **stra** | `pms` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cantar | cantar | cantar | chanter | cantare | cantar | **kont** | `ruq` | 1 | única legal a σ=1 | — |
| carne | carne | carne | viande | carne | carn | **c⟨ɔ⟩** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cavar | cavar | cavar | creuser | scavare | cavar | **fwi** | `gallo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cazar | cazar | caçar | chasser | cacciare | caçar | **kasa⟨ɾ⟩** | `pt` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| ceniza | ceniza | cinza | cendre | cenere | cendra | **s⟨ɑ̃⟩t** | `gallo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cerca | cerca | perto | près | vicino | prop | **p⟨ʀ⟩e** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| chupar | chupar | chupar | sucer | succhiare | xuclar | **sug** | `rup` | 1 | única legal a σ=1 | — |
| cielo | cielo | céu | ciel | cielo | cel | **cer** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| cinco | cinco | cinco | cinq | cinque | cinc | **x⟨ɔ̃⟩k** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cola | cola | rabo | queue | coda | cua | **kwa** | `oc` | 1 | σ=1; desempate por segmentos del léxico global | — |
| comer | comer | comer | manger | mangiare | menjar | **m⟨ə⟩k** | `rup` | 1 | única legal a σ=1 | — |
| con | con | com | avec | con | amb | **kont** | `lmo` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| congelar | congelar | congelar | geler | gelare | gelar | **⟨ð⟩l⟨ɛ⟩r** | `eml` | 1 | única legal a σ=1 | — |
| contar | contar | contar | compter | contare | comptar | **kontal** | `ext` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| corazón | corazón | coração | cœur | cuore | cor | **k⟨ø⟩r** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | — |
| correcto | correcto | correto | correct | corretto | correcte | **⟨ʒ⟩⟨y⟩st** | `nrf` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cortar | cortar | cortar | couper | tagliare | tallar | **taly** | `ruq` | 1 | única legal a σ=1 | — |
| corteza | corteza | casca | écorce | corteccia | escorça | **skwas** | `wa` | 1 | única legal a σ=1 | — |
| corto | corto | curto | court | corto | curt | **ku⟨ʀ⟩** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| coser | coser | costurar | coudre | cucire | cosir | **kos** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cuatro | cuatro | quatro | quatre | quattro | quatre | **kwat** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cuello | cuello | pescoço | cou | collo | coll | **ku** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cuerda | cuerda | corda | corde | corda | corda | **k⟨ɔ⟩⟨ʀ⟩d** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cuerno | cuerno | chifre | corne | corno | banya | **k⟨ɔ⟩⟨ɾ⟩** | `gsc` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cuándo | cuándo | quando | quand | quando | quan | **kwand** | `lmo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cómo | cómo | como | comment | come | com | **kal** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| dar | dar | dar | donner | dare | donar | **de** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| decir | decir | dizer | dire | dire | dir | **dir** | `rm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| delgado | delgado | fino | mince | sottile | prim | **fen** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | — |
| derecha | derecha | direita | droite | destra | dreta | **d⟨ʀ⟩et** | `nrf` | 1 | σ=1; desempate por segmentos del léxico global | — |
| diente | diente | dente | dent | dente | dent | **d⟨ɑ̃⟩** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| dormir | dormir | dormir | dormir | dormire | dormir | **dorm** | `ruq` | 1 | única legal a σ=1 | — |
| dos | dos | dois | deux | due | dos | **doy** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| día | día | dia | jour | giorno | dia | **⟨d͡z⟩w⟨ə⟩** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| dónde | dónde | onde | où | dove | on | **an** | `an` | 1 | σ=1; desempate por segmentos del léxico global | — |
| el | el | o | le | il | el | **⟨ə⟩l** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| ellos | ellos | eles | ils | loro | ells | **lor** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | — |
| empujar | empujar | empurrar | pousser | spingere | empènyer | **sping** | `lmo` | 1 | única legal a σ=1 | — |
| en | en | em | dans | in | en | **i⟨ŋ⟩** | `lij` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| entrañas | entrañas | tripas | entrailles | viscere | budells | **bw⟨ɛ⟩l** | `frp` | 1 | única legal a σ=1 | — |
| escupir | escupir | cuspir | cracher | sputare | escopir | **skwip** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| eso | eso | isso | cela | quello | aquell | **kul** | `pms` | 1 | σ=1; desempate por segmentos del léxico global | — |
| espalda | espalda | costas | dos | schiena | esquena | **do** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| esposa | esposa | esposa | épouse | moglie | muller | **f⟨ɑ⟩m** | `nrf` | 1 | σ=1; desempate por segmentos del léxico global | — |
| esposo | esposo | marido | mari | marito | marit | **om** | `ruo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| esto | esto | isto | ceci | questo | aquest | **kust** | `pms` | 1 | σ=1; desempate por segmentos del léxico global | — |
| estrecho | estrecho | estreito | étroit | stretto | estret | **xtre⟨t͡ɕ⟩** | `rm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| estrella | estrella | estrela | étoile | stella | estrella | **stya** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | — |
| flor | flor | flor | fleur | fiore | flor | **flo⟨ɾ⟩** | `ext` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| flotar | flotar | flutuar | flotter | galleggiare | flotar | **flotar** | `rm` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| fluir | fluir | fluir | couler | fluire | fluir | **flwi⟨ɾ⟩** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| frotar | frotar | esfregar | frotter | strofinare | fregar | **frek** | `rup` | 1 | única legal a σ=1 | — |
| fruta | fruta | fruta | fruit | frutto | fruita | **f⟨ʀ⟩⟨ɥ⟩i** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| frío | frío | frio | froid | freddo | fred | **fr⟨ɛ⟩yd** | `pms` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| fuego | fuego | fogo | feu | fuoco | foc | **fuk** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | — |
| gata | gata | gata | chatte | gatta | gata | **kat** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| gato | gato | gato | chat | gatto | gat | **gat** | `rm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| girar | girar | girar | tourner | girare | girar | **gya** | `lij` | 1 | única legal a σ=1 | — |
| golpear | golpear | bater | frapper | colpire | pegar | **bat** | `lmo` | 1 | única legal a σ=1 | — |
| grande | grande | grande | grand | grande | gran | **gr⟨ə̃⟩nd** | `rgn` | 1 | σ=1; desempate por segmentos del léxico global | — |
| grasa | grasa | gordura | graisse | grasso | greix | **m⟨ɒ⟩st** | `ruo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| grueso | grueso | grosso | épais | spesso | gruixut | **gros** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | — |
| gusano | gusano | verme | ver | verme | cuc | **v⟨ɛ⟩⟨ʀ⟩m** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | — |
| hielo | hielo | gelo | glace | ghiaccio | gel | **⟨d͡ʒ⟩a⟨θ⟩** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | — |
| hierba | hierba | erva | herbe | erba | herba | **⟨ɛ⟩⟨ʀ⟩b** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| hinchar | hinchar | inchar | enfler | gonfiare | inflar | **⟨ĩ⟩xa⟨ɾ⟩** | `pt` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| hoja | hoja | folha | feuille | foglia | fulla | **f⟨œ⟩l** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| hombre | hombre | homem | homme | uomo | home | **⟨ɔ⟩m** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| hueso | hueso | osso | os | osso | os | **os** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| huevo | huevo | ovo | œuf | uovo | ou | **ow** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| humo | humo | fumo | fumée | fumo | fum | **⟨h⟩⟨y⟩n** | `gsc` | 1 | σ=1; desempate por segmentos del léxico global | — |
| hígado | hígado | fígado | foie | fegato | fetge | **fwa** | `nrf` | 1 | σ=1; desempate por segmentos del léxico global | — |
| izquierda | izquierda | esquerda | gauche | sinistra | esquerra | **gox** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| jugar | jugar | jogar | jouer | giocare | jugar | **⟨d͡ʒ⟩yok** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| lago | lago | lago | lac | lago | llac | **lak** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | — |
| lanzar | lanzar | atirar | jeter | lanciare | llançar | **tya** | `lij` | 1 | σ=1; desempate por segmentos del léxico global | — |
| largo | largo | longo | long | lungo | llarg | **lung** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | — |
| lavar | lavar | lavar | laver | lavare | rentar | **spel** | `rup` | 1 | única legal a σ=1 | — |
| lejos | lejos | longe | loin | lontano | lluny | **lyuny** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| lengua | lengua | língua | langue | lingua | llengua | **l⟨ɛ̃⟩w** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| liso | liso | liso | lisse | liscio | llis | **lyix** | `rm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| lleno | lleno | cheio | plein | pieno | ple | **pl⟨ɛ⟩** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| lluvia | lluvia | chuva | pluie | pioggia | pluja | **pli** | `nrf` | 1 | σ=1; desempate por segmentos del léxico global | — |
| luna | luna | lua | lune | luna | lluna | **l⟨ɛ⟩n** | `gallo` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| madre | madre | mãe | mère | madre | mare | **may** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| malo | malo | mau | mauvais | cattivo | dolent | **r⟨æ⟩v** | `ruo` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| mano | mano | mão | main | mano | mà | **m⟨ɐ̃⟩w** | `pt` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| mar | mar | mar | mer | mare | mar | **ma⟨ɾ⟩** | `pt` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| matar | matar | matar | tuer | uccidere | matar | **t⟨ɥ⟩e** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| mojado | mojado | molhado | mouillé | bagnato | mullat | **k⟨ʀ⟩⟨y⟩** | `gallo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| montaña | montaña | montanha | montagne | montagna | muntanya | **mont** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | — |
| morder | morder | morder | mordre | mordere | mossegar | **m⟨ɔ⟩⟨ʀ⟩d** | `pcd` | 1 | única legal a σ=1 | — |
| morir | morir | morrer | mourir | morire | morir | **mwi** | `lij` | 1 | σ=1; desempate por segmentos del léxico global | — |
| muchos | muchos | muitos | beaucoup | molti | molts | **mul⟨t͡sʲ⟩** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | — |
| mujer | mujer | mulher | femme | donna | dona | **f⟨ɛ⟩m** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| nadar | nadar | nadar | nager | nuotare | nedar | **nwe** | `pms` | 1 | única legal a σ=1 | — |
| nariz | nariz | nariz | nez | naso | nas | **nas** | `oc` | 1 | σ=1; desempate por segmentos del léxico global | — |
| negro | negro | preto | noir | nero | negre | **n⟨ɛ⟩⟨ʀ⟩** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | — |
| niebla | niebla | nevoeiro | brouillard | nebbia | boira | **n⟨ɛ⟩bya** | `eml` | 2 | σ=2; desempate por segmentos del léxico global | adivinable |
| nieve | nieve | neve | neige | neve | neu | **n⟨ɛ⟩⟨ʒ⟩** | `gallo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| niño | niño | criança | enfant | bambino | nen | **frut** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | — |
| no | no | não | non | non | no | **be⟨t͡ɕ⟩** | `rm` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| noche | noche | noite | nuit | notte | nit | **n⟨ø⟩yt** | `pms` | 1 | σ=1; desempate por segmentos del léxico global | — |
| nombre | nombre | nome | nom | nome | nom | **n⟨ɔ⟩m** | `pms` | 1 | σ=1; desempate por segmentos del léxico global | — |
| nosotros | nosotros | nós | nous | noi | nosaltres | **nus** | `rm` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| nube | nube | nuvem | nuage | nuvola | núvol | **nor** | `ruq` | 1 | σ=1; desempate por segmentos del léxico global | — |
| nuevo | nuevo | novo | nouveau | nuovo | nou | **n⟨ɔ⟩w** | `oc` | 1 | σ=1; desempate por segmentos del léxico global | — |
| ojo | ojo | olho | œil | occhio | ull | **yi** | `nrf` | 1 | σ=1; desempate por segmentos del léxico global | — |
| oler | oler | cheirar | sentir | odorare | ensumar | **gole⟨ɾ⟩** | `ast` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| oreja | oreja | orelha | oreille | orecchio | orella | **reca** | `vec` | 2 | σ=2; desempate por segmentos del léxico global | — |
| otro | otro | outro | autre | altro | altre | **alt** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | — |
| oír | oír | ouvir | entendre | sentire | sentir | **⟨õ⟩⟨ʀ⟩** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| padre | padre | pai | père | padre | pare | **pay** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| palo | palo | pau | bâton | bastone | pal | **stal** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| parar | parar | ficar | tenir | stare | estar | **xte** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | — |
| partir | partir | fender | fendre | spaccare | fendre | **f⟨ɛ̃⟩t** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pecho | pecho | peito | sein | petto | pit | **s⟨ɨ⟩n** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pelear | pelear | lutar | combattre | combattere | lluitar | **bat** | `wa` | 1 | única legal a σ=1 | — |
| pelo | pelo | cabelo | cheveu | capello | cabell | **per** | `ruo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pensar | pensar | pensar | penser | pensare | pensar | **p⟨ẽ⟩sa⟨ɾ⟩** | `mwl` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| pequeño | pequeño | pequeno | petit | piccolo | petit | **mik** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | — |
| perra | perra | cadela | chienne | cagna | gossa | **l⟨ɛ⟩x** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| perro | perro | cão | chien | cane | gos | **⟨c⟩an** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| persona | persona | pessoa | personne | persona | persona | **⟨d͡ʒ⟩in** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pesado | pesado | pesado | lourd | pesante | pesat | **lu⟨ʀ⟩** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pez | pez | peixe | poisson | pesce | peix | **pesk** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| pie | pie | pé | pied | piede | peu | **pe** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| piedra | piedra | pedra | pierre | pietra | pedra | **py⟨ɛ⟩⟨ʀ⟩** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| piel | piel | pele | peau | pelle | pell | **po** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| pierna | pierna | perna | jambe | gamba | cama | **⟨d͡ʒ⟩⟨ɑ̃⟩p** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| piojo | piojo | piolho | pou | pidocchio | poll | **pyuly** | `oc` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pluma | pluma | pena | plume | piuma | ploma | **pl⟨ɔ⟩m** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pocos | pocos | poucos | peu | pochi | pocs | **pok** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | — |
| podrido | podrido | podre | pourri | marcio | podrit | **mar⟨t͡s⟩** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | — |
| polvo | polvo | pó | poussière | polvere | pols | **praw** | `ruq` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| porque | porque | porque | car | perché | perquè | **ka** | `sc` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pájaro | pájaro | pássaro | oiseau | uccello | ocell | **puly** | `ruo` | 1 | única legal a σ=1 | — |
| quemar | quemar | queimar | brûler | bruciare | cremar | **ard** | `rup` | 1 | única legal a σ=1 | — |
| quién | quién | quem | qui | chi | qui | **⟨t͡ɕ⟩i** | `rm` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| qué | qué | que | quoi | che | què | **ki** | `scn` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| rascar | rascar | coçar | gratter | grattare | gratar | **zgayr** | `ruq` | 1 | única legal a σ=1 | — |
| raíz | raíz | raiz | racine | radice | arrel | **⟨ʁ⟩ayx** | `pt` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| recto | recto | direito | droit | dritto | recte | **d⟨ʀ⟩⟨ɛ⟩** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | — |
| redondo | redondo | redondo | rond | rotondo | rodó | **t⟨ʌ⟩nd** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | — |
| respirar | respirar | respirar | respirer | respirare | respirar | **fyutar** | `dlm` | 2 | σ=2; desempate por segmentos del léxico global | — |
| reír | reír | rir | rire | ridere | riure | **⟨ʀ⟩i⟨ʀ⟩** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| rodilla | rodilla | joelho | genou | ginocchio | genoll | **⟨d͡ʒ⟩enun⟨kʲ⟩** | `ro` | 2 | σ=2; desempate por segmentos del léxico global | opaco |
| rojo | rojo | vermelho | rouge | rosso | roig | **r⟨ɔ⟩s** | `rgn` | 1 | σ=1; desempate por segmentos del léxico global | — |
| romo | romo | cego | émoussé | smussato | rom | **xtus** | `rm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| río | río | rio | rivière | fiume | riu | **fy⟨ũ⟩** | `rgn` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| saber | saber | saber | savoir | sapere | saber | **styu** | `ruq` | 1 | σ=1; desempate por segmentos del léxico global | — |
| sal | sal | sal | sel | sale | sal | **sal** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| sangre | sangre | sangue | sang | sangue | sang | **sonk** | `rm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| secar | secar | enxugar | essuyer | asciugare | eixugar | **xterg** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| seco | seco | seco | sec | secco | sec | **s⟨ɛ⟩k** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| semilla | semilla | semente | graine | seme | llavor | **grun** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| sentar | sentar | sentar | asseoir | sedere | seure | **xed** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| ser | ser | ser | être | essere | ser | **⟨ɛ⟩s** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| serpiente | serpiente | serpente | serpent | serpente | serp | **xerp** | `ruo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| si | si | se | si | se | si | **si** | `sc` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| sol | sol | sol | soleil | sole | sol | **sol** | `vec` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| sonreír | sonreír | sorrir | sourire | sorridere | somriure | **son⟨ɾ⟩ey⟨ɾ⟩** | `lad` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| soplar | soplar | soprar | souffler | soffiare | bufar | **sfya** | `lmo` | 1 | única legal a σ=1 | — |
| sucio | sucio | sujo | sale | sporco | brut | **spwark** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| temer | temer | temer | craindre | temere | témer | **k⟨ʀ⟩⟨ɛ̃⟩d** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| tener | tener | ter | tenir | tenere | tenir | **⟨t͡s⟩on** | `ruq` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| tierra | tierra | terra | terre | terra | terra | **te⟨ð⟩** | `nrf` | 1 | σ=1; desempate por segmentos del léxico global | — |
| tirar | tirar | puxar | tirer | tirare | estirar | **trag** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| todo | todo | todo | tout | tutto | tot | **tut** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| tres | tres | três | trois | tre | tres | **trey** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| tú | tú | tu | tu | tu | tu | **t⟨ə⟩** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| uno | uno | um | un | uno | un | **⟨œ̃⟩** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| uña | uña | unha | ongle | unghia | ungla | **⟨ɔ̃⟩g** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | — |
| venir | venir | vir | venir | venire | venir | **vnyir** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| ver | ver | ver | voir | vedere | veure | **v⟨ɛ⟩⟨ʀ⟩** | `gallo` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| verde | verde | verde | vert | verde | verd | **v⟨ɐ⟩rt** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | — |
| viejo | viejo | velho | vieux | vecchio | vell | **vi** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| viento | viento | vento | vent | vento | vent | **ven** | `gsc` | 1 | σ=1; desempate por segmentos del léxico global | — |
| vientre | vientre | ventre | ventre | pancia | ventre | **v⟨ɛ̃⟩t** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| vivir | vivir | viver | vivre | vivere | viure | **viv** | `lmo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| volar | volar | voar | voler | volare | volar | **⟨ʒ⟩wa** | `lij` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| vomitar | vomitar | vomitar | vomir | vomitare | vomitar | **vom** | `ruq` | 1 | única legal a σ=1 | — |
| vosotros | vosotros | vocês | vous | voi | vosaltres | **vus** | `rm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| y | y | e | et | e | i | **i** | `mwl` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| yacer | yacer | jazer | gésir | giacere | jeure | **kulk** | `ruq` | 1 | σ=1; desempate por segmentos del léxico global | — |
| yo | yo | eu | je | io | jo | **⟨ʒ⟩⟨ə⟩** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| árbol | árbol | árvore | arbre | albero | arbre | **⟨ɔ⟩p** | `wa` | 1 | σ=1; desempate por segmentos del léxico global | — |
| él | él | ele | il | lui | ell | **⟨ɐ⟩l** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | transparente |

## Apéndice: SA ≠ greedy-phones

| glosa | SA | src | σ | greedy-phones | src | σ | razón |
|---|---|---|---:|---|---|---:|---|
| a | ⟨ə⟩ | `ca` | 1 | a | `an` | 1 | misma σ, otra forma |
| agua | yaw | `gallo` | 1 | o | `fr` | 1 | misma σ, otra forma |
| ala | a | `gl` | 1 | yal | `dlm` | 1 | misma σ, otra forma |
| algunos | k⟨ə⟩k | `gallo` | 1 | ka⟨ʀ⟩k | `frp` | 1 | misma σ, otra forma |
| allí | la | `gallo` | 1 | ci | `co` | 1 | misma σ, otra forma |
| amarillo | ⟨ʒ⟩ut | `ruo` | 1 | g⟨ɾ⟩⟨ɔ⟩k | `ca` | 1 | misma σ, otra forma |
| animal | by⟨ɛ⟩s | `wa` | 1 | b⟨ɛ⟩t | `nrf` | 1 | misma σ, otra forma |
| aquí | kwa | `vec` | 1 | kawk | `dlm` | 1 | misma σ, otra forma |
| atar | leg | `rup` | 1 | lye | `fr` | 1 | misma σ, otra forma |
| año | an | `gsc` | 1 | any | `ca` | 1 | misma σ, otra forma |
| beber | b⟨ɛ⟩⟨ʀ⟩ | `gallo` | 1 | bar | `dlm` | 1 | misma σ, otra forma |
| blanco | bla⟨ŋ⟩k | `oc` | 1 | bla⟨ŋ⟩ | `ca` | 1 | misma σ, otra forma |
| boca | bux | `nrf` | 1 | bux | `fr` | 1 | misma σ, otra forma |
| bosque | bu | `pcd` | 1 | b⟨ɔ⟩sk | `ca` | 1 | misma σ, otra forma |
| bueno | bo | `gl` | 1 | b⟨ɔ⟩ | `ca` | 1 | misma σ, otra forma |
| cabeza | kap | `rup` | 1 | kap | `ca` | 1 | misma σ, otra forma |
| caer | kad | `ruq` | 1 | x⟨ɛ⟩⟨ʀ⟩ | `gallo` | 1 | misma σ, otra forma |
| caliente | kald | `rup` | 1 | kwald | `dlm` | 1 | misma σ, otra forma |
| caminar | ir | `rm` | 1 | yi | `lld` | 1 | misma σ, otra forma |
| camino | stra | `pms` | 1 | str⟨ɛ⟩ | `eml` | 1 | misma σ, otra forma |
| carne | c⟨ɔ⟩ | `wa` | 1 | karn | `ca` | 1 | misma σ, otra forma |
| cazar | kasa⟨ɾ⟩ | `pt` | 2 | ka⟨θ⟩a⟨ɾ⟩ | `an` | 2 | misma σ, otra forma |
| cerca | p⟨ʀ⟩e | `pcd` | 1 | p⟨ɾ⟩⟨ɔ⟩p | `ca` | 1 | misma σ, otra forma |
| cielo | cer | `ro` | 1 | s⟨ɛ⟩l | `ca` | 1 | misma σ, otra forma |
| cinco | x⟨ɔ̃⟩k | `pcd` | 1 | s⟨ẽ⟩k | `wa` | 1 | misma σ, otra forma |
| cola | kwa | `oc` | 1 | kw⟨ə⟩ | `ca` | 1 | misma σ, otra forma |
| con | kont | `lmo` | 1 | kon | `an` | 1 | misma σ, otra forma |
| contar | kontal | `ext` | 2 | konta⟨ɾ⟩ | `an` | 2 | misma σ, otra forma |
| corazón | k⟨ø⟩r | `lld` | 1 | k⟨ɔ⟩r | `ca` | 1 | misma σ, otra forma |
| correcto | ⟨ʒ⟩⟨y⟩st | `nrf` | 1 | drat | `dlm` | 1 | misma σ, otra forma |
| corto | ku⟨ʀ⟩ | `wa` | 1 | kurt | `ca` | 1 | misma σ, otra forma |
| coser | kos | `rup` | 1 | c⟨ø⟩d | `pcd` | 1 | misma σ, otra forma |
| cuatro | kwat | `pcd` | 1 | kat | `nrf` | 1 | misma σ, otra forma |
| cuello | ku | `pcd` | 1 | k⟨ɔ⟩ly | `ca` | 1 | misma σ, otra forma |
| cuerda | k⟨ɔ⟩⟨ʀ⟩d | `pcd` | 1 | k⟨ɔ⟩⟨ʀ⟩d | `fr` | 1 | misma σ, otra forma |
| cuerno | k⟨ɔ⟩⟨ɾ⟩ | `gsc` | 1 | k⟨ɔ⟩⟨ʀ⟩n | `fr` | 1 | misma σ, otra forma |
| cuándo | kwand | `lmo` | 1 | kwan | `an` | 1 | misma σ, otra forma |
| cómo | kal | `dlm` | 1 | k⟨ɔ⟩m | `ca` | 1 | misma σ, otra forma |
| dar | de | `lld` | 1 | da⟨ɾ⟩ | `an` | 1 | misma σ, otra forma |
| decir | dir | `rm` | 1 | di | `ca` | 1 | misma σ, otra forma |
| delgado | fen | `eml` | 1 | p⟨ɾ⟩im | `ca` | 1 | misma σ, otra forma |
| derecha | d⟨ʀ⟩et | `nrf` | 1 | d⟨ʀ⟩⟨ɛ⟩ | `frp` | 1 | misma σ, otra forma |
| diente | d⟨ɑ̃⟩ | `fr` | 1 | den | `ca` | 1 | misma σ, otra forma |
| dos | doy | `lld` | 1 | dos | `an` | 1 | misma σ, otra forma |
| el | ⟨ə⟩l | `ca` | 1 | o | `an` | 1 | misma σ, otra forma |
| ellos | lor | `eml` | 1 | els | `an` | 1 | misma σ, otra forma |
| en | i⟨ŋ⟩ | `lij` | 1 | en | `an` | 1 | misma σ, otra forma |
| escupir | skwip | `rup` | 1 | spoyt | `dlm` | 1 | misma σ, otra forma |
| eso | kul | `pms` | 1 | kol | `dlm` | 1 | misma σ, otra forma |
| espalda | do | `pcd` | 1 | dwas | `dlm` | 1 | misma σ, otra forma |
| esposa | f⟨ɑ⟩m | `nrf` | 1 | mwir | `fur` | 1 | misma σ, otra forma |
| esposo | om | `ruo` | 1 | mar | `fur` | 1 | misma σ, otra forma |
| esto | kust | `pms` | 1 | kost | `dlm` | 1 | misma σ, otra forma |
| estrella | stya | `ro` | 1 | st⟨æ⟩ | `ruo` | 1 | misma σ, otra forma |
| flor | flo⟨ɾ⟩ | `ext` | 1 | flo⟨ɾ⟩ | `an` | 1 | misma σ, otra forma |
| flotar | flotar | `rm` | 2 | flota⟨ɾ⟩ | `an` | 2 | misma σ, otra forma |
| fruta | f⟨ʀ⟩⟨ɥ⟩i | `fr` | 1 | froyt | `dlm` | 1 | misma σ, otra forma |
| frío | fr⟨ɛ⟩yd | `pms` | 1 | f⟨ɾ⟩yo | `an` | 1 | misma σ, otra forma |
| fuego | fuk | `fur` | 1 | fwew | `ast` | 1 | misma σ, otra forma |
| gata | kat | `wa` | 1 | xat | `fr` | 1 | misma σ, otra forma |
| gato | gat | `rm` | 1 | gat | `ca` | 1 | misma σ, otra forma |
| grasa | m⟨ɒ⟩st | `ruo` | 1 | g⟨ɾ⟩ex | `ca` | 1 | misma σ, otra forma |
| grueso | gros | `fur` | 1 | days | `dlm` | 1 | misma σ, otra forma |
| gusano | v⟨ɛ⟩⟨ʀ⟩m | `frp` | 1 | kuk | `ca` | 1 | misma σ, otra forma |
| hielo | ⟨d͡ʒ⟩a⟨θ⟩ | `eml` | 1 | ⟨ʒ⟩⟨ɛ⟩l | `ca` | 1 | misma σ, otra forma |
| hierba | ⟨ɛ⟩⟨ʀ⟩b | `pcd` | 1 | ⟨ɛ⟩⟨ʀ⟩b | `fr` | 1 | misma σ, otra forma |
| hoja | f⟨œ⟩l | `pcd` | 1 | f⟨œ⟩y | `fr` | 1 | misma σ, otra forma |
| hombre | ⟨ɔ⟩m | `wa` | 1 | ⟨ɔ⟩m | `fr` | 1 | misma σ, otra forma |
| hueso | os | `rup` | 1 | ⟨ɔ⟩s | `ca` | 1 | misma σ, otra forma |
| huevo | ow | `rup` | 1 | ⟨ɔ⟩w | `ca` | 1 | misma σ, otra forma |
| humo | ⟨h⟩⟨y⟩n | `gsc` | 1 | f⟨œ̃⟩ | `frp` | 1 | misma σ, otra forma |
| hígado | fwa | `nrf` | 1 | fwa | `fr` | 1 | misma σ, otra forma |
| izquierda | gox | `fr` | 1 | ⟨h⟩⟨ɛ̃⟩c | `wa` | 1 | misma σ, otra forma |
| jugar | ⟨d͡ʒ⟩yok | `rup` | 1 | ⟨ʒ⟩⟨ɥ⟩e | `pcd` | 1 | misma σ, otra forma |
| lago | lak | `fur` | 1 | lyak | `ca` | 1 | misma σ, otra forma |
| lanzar | tya | `lij` | 1 | tr⟨ɛ⟩r | `eml` | 1 | misma σ, otra forma |
| largo | lung | `ro` | 1 | lyark | `ca` | 1 | misma σ, otra forma |
| lengua | l⟨ɛ̃⟩w | `wa` | 1 | l⟨ɑ̃⟩g | `fr` | 1 | misma σ, otra forma |
| liso | lyix | `rm` | 1 | lyis | `ca` | 1 | misma σ, otra forma |
| lleno | pl⟨ɛ⟩ | `ca` | 1 | plen | `an` | 1 | misma σ, otra forma |
| lluvia | pli | `nrf` | 1 | pl⟨ø⟩v | `pcd` | 1 | misma σ, otra forma |
| luna | l⟨ɛ⟩n | `gallo` | 1 | l⟨y⟩n | `fr` | 1 | misma σ, otra forma |
| madre | may | `an` | 1 | m⟨ɐ̃⟩y | `pt` | 1 | misma σ, otra forma |
| malo | r⟨æ⟩v | `ruo` | 1 | ri | `dlm` | 1 | misma σ, otra forma |
| mano | m⟨ɐ̃⟩w | `pt` | 1 | man | `an` | 1 | misma σ, otra forma |
| mar | ma⟨ɾ⟩ | `pt` | 1 | ma⟨ɾ⟩ | `an` | 1 | misma σ, otra forma |
| mojado | k⟨ʀ⟩⟨y⟩ | `gallo` | 1 | yoyt | `dlm` | 1 | misma σ, otra forma |
| montaña | mont | `fur` | 1 | mwant | `dlm` | 1 | misma σ, otra forma |
| muchos | mul⟨t͡sʲ⟩ | `ro` | 1 | tan⟨c⟩ | `fur` | 1 | misma σ, otra forma |
| mujer | f⟨ɛ⟩m | `wa` | 1 | f⟨ɑ⟩m | `nrf` | 1 | misma σ, otra forma |
| nariz | nas | `oc` | 1 | nas | `ca` | 1 | misma σ, otra forma |
| negro | n⟨ɛ⟩⟨ʀ⟩ | `frp` | 1 | fox | `dlm` | 1 | misma σ, otra forma |
| niebla | n⟨ɛ⟩bya | `eml` | 2 | boy⟨ɾ⟩a | `an` | 2 | misma σ, otra forma |
| nieve | n⟨ɛ⟩⟨ʒ⟩ | `gallo` | 1 | nyew | `an` | 1 | misma σ, otra forma |
| niño | frut | `fur` | 1 | n⟨ɛ⟩n | `ca` | 1 | misma σ, otra forma |
| no | be⟨t͡ɕ⟩ | `rm` | 1 | no | `an` | 1 | misma σ, otra forma |
| noche | n⟨ø⟩yt | `pms` | 1 | nweyt | `an` | 1 | misma σ, otra forma |
| nombre | n⟨ɔ⟩m | `pms` | 1 | n⟨ɔ⟩m | `ca` | 1 | misma σ, otra forma |
| nosotros | nus | `rm` | 1 | noy | `co` | 1 | misma σ, otra forma |
| nube | nor | `ruq` | 1 | n⟨ɥ⟩a⟨ʒ⟩ | `fr` | 1 | misma σ, otra forma |
| nuevo | n⟨ɔ⟩w | `oc` | 1 | n⟨ɔ⟩w | `ca` | 1 | misma σ, otra forma |
| ojo | yi | `nrf` | 1 | o⟨kʲ⟩ | `ro` | 1 | misma σ, otra forma |
| oler | gole⟨ɾ⟩ | `ast` | 2 | ole⟨ɾ⟩ | `an` | 2 | misma σ, otra forma |
| oreja | reca | `vec` | 2 | o⟨ʀ⟩⟨ɛ⟩y | `fr` | 2 | misma σ, otra forma |
| otro | alt | `ro` | 1 | ⟨ɒ⟩t | `ruo` | 1 | misma σ, otra forma |
| palo | stal | `dlm` | 1 | pal | `ca` | 1 | misma σ, otra forma |
| parar | xte | `lld` | 1 | ta⟨ɾ⟩ | `ast` | 1 | misma σ, otra forma |
| partir | f⟨ɛ̃⟩t | `wa` | 1 | f⟨ɛ̃⟩d | `pcd` | 1 | misma σ, otra forma |
| pecho | s⟨ɨ⟩n | `ro` | 1 | pit | `ca` | 1 | misma σ, otra forma |
| pelear | bat | `wa` | 1 | bat | `pcd` | 1 | misma σ, otra forma |
| pelo | per | `ruo` | 1 | payl | `dlm` | 1 | misma σ, otra forma |
| pensar | p⟨ẽ⟩sa⟨ɾ⟩ | `mwl` | 2 | pensa⟨ɾ⟩ | `an` | 2 | misma σ, otra forma |
| pequeño | mik | `ro` | 1 | cen | `eml` | 1 | misma σ, otra forma |
| perra | l⟨ɛ⟩x | `wa` | 1 | xy⟨ɛ⟩n | `fr` | 1 | misma σ, otra forma |
| perro | ⟨c⟩an | `fur` | 1 | kan | `an` | 1 | misma σ, otra forma |
| pesado | lu⟨ʀ⟩ | `fr` | 1 | payz | `eml` | 1 | misma σ, otra forma |
| pez | pesk | `fur` | 1 | pex | `an` | 1 | misma σ, otra forma |
| pie | pe | `lld` | 1 | pye | `an` | 1 | misma σ, otra forma |
| piedra | py⟨ɛ⟩⟨ʀ⟩ | `pcd` | 1 | sas | `eml` | 1 | misma σ, otra forma |
| piel | po | `fr` | 1 | pyel | `an` | 1 | misma σ, otra forma |
| pierna | ⟨d͡ʒ⟩⟨ɑ̃⟩p | `wa` | 1 | gwonb | `dlm` | 1 | misma σ, otra forma |
| piojo | pyuly | `oc` | 1 | poly | `ca` | 1 | misma σ, otra forma |
| pluma | pl⟨ɔ⟩m | `wa` | 1 | pl⟨y⟩m | `fr` | 1 | misma σ, otra forma |
| podrido | mar⟨t͡s⟩ | `lld` | 1 | m⟨ɛ⟩r⟨θ⟩ | `eml` | 1 | misma σ, otra forma |
| polvo | praw | `ruq` | 1 | pols | `ca` | 1 | misma σ, otra forma |
| porque | ka | `sc` | 1 | ka⟨ʀ⟩ | `fr` | 1 | misma σ, otra forma |
| quién | ⟨t͡ɕ⟩i | `rm` | 1 | kyen | `an` | 1 | misma σ, otra forma |
| qué | ki | `scn` | 1 | ke | `an` | 1 | misma σ, otra forma |
| raíz | ⟨ʁ⟩ayx | `pt` | 1 | ⟨ʁ⟩ays | `mwl` | 1 | misma σ, otra forma |
| recto | d⟨ʀ⟩⟨ɛ⟩ | `frp` | 1 | drat | `dlm` | 1 | misma σ, otra forma |
| reír | ⟨ʀ⟩i⟨ʀ⟩ | `frp` | 1 | rey⟨ɾ⟩ | `an` | 1 | misma σ, otra forma |
| rodilla | ⟨d͡ʒ⟩enun⟨kʲ⟩ | `ro` | 2 | ⟨ɾ⟩odya | `ast` | 2 | misma σ, otra forma |
| rojo | r⟨ɔ⟩s | `rgn` | 1 | r⟨ʌ⟩s | `eml` | 1 | misma σ, otra forma |
| romo | xtus | `rm` | 1 | rom | `ca` | 1 | misma σ, otra forma |
| saber | styu | `ruq` | 1 | xti | `ro` | 1 | misma σ, otra forma |
| sal | sal | `ca` | 1 | sal | `an` | 1 | misma σ, otra forma |
| sangre | sonk | `rm` | 1 | sa⟨ŋ⟩ | `ca` | 1 | misma σ, otra forma |
| seco | s⟨ɛ⟩k | `fr` | 1 | s⟨ɛ⟩k | `ca` | 1 | misma σ, otra forma |
| ser | ⟨ɛ⟩s | `wa` | 1 | se⟨ɾ⟩ | `an` | 1 | misma σ, otra forma |
| serpiente | xerp | `ruo` | 1 | serp | `ca` | 1 | misma σ, otra forma |
| si | si | `sc` | 1 | si | `an` | 1 | misma σ, otra forma |
| sol | sol | `vec` | 1 | sol | `an` | 1 | misma σ, otra forma |
| sonreír | son⟨ɾ⟩ey⟨ɾ⟩ | `lad` | 2 | sonrey⟨ɾ⟩ | `an` | 2 | misma σ, otra forma |
| sucio | spwark | `dlm` | 1 | b⟨ɾ⟩ut | `ca` | 1 | misma σ, otra forma |
| tener | ⟨t͡s⟩on | `ruq` | 1 | t⟨ɨ⟩⟨ɾ⟩ | `pt` | 1 | misma σ, otra forma |
| tierra | te⟨ð⟩ | `nrf` | 1 | t⟨ɛ⟩⟨ʀ⟩ | `fr` | 1 | misma σ, otra forma |
| tirar | trag | `rup` | 1 | tya | `lij` | 1 | misma σ, otra forma |
| todo | tut | `rup` | 1 | tot | `an` | 1 | misma σ, otra forma |
| tres | trey | `ro` | 1 | t⟨ɾ⟩es | `an` | 1 | misma σ, otra forma |
| tú | t⟨ə⟩ | `frp` | 1 | tu | `an` | 1 | misma σ, otra forma |
| uno | ⟨œ̃⟩ | `fr` | 1 | un | `an` | 1 | misma σ, otra forma |
| ver | v⟨ɛ⟩⟨ʀ⟩ | `gallo` | 1 | ve⟨ɾ⟩ | `ast` | 1 | misma σ, otra forma |
| verde | v⟨ɐ⟩rt | `lld` | 1 | v⟨ɛ⟩rt | `ca` | 1 | misma σ, otra forma |
| viejo | vi | `wa` | 1 | vely | `ca` | 1 | misma σ, otra forma |
| viento | ven | `gsc` | 1 | ven | `ca` | 1 | misma σ, otra forma |
| vientre | v⟨ɛ̃⟩t | `wa` | 1 | b⟨œ⟩y | `gallo` | 1 | misma σ, otra forma |
| vivir | viv | `lmo` | 1 | vi | `lld` | 1 | misma σ, otra forma |
| vosotros | vus | `rm` | 1 | voy | `co` | 1 | misma σ, otra forma |
| y | i | `mwl` | 1 | ye | `an` | 1 | misma σ, otra forma |
| yacer | kulk | `ruq` | 1 | zak | `rup` | 1 | misma σ, otra forma |
| yo | ⟨ʒ⟩⟨ə⟩ | `frp` | 1 | yo | `an` | 1 | misma σ, otra forma |
| árbol | ⟨ɔ⟩p | `wa` | 1 | l⟨ɐ⟩n | `lld` | 1 | misma σ, otra forma |
| él | ⟨ɐ⟩l | `lld` | 1 | el | `an` | 1 | misma σ, otra forma |

## Caveats

- La glosa del scorecard es española; el `id` inglés del gold list no es fuente.
- El inglés no es lengua fuente. El latín está reservado y no entra en el knapsack.
- Epitran usa la lect hermana cuando no hay mapa propio (Oil←fr, retorromance y dálmata←it, asturiano←es, oriental←ro): `água`→`aga`, `olho`→`olo`, `ojo`/`rojo`→`okso`/`rokso`. `chat`→`xa` es la ortografía de `ʃ`.
- Las desinencias comparan tablas de lect atestiguadas y una tabla productiva hecha con segmentos observados; esta última no afirma que sus combinaciones sean morfemas atestiguados. El recocido solo mueve raíces dentro del corte de σ mínima.
