<!-- GENERATED FILE: scripts/es_pt_beta.py; do not edit by hand. -->
<!-- source_lects: 36 (es, pt, gl, an, ast, ext, lad, mwl, oc, ca, gsc, fr, wa, pcd, nrf, glw, frp, lmo, pms, lij, eml, rgn, it, scn, vec, co, ist, dlm, rm, fur, lld, sc, ro, rup, ruo, ruq) -->
<!-- concepts: 213 -->
<!-- candidates_sha256_16: f757820ba72963f2 -->
<!-- lexicon_sha256_16: bed2db33daab92b5 -->
<!-- lexicon_iterations: 499997 -->
<!-- Re-run scripts/run_vulgultra.py or this renderer to refresh. -->
# Vulgultra concept grid — 36 daughter lects

Lexicón de origen mixto: una forma Vulgultra por concepto, elegida
entre candidatos meaning-aligned de las hijas Romance, por rama:

- **ibero:** `es` Spanish, `pt` Portuguese, `gl` Galician, `an` Aragonese, `ast` Asturian, `ext` Extremaduran, `lad` Ladino, `mwl` Mirandese
- **occitano:** `oc` Occitan, `ca` Catalan, `gsc` Gascon
- **oil:** `fr` French, `wa` Walloon, `pcd` Picard, `nrf` Norman, `glw` Gallo
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

Frente a **español** y **portugués** (las lenguas de inspección): el mixto tiene **230** sílabas de raíz vs ES 230 y PT 230, con **0** violaciones (ES 0, PT 0).

Frente a **francés**: always-fr suma 230σ con **0** violaciones. El mixto es igual de largo, con 0 violaciones. Italiano suma 230σ (0 viol.).

Calidad del optimizador: greedy-phones Σσ=230 |Φ|=64 E=16538; SA Σσ=230 |Φ|=64 E=16538 (acuerdo con greedy-phones 213/213). El shortest crudo llega a 230σ con 0 violaciones.

Desinencias seleccionadas después de fijar las raíces: tema nominal `lect:an`, tiempos verbales `prs=an/ca/an/co/grid-inventory/co,pst=an/eml/an/grid-inventory/grid-inventory/grid-inventory,fut=an/ca/sc/an/grid-inventory/grid-inventory,subj=an/gsc/ca/grid-inventory/grid-inventory/grid-inventory,theme_i=an/ca/grid-inventory/grid-inventory/grid-inventory/grid-inventory,theme_a=an/ca/grid-inventory/grid-inventory/grid-inventory/grid-inventory`. Cada tiempo es una fila; el SA de raíces no las mueve.

## Procedencia (raíces SA)

| fuente | raíces | % |
|---|---:|---:|
| `es` | 0 | 0.0% |
| `pt` | 4 | 1.9% |
| `gl` | 4 | 1.9% |
| `an` | 40 | 18.8% |
| `ast` | 4 | 1.9% |
| `ext` | 0 | 0.0% |
| `lad` | 0 | 0.0% |
| `mwl` | 2 | 0.9% |
| `oc` | 1 | 0.5% |
| `ca` | 48 | 22.5% |
| `gsc` | 2 | 0.9% |
| `fr` | 22 | 10.3% |
| `wa` | 6 | 2.8% |
| `pcd` | 3 | 1.4% |
| `nrf` | 1 | 0.5% |
| `glw` | 5 | 2.3% |
| `frp` | 3 | 1.4% |
| `lmo` | 8 | 3.8% |
| `pms` | 1 | 0.5% |
| `lij` | 3 | 1.4% |
| `eml` | 8 | 3.8% |
| `rgn` | 2 | 0.9% |
| `it` | 0 | 0.0% |
| `scn` | 0 | 0.0% |
| `vec` | 0 | 0.0% |
| `co` | 2 | 0.9% |
| `ist` | 0 | 0.0% |
| `dlm` | 19 | 8.9% |
| `rm` | 0 | 0.0% |
| `fur` | 1 | 0.5% |
| `lld` | 3 | 1.4% |
| `sc` | 0 | 0.0% |
| `ro` | 3 | 1.4% |
| `rup` | 10 | 4.7% |
| `ruo` | 2 | 0.9% |
| `ruq` | 6 | 2.8% |
| **total** | 213 | 100% |

## Totales por política

Las terminaciones de SA se mantienen fijas en las políticas de raíz.
`greedy-phones` es la inicialización voraz por segmentos nuevos; SA recorre el mismo corte de σ mínima.

| política | Σσ raíces | media σ | viol | \|Φ\| | lects (dato) | E_end | E_coll | E_tact | E_dist | E_total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sa | 230 | 1.08 | 0 | 64 | 27 | 10600 | 0 | 6000 | 0 | 16538 |
| greedy-phones | 230 | 1.08 | 0 | 64 | 27 | 10600 | 0 | 6000 | 0 | 16538 |
| shortest | 230 | 1.08 | 0 | 52 | 23 | 10600 | 0 | 6000 | 0 | 16559 |
| always-es | 230 | 1.08 | 0 | 52 | 24 | 10600 | 0 | 6000 | 0 | 16558 |
| always-pt | 230 | 1.08 | 0 | 55 | 22 | 10600 | 0 | 6000 | 0 | 16553 |
| always-fr | 230 | 1.08 | 0 | 54 | 23 | 10600 | 0 | 6000 | 0 | 16558 |
| always-it | 230 | 1.08 | 0 | 52 | 23 | 10600 | 0 | 6000 | 0 | 16560 |
| always-ca | 230 | 1.08 | 0 | 52 | 23 | 10600 | 0 | 6000 | 0 | 16560 |
| always-ro | 230 | 1.08 | 0 | 53 | 21 | 10600 | 0 | 6000 | 0 | 16558 |
| always-gl | 230 | 1.08 | 0 | 55 | 23 | 10600 | 0 | 6000 | 0 | 16556 |
| always-oc | 230 | 1.08 | 0 | 52 | 22 | 10600 | 0 | 6000 | 0 | 16559 |
| init | 230 | 1.08 | 0 | 64 | 27 | 10600 | 0 | 6000 | 0 | 16538 |

Energía inicial reportada por el CLI Rust: **16538** (comparar con SA E_total = 16538).

## Acuerdo

- Conceptos: **213**
- ES y PT adaptados idénticos: 4/213
- SA = ES (ortografía Vulgultra): 31/213
- SA = PT: 10/213
- SA = FR: 27/213
- SA = IT: 5/213
- SA = shortest (crudo): 191/213
- SA = greedy-phones: 213/213
- SA ≠ greedy-phones: 0/213

## Frases de demostración

Con conjugación y concordancia. Artículo **o/a**. Copula 3sg **e**.
Verbo = tema + la fila de presente elegida. El objeto va en acusativo.

### El gato rojo sonríe.

PT: O gato vermelho sorri.

```
Vulgultra  o  gato  ⟨ɾ⟩⟨ɔ⟩⟨ʒ⟩co  somy⟨kʷ⟩il
src    [pt]  [ca]  [ca]  [dlm]
es     el/la  gato  rojo  sonreír
pt     o  gato  vermelho  sorrir
σ      7
```

### El perro es grande.

PT: O cão é grande.

```
Vulgultra  o  k⟨ɐ̃⟩⟨w̃⟩o  e  gr⟨ã⟩ndo
src    [pt]  [pt]  [pt]  [rgn]
es     el/la  perro  es  grande
pt     o  cão  é  grande
σ      6
```

### El agua es fría.

PT: A água é fria.

```
Vulgultra  a  ⟨ə⟩wa  e  f⟨ɾ⟩yoa
src    [pt]  [glw]  [pt]  [an]
es     el/la  agua  es  frío
pt     a  água  é  frio
σ      6
```

### Yo veo el sol.

PT: Eu vejo o sol.

```
Vulgultra  yo  ve⟨ɾ⟩o  o  solon
src    [an]  [ast]  [pt]  [an]
es     yo  ver  el/la  sol
pt     eu  ver  o  sol
σ      6
```

### La mujer come pez.

PT: A mulher come peixe.

```
Vulgultra  a  mu⟨ʝ⟩e⟨ɾ⟩a  m⟨ə⟩k⟨kʷ⟩il  peson
src    [pt]  [an]  [rup]  [ast]
es     el/la  mujer  comer  pez
pt     a  mulher  comer  peixe
σ      8
```

### El fuego es rojo.

PT: O fogo é vermelho.

```
Vulgultra  o  f⟨ɔ⟩ko  e  ⟨ɾ⟩⟨ɔ⟩⟨ʒ⟩co
src    [pt]  [ca]  [pt]  [ca]
es     el/la  fuego  es  rojo
pt     o  fogo  é  vermelho
σ      6
```

### Nosotros damos agua.

PT: Nós damos água.

```
Vulgultra  nu  da⟨ɾ⟩em  ⟨ə⟩wan
src    [dlm]  [an]  [glw]
es     nosotros  dar  agua
pt     nós  dar  água
σ      5
```

### El hombre es bueno.

PT: O homem é bom.

```
Vulgultra  o  ⟨ɔ⟩mo  e  b⟨õ⟩o
src    [pt]  [eml]  [pt]  [pt]
es     el/la  hombre  es  bueno
pt     o  homem  é  bom
σ      6
```

### La noche es negra.

PT: A noite é preta.

```
Vulgultra  a  nita  e  foxa
src    [pt]  [ca]  [pt]  [dlm]
es     el/la  noche  es  negro
pt     a  noite  é  preto
σ      6
```

### Tú oyes el viento.

PT: Tu ouves o vento.

```
Vulgultra  tu  wyi⟨ʀ⟩as  o  v⟨ɛ⟩nton
src    [an]  [glw]  [pt]  [ca]
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
| gato | **gat** | `ca` | 1 | **xat** | `fr` | 1 |
| perro | **k⟨ɐ̃⟩⟨w̃⟩** | `pt` | 1 | **xy⟨ɛ⟩n** | `fr` | 1 |

## Tabla por concepto

| glosa | es | pt | fr | it | ca | Vulgultra | src | σ | por qué | bin |
|---|---|---|---|---|---|---|---|---:|---|---|
| a | a | a | à | a | a | **a** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| afilado | afilado | afiado | aigu | affilato | esmolat | **⟨ɛ⟩g** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| agua | agua | água | eau | acqua | aigua | **o** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| ala | ala | asa | aile | ala | ala | **e** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| algunos | algunos | alguns | quelques | alcuni | alguns | **nek** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| allí | allí | ali | là | lì | allà | **ci** | `co` | 1 | σ=1; desempate por segmentos del léxico global | — |
| amarillo | amarillo | amarelo | jaune | giallo | groc | **g⟨ɾ⟩⟨ɔ⟩k** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| ancho | ancho | largo | large | largo | ample | **larg** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| animal | animal | animal | animal | animale | animal | **bet** | `glw` | 1 | σ=1; desempate por segmentos del léxico global | — |
| apretar | apretar | apertar | presser | spremere | prémer | **strens** | `lmo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| apuñalar | apuñalar | esfaquear | poignarder | pugnalare | apunyalar | **pung** | `ruq` | 1 | única legal a σ=1 | — |
| aquí | aquí | aqui | ici | qui | aquí | **ka** | `co` | 1 | σ=1; desempate por segmentos del léxico global | — |
| arena | arena | areia | sable | sabbia | sorra | **sa⟨β⟩la** | `gsc` | 2 | σ=2; desempate por segmentos del léxico global | — |
| atar | atar | atar | lier | legare | lligar | **ly⟨ɛ⟩⟨ʀ⟩** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| año | año | ano | année | anno | any | **a⟨ɲ⟩** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| beber | beber | beber | boire | bere | beure | **bwa⟨ʀ⟩** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| blanco | blanco | branco | blanc | bianco | blanc | **bla⟨ŋ⟩k** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| boca | boca | boca | bouche | bocca | boca | **bux** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| bosque | bosque | floresta | forêt | foresta | bosc | **b⟨ɔ⟩sk** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| bueno | bueno | bom | bon | buono | bo | **b⟨õ⟩** | `pt` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| cabeza | cabeza | cabeça | tête | testa | cap | **kap** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| caer | caer | cair | tomber | cadere | caure | **kad** | `lmo` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| caliente | caliente | quente | chaud | caldo | calent | **kald** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| caminar | caminar | andar | marcher | camminare | caminar | **yi** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | — |
| camino | camino | estrada | route | strada | camí | **vya** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cantar | cantar | cantar | chanter | cantare | cantar | **kont** | `ruq` | 1 | única legal a σ=1 | — |
| carne | carne | carne | viande | carne | carn | **ka⟨ɾ⟩n** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cavar | cavar | cavar | creuser | scavare | cavar | **sap** | `rup` | 1 | única legal a σ=1 | — |
| cazar | cazar | caçar | chasser | cacciare | caçar | **kasa⟨ɾ⟩** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| ceniza | ceniza | cinza | cendre | cenere | cendra | **s⟨ɛ̃⟩d** | `wa` | 1 | única legal a σ=1 | — |
| cerca | cerca | perto | près | vicino | prop | **p⟨ɾ⟩⟨ɔ⟩p** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| chupar | chupar | chupar | sucer | succhiare | xuclar | **sug** | `rup` | 1 | única legal a σ=1 | — |
| cielo | cielo | céu | ciel | cielo | cel | **s⟨ɛ⟩l** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| cinco | cinco | cinco | cinq | cinque | cinc | **si⟨ŋ⟩k** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cola | cola | rabo | queue | coda | cua | **kwa** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| comer | comer | comer | manger | mangiare | menjar | **m⟨ə⟩k** | `rup` | 1 | única legal a σ=1 | — |
| con | con | com | avec | con | amb | **kon** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| congelar | congelar | congelar | geler | gelare | gelar | **gl⟨ɛ⟩⟨ʀ⟩** | `pcd` | 1 | única legal a σ=1 | — |
| contar | contar | contar | compter | contare | comptar | **konta⟨ɾ⟩** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| corazón | corazón | coração | cœur | cuore | cor | **k⟨ɔ⟩⟨ɾ⟩** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| correcto | correcto | correto | correct | corretto | correcte | **⟨d͡ʒ⟩⟨ü⟩st** | `lmo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cortar | cortar | cortar | couper | tagliare | tallar | **tal⟨ʒ⟩** | `ruq` | 1 | única legal a σ=1 | — |
| corteza | corteza | casca | écorce | corteccia | escorça | **skwaz** | `wa` | 1 | única legal a σ=1 | — |
| corto | corto | curto | court | corto | curt | **ku⟨ɾ⟩t** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| coser | coser | costurar | coudre | cucire | cosir | **kos** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cuatro | cuatro | quatro | quatre | quattro | quatre | **kat** | `glw` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cuello | cuello | pescoço | cou | collo | coll | **k⟨ɔ⟩⟨ʎ⟩** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cuerda | cuerda | corda | corde | corda | corda | **k⟨ɔ⟩⟨ʀ⟩d** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cuerno | cuerno | chifre | corne | corno | banya | **k⟨ɔ⟩⟨ʀ⟩n** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cuándo | cuándo | quando | quand | quando | quan | **kwan** | `an` | 1 | σ=1; desempate por segmentos del léxico global | — |
| cómo | cómo | como | comment | come | com | **k⟨ɔ⟩m** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| dar | dar | dar | donner | dare | donar | **da⟨ɾ⟩** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| decir | decir | dizer | dire | dire | dir | **di⟨ɾ⟩** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| delgado | delgado | fino | mince | sottile | prim | **p⟨ɾ⟩im** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| derecha | derecha | direita | droite | destra | dreta | **dret** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| diente | diente | dente | dent | dente | dent | **d⟨ɛ⟩nt** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| dormir | dormir | dormir | dormir | dormire | dormir | **dorm** | `ruq` | 1 | única legal a σ=1 | — |
| dos | dos | dois | deux | due | dos | **dos** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| día | día | dia | jour | giorno | dia | **dya** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| dónde | dónde | onde | où | dove | on | **an** | `an` | 1 | σ=1; desempate por segmentos del léxico global | — |
| el | el | o | le | il | el | **o** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| ellos | ellos | eles | ils | loro | ells | **els** | `an` | 1 | σ=1; desempate por segmentos del léxico global | — |
| empujar | empujar | empurrar | pousser | spingere | empènyer | **sping** | `lmo` | 1 | única legal a σ=1 | — |
| en | en | em | dans | in | en | **en** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| entrañas | entrañas | tripas | entrailles | viscere | budells | **t⟨ɾ⟩ipas** | `an` | 2 | σ=2; desempate por segmentos del léxico global | adivinable |
| escupir | escupir | cuspir | cracher | sputare | escopir | **spwar** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| eso | eso | isso | cela | quello | aquell | **kol** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| espalda | espalda | costas | dos | schiena | esquena | **dri** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| esposa | esposa | esposa | épouse | moglie | muller | **mwir** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | — |
| esposo | esposo | marido | mari | marito | marit | **so⟨t͡s⟩** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | — |
| esto | esto | isto | ceci | questo | aquest | **cest** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| estrecho | estrecho | estreito | étroit | stretto | estret | **str⟨ɨ⟩mt** | `ruo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| estrella | estrella | estrela | étoile | stella | estrella | **st⟨œ⟩l** | `wa` | 1 | única legal a σ=1 | — |
| flor | flor | flor | fleur | fiore | flor | **flo⟨ɾ⟩** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| flotar | flotar | flutuar | flotter | galleggiare | flotar | **flota⟨ɾ⟩** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| fluir | fluir | fluir | couler | fluire | fluir | **flwi⟨ɾ⟩** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| frotar | frotar | esfregar | frotter | strofinare | fregar | **frek** | `rup` | 1 | única legal a σ=1 | — |
| fruta | fruta | fruta | fruit | frutto | fruita | **frot** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | — |
| frío | frío | frio | froid | freddo | fred | **f⟨ɾ⟩yo** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| fuego | fuego | fogo | feu | fuoco | foc | **f⟨ɔ⟩k** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| gata | gata | gata | chatte | gatta | gata | **xat** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| gato | gato | gato | chat | gatto | gat | **gat** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| girar | girar | girar | tourner | girare | girar | **⟨d͡ʒ⟩ya** | `lij` | 1 | única legal a σ=1 | — |
| golpear | golpear | bater | frapper | colpire | pegar | **bat** | `lmo` | 1 | única legal a σ=1 | — |
| grande | grande | grande | grand | grande | gran | **gr⟨ã⟩nd** | `rgn` | 1 | σ=1; desempate por segmentos del léxico global | — |
| grasa | grasa | gordura | graisse | grasso | greix | **g⟨ɾ⟩⟨ɛ⟩⟨ʒ⟩x** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| grueso | grueso | grosso | épais | spesso | gruixut | **gros** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| gusano | gusano | verme | ver | verme | cuc | **kuk** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| hielo | hielo | gelo | glace | ghiaccio | gel | **⟨ʒ⟩⟨ɛ⟩l** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| hierba | hierba | erva | herbe | erba | herba | **⟨ɛ⟩⟨ʀ⟩b** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| hinchar | hinchar | inchar | enfler | gonfiare | inflar | **e⟨ɱ⟩fla** | `gsc` | 2 | σ=2; desempate por segmentos del léxico global | opaco |
| hoja | hoja | folha | feuille | foglia | fulla | **foy** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | — |
| hombre | hombre | homem | homme | uomo | home | **⟨ɔ⟩m** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | — |
| hueso | hueso | osso | os | osso | os | **⟨ɔ⟩s** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| huevo | huevo | ovo | œuf | uovo | ou | **⟨ɔ⟩b** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| humo | humo | fumo | fumée | fumo | fum | **f⟨œ̃⟩** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | — |
| hígado | hígado | fígado | foie | fegato | fetge | **fwa** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| izquierda | izquierda | esquerda | gauche | sinistra | esquerra | **sank** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| jugar | jugar | jogar | jouer | giocare | jugar | **⟨ʒ⟩u⟨ʀ⟩** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| lago | lago | lago | lac | lago | llac | **⟨ʎ⟩ak** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| lanzar | lanzar | atirar | jeter | lanciare | llançar | **tra** | `lmo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| largo | largo | longo | long | lungo | llarg | **⟨ʎ⟩a⟨ɾ⟩g** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| lavar | lavar | lavar | laver | lavare | rentar | **spel** | `rup` | 1 | única legal a σ=1 | — |
| lejos | lejos | longe | loin | lontano | lluny | **⟨ʎ⟩u⟨ɲ⟩** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| lengua | lengua | língua | langue | lingua | llengua | **l⟨ɑ̃⟩g** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| liso | liso | liso | lisse | liscio | llis | **⟨ʎ⟩is** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| lleno | lleno | cheio | plein | pieno | ple | **plen** | `an` | 1 | σ=1; desempate por segmentos del léxico global | — |
| lluvia | lluvia | chuva | pluie | pioggia | pluja | **pl⟨ø⟩** | `glw` | 1 | σ=1; desempate por segmentos del léxico global | — |
| luna | luna | lua | lune | luna | lluna | **lw⟨ɐ⟩** | `pt` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| madre | madre | mãe | mère | madre | mare | **m⟨ɐ̃⟩⟨j̃⟩** | `pt` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| malo | malo | mau | mauvais | cattivo | dolent | **ri** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| mano | mano | mão | main | mano | mà | **man** | `an` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| mar | mar | mar | mer | mare | mar | **ma⟨ɾ⟩** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| matar | matar | matar | tuer | uccidere | matar | **t⟨ɥ⟩a⟨ʀ⟩** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | — |
| mojado | mojado | molhado | mouillé | bagnato | mullat | **ud** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | — |
| montaña | montaña | montanha | montagne | montagna | muntanya | **kr⟨ë⟩p** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | — |
| morder | morder | morder | mordre | mordere | mossegar | **mo⟨ɾ⟩de⟨ɾ⟩** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| morir | morir | morrer | mourir | morire | morir | **mwi** | `lij` | 1 | σ=1; desempate por segmentos del léxico global | — |
| muchos | muchos | muitos | beaucoup | molti | molts | **m⟨ɔ⟩ls** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| mujer | mujer | mulher | femme | donna | dona | **mu⟨ʝ⟩e⟨ɾ⟩** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| nadar | nadar | nadar | nager | nuotare | nedar | **n⟨ɛ⟩d** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | — |
| nariz | nariz | nariz | nez | naso | nas | **nas** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| negro | negro | preto | noir | nero | negre | **fox** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| niebla | niebla | nevoeiro | brouillard | nebbia | boira | **b⟨ɔ⟩⟨ʒ⟩⟨ɾ⟩a** | `ca` | 2 | σ=2; desempate por segmentos del léxico global | opaco |
| nieve | nieve | neve | neige | neve | neu | **n⟨ɛ⟩b** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| niño | niño | criança | enfant | bambino | nen | **fy⟨ö⟩** | `lmo` | 1 | σ=1; desempate por segmentos del léxico global | — |
| no | no | não | non | non | no | **no** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| noche | noche | noite | nuit | notte | nit | **nit** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| nombre | nombre | nome | nom | nome | nom | **n⟨ɔ⟩m** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| nosotros | nosotros | nós | nous | noi | nosaltres | **nu** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| nube | nube | nuvem | nuage | nuvola | núvol | **n⟨ɥ⟩a⟨ʒ⟩** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| nuevo | nuevo | novo | nouveau | nuovo | nou | **n⟨ɔ⟩b** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| ojo | ojo | olho | œil | occhio | ull | **u⟨ʎ⟩** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| oler | oler | cheirar | sentir | odorare | ensumar | **ole⟨ɾ⟩** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| oreja | oreja | orelha | oreille | orecchio | orella | **⟨ɔ⟩⟨ʀ⟩** | `wa` | 1 | única legal a σ=1 | — |
| otro | otro | outro | autre | altro | altre | **ot** | `nrf` | 1 | σ=1; desempate por segmentos del léxico global | — |
| oír | oír | ouvir | entendre | sentire | sentir | **wyi⟨ʀ⟩** | `glw` | 1 | σ=1; desempate por segmentos del léxico global | — |
| padre | padre | pai | père | padre | pare | **pa⟨ʀ⟩** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| palo | palo | pau | bâton | bastone | pal | **pal** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| parar | parar | ficar | tenir | stare | estar | **ta⟨ɾ⟩** | `ast` | 1 | σ=1; desempate por segmentos del léxico global | — |
| partir | partir | fender | fendre | spaccare | fendre | **f⟨ɛ̃⟩d** | `wa` | 1 | única legal a σ=1 | — |
| pecho | pecho | peito | sein | petto | pit | **pit** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pelear | pelear | lutar | combattre | combattere | lluitar | **bat** | `pcd` | 1 | única legal a σ=1 | — |
| pelo | pelo | cabelo | cheveu | capello | cabell | **p⟨ɛ⟩l** | `oc` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pensar | pensar | pensar | penser | pensare | pensar | **pensa⟨ɾ⟩** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| pequeño | pequeño | pequeno | petit | piccolo | petit | **cit** | `pms` | 1 | σ=1; desempate por segmentos del léxico global | — |
| perra | perra | cadela | chienne | cagna | gossa | **xy⟨ɛ⟩n** | `fr` | 1 | única legal a σ=1 | — |
| perro | perro | cão | chien | cane | gos | **k⟨ɐ̃⟩⟨w̃⟩** | `pt` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| persona | persona | pessoa | personne | persona | persona | **om** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pesado | pesado | pesado | lourd | pesante | pesat | **lu⟨ʀ⟩** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pez | pez | peixe | poisson | pesce | peix | **pes** | `ast` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| pie | pie | pé | pied | piede | peu | **pye** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| piedra | piedra | pedra | pierre | pietra | pedra | **py⟨ɛ⟩⟨ʀ⟩⟨ʀ⟩** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| piel | piel | pele | peau | pelle | pell | **pyel** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| pierna | pierna | perna | jambe | gamba | cama | **gamba** | `an` | 2 | σ=2; desempate por segmentos del léxico global | opaco |
| piojo | piojo | piolho | pou | pidocchio | poll | **p⟨ɔ⟩⟨ʎ⟩** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pluma | pluma | pena | plume | piuma | ploma | **pl⟨y⟩m** | `fr` | 1 | única legal a σ=1 | — |
| pocos | pocos | poucos | peu | pochi | pocs | **pok** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| podrido | podrido | podre | pourri | marcio | podrit | **m⟨ɛ⟩rs** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | — |
| polvo | polvo | pó | poussière | polvere | pols | **p⟨ʊ⟩** | `gl` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| porque | porque | porque | parce | perché | perquè | **pa⟨ʀ⟩s** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| pájaro | pájaro | pássaro | oiseau | uccello | ocell | **pul⟨ʒ⟩** | `ruo` | 1 | única legal a σ=1 | — |
| quemar | quemar | queimar | brûler | bruciare | cremar | **ard** | `rup` | 1 | única legal a σ=1 | — |
| quién | quién | quem | qui | chi | qui | **⟨kʷ⟩y⟨ɛ̃⟩** | `mwl` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| qué | qué | que | quoi | che | què | **k⟨ɪ⟩** | `gl` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| rascar | rascar | coçar | gratter | grattare | gratar | **ras⟨θ⟩a⟨ɾ⟩** | `gl` | 2 | σ=2; desempate por segmentos del léxico global | adivinable |
| raíz | raíz | raiz | racine | radice | arrel | **⟨ʁ⟩ay⟨ʒ⟩** | `mwl` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| recto | recto | direito | droit | dritto | recte | **drit** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| redondo | redondo | redondo | rond | rotondo | rodó | **tond** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | — |
| respirar | respirar | respirar | respirer | respirare | respirar | **spirar** | `dlm` | 2 | σ=2; desempate por segmentos del léxico global | — |
| reír | reír | rir | rire | ridere | riure | **⟨ʀ⟩i⟨ʀ⟩** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| rodilla | rodilla | joelho | genou | ginocchio | genoll | **⟨ɾ⟩odya** | `ast` | 2 | σ=2; desempate por segmentos del léxico global | — |
| rojo | rojo | vermelho | rouge | rosso | roig | **⟨ɾ⟩⟨ɔ⟩⟨ʒ⟩c** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| romo | romo | cego | émoussé | smussato | rom | **⟨ɾ⟩⟨ɔ⟩m** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| río | río | rio | rivière | fiume | riu | **fy⟨ũ⟩** | `rgn` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| saber | saber | saber | savoir | sapere | saber | **xti** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | — |
| sal | sal | sal | sel | sale | sal | **sal** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| sangre | sangre | sangue | sang | sangue | sang | **sa⟨ŋ⟩g** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| secar | secar | enxugar | essuyer | asciugare | eixugar | **sterg** | `ruq` | 1 | única legal a σ=1 | — |
| seco | seco | seco | sec | secco | sec | **s⟨ɛ⟩k** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| semilla | semilla | semente | graine | seme | llavor | **zm⟨ɛ⟩ns** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | — |
| sentar | sentar | sentar | asseoir | sedere | seure | **s⟨h⟩ed** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| ser | ser | ser | être | essere | ser | **se⟨ɾ⟩** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| serpiente | serpiente | serpente | serpent | serpente | serp | **s⟨ɛ⟩⟨ɾ⟩p** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| si | si | se | si | se | si | **si** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| sol | sol | sol | soleil | sole | sol | **sol** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| sonreír | sonreír | sorrir | sourire | sorridere | somriure | **somyar** | `dlm` | 2 | σ=2; desempate por segmentos del léxico global | opaco |
| soplar | soplar | soprar | souffler | soffiare | bufar | **sfya** | `lmo` | 1 | única legal a σ=1 | — |
| sucio | sucio | sujo | sale | sporco | brut | **b⟨ɾ⟩ut** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| temer | temer | temer | craindre | temere | témer | **teme⟨ɾ⟩** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| tener | tener | ter | tenir | tenere | tenir | **te⟨ɾ⟩** | `gl` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| tierra | tierra | terra | terre | terra | terra | **t⟨ɛ⟩⟨ʀ⟩⟨ʀ⟩** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| tirar | tirar | puxar | tirer | tirare | estirar | **tya** | `lij` | 1 | σ=1; desempate por segmentos del léxico global | — |
| todo | todo | todo | tout | tutto | tot | **tot** | `an` | 1 | σ=1; desempate por segmentos del léxico global | — |
| tres | tres | três | trois | tre | tres | **t⟨ɾ⟩es** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| tú | tú | tu | tu | tu | tu | **tu** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| uno | uno | um | un | uno | un | **un** | `an` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| uña | uña | unha | ongle | unghia | ungla | **⟨ɔ̃⟩g** | `wa` | 1 | única legal a σ=1 | — |
| venir | venir | vir | venir | venire | venir | **⟨ɲ⟩ir** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| ver | ver | ver | voir | vedere | veure | **ve⟨ɾ⟩** | `ast` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| verde | verde | verde | vert | verde | verd | **v⟨ɛ⟩⟨ɾ⟩d** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| viejo | viejo | velho | vieux | vecchio | vell | **v⟨ɛ⟩⟨ʎ⟩** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| viento | viento | vento | vent | vento | vent | **v⟨ɛ⟩nt** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | — |
| vientre | vientre | ventre | ventre | pancia | ventre | **v⟨ɛ̃⟩t** | `pcd` | 1 | única legal a σ=1 | — |
| vivir | vivir | viver | vivre | vivere | viure | **vi** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | — |
| volar | volar | voar | voler | volare | volar | **zbor** | `rup` | 1 | única legal a σ=1 | — |
| vomitar | vomitar | vomitar | vomir | vomitare | vomitar | **vom** | `ruq` | 1 | única legal a σ=1 | — |
| vosotros | vosotros | vocês | vous | voi | vosaltres | **vu** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | — |
| y | y | e | et | e | i | **i** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| yacer | yacer | jazer | gésir | giacere | jeure | **zak** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | — |
| yo | yo | eu | je | io | jo | **yo** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| árbol | árbol | árvore | arbre | albero | arbre | **ab** | `glw` | 1 | σ=1; desempate por segmentos del léxico global | — |
| él | él | ele | il | lui | ell | **el** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |

## Apéndice: SA ≠ greedy-phones

Ninguna. SA coincidió con greedy-phones en todos los conceptos.

## Caveats

- La glosa del scorecard es española; el `id` inglés del gold list no es fuente.
- El inglés no es lengua fuente. El latín está reservado y no entra en el knapsack.
- Epitran usa la lect hermana cuando no hay mapa propio (Oil←fr, retorromance y dálmata←it, asturiano←es, oriental←ro): `água`→`aga`, `olho`→`olo`, `ojo`/`rojo`→`okso`/`rokso`. `chat`→`xa` es la ortografía de `ʃ`.
- Las desinencias comparan tablas de lect atestiguadas y una tabla productiva hecha con segmentos observados; esta última no afirma que sus combinaciones sean morfemas atestiguados. El recocido solo mueve raíces dentro del corte de σ mínima.
