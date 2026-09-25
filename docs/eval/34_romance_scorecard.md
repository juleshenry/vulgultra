<!-- GENERATED FILE: scripts/es_pt_beta.py; do not edit by hand. -->
<!-- source_lects: 36 (es, pt, gl, an, ast, ext, lad, mwl, oc, ca, gsc, fr, wa, pcd, nrf, glw, frp, lmo, pms, lij, eml, rgn, it, scn, vec, co, ist, dlm, rm, fur, lld, sc, ro, rup, ruo, ruq) -->
<!-- concepts: 213 -->
<!-- candidates_sha256_16: f77846f7b61e8d1c -->
<!-- lexicon_sha256_16: 8cea83d137a0000d -->
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

Frente a **español** y **portugués** (las lenguas de inspección): el mixto tiene **223** sílabas de raíz vs ES 450 y PT 442, con **0** violaciones (ES 0, PT 0).

Frente a **francés**: always-fr suma 327σ con **0** violaciones. El mixto es 104σ más corto, con 0 violaciones. Italiano suma 518σ (0 viol.).

Calidad del optimizador: greedy-phones Σσ=223 |Φ|=23 E=34077; SA Σσ=223 |Φ|=22 E=34078 (acuerdo con greedy-phones 120/213). El shortest crudo llega a 223σ con 0 violaciones.

Desinencias seleccionadas después de fijar las raíces: tema nominal `o`, tiempos verbales `prs=frp,pst=ca,fut=eml,subj=ca,theme_i=ca,theme_a=ca`. Cada tiempo es una fila; el SA de raíces no las mueve.

## Procedencia (raíces SA)

| fuente | raíces | % |
|---|---:|---:|
| `es` | 1 | 0.5% |
| `pt` | 1 | 0.5% |
| `gl` | 2 | 0.9% |
| `an` | 26 | 12.2% |
| `ast` | 2 | 0.9% |
| `ext` | 1 | 0.5% |
| `lad` | 1 | 0.5% |
| `mwl` | 1 | 0.5% |
| `oc` | 1 | 0.5% |
| `ca` | 19 | 8.9% |
| `gsc` | 4 | 1.9% |
| `fr` | 37 | 17.4% |
| `wa` | 5 | 2.3% |
| `pcd` | 5 | 2.3% |
| `nrf` | 4 | 1.9% |
| `glw` | 7 | 3.3% |
| `frp` | 9 | 4.2% |
| `lmo` | 5 | 2.3% |
| `pms` | 2 | 0.9% |
| `lij` | 2 | 0.9% |
| `eml` | 17 | 8.0% |
| `rgn` | 1 | 0.5% |
| `it` | 1 | 0.5% |
| `scn` | 1 | 0.5% |
| `vec` | 1 | 0.5% |
| `co` | 2 | 0.9% |
| `ist` | 2 | 0.9% |
| `dlm` | 16 | 7.5% |
| `rm` | 1 | 0.5% |
| `fur` | 4 | 1.9% |
| `lld` | 7 | 3.3% |
| `sc` | 1 | 0.5% |
| `ro` | 6 | 2.8% |
| `rup` | 9 | 4.2% |
| `ruo` | 5 | 2.3% |
| `ruq` | 4 | 1.9% |
| **total** | 213 | 100% |

## Totales por política

Las terminaciones de SA se mantienen fijas en las políticas de raíz.
`greedy-phones` es la inicialización voraz por segmentos nuevos; SA recorre el mismo corte de σ mínima.

| política | Σσ raíces | media σ | viol | \|Φ\| | lects (dato) | E_end | E_coll | E_tact | E_dist | E_total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sa | 223 | 1.05 | 0 | 22 | 36 | 10600 | 0 | 6000 | 17500 | 34078 |
| greedy-phones | 223 | 1.05 | 0 | 23 | 24 | 10600 | 0 | 6000 | 17500 | 34077 |
| shortest | 223 | 1.05 | 0 | 23 | 24 | 10600 | 0 | 6000 | 17500 | 34077 |
| always-es | 450 | 2.11 | 0 | 21 | 2 | 10600 | 0 | 6000 | 17500 | 34079 |
| always-pt | 442 | 2.08 | 0 | 22 | 2 | 10600 | 0 | 6000 | 17500 | 34078 |
| always-fr | 327 | 1.54 | 0 | 22 | 5 | 10600 | 0 | 6000 | 17500 | 34078 |
| always-it | 518 | 2.43 | 0 | 23 | 1 | 10600 | 0 | 6000 | 17500 | 34077 |
| always-ca | 363 | 1.70 | 0 | 22 | 3 | 10600 | 0 | 6000 | 17500 | 34078 |
| always-ro | 445 | 2.09 | 0 | 23 | 1 | 10600 | 0 | 6000 | 17500 | 34077 |
| always-gl | 427 | 2.00 | 0 | 21 | 2 | 10600 | 0 | 6000 | 17500 | 34079 |
| always-oc | 373 | 1.75 | 0 | 22 | 2 | 10600 | 0 | 6000 | 17500 | 34078 |
| init | 223 | 1.05 | 0 | 23 | 24 | 10600 | 0 | 6000 | 0 | 16577 |

Energía inicial reportada por el CLI Rust: **257981** (comparar con SA E_total = 34078).

## Acuerdo

- Conceptos: **213**
- ES y PT adaptados idénticos: 51/213
- SA = ES (ortografía Vulgultra): 24/213
- SA = PT: 27/213
- SA = FR: 53/213
- SA = IT: 9/213
- SA = shortest (crudo): 120/213
- SA = greedy-phones: 120/213
- SA ≠ greedy-phones: 93/213

## Frases de demostración

Con conjugación y concordancia. Artículo **o/a**. Copula 3sg **e**.
Verbo = tema + la fila de presente elegida. El objeto va en acusativo.

### El gato rojo sonríe.

PT: O gato vermelho sorri.

```
Vulgultra  o  gato  roso  sure
src    [pt]  [ca]  [dlm]  [fr]
es     el/la  gato  rojo  sonreír
pt     o  gato  vermelho  sorrir
σ      7
```

### El perro es grande.

PT: O cão é grande.

```
Vulgultra  o  kano  e  grando
src    [pt]  [an]  [pt]  [eml]
es     el/la  perro  es  grande
pt     o  cão  é  grande
σ      6
```

### El agua es fría.

PT: A água é fria.

```
Vulgultra  a  ewa  e  frea
src    [pt]  [glw]  [pt]  [frp]
es     el/la  agua  es  frío
pt     a  água  é  frio
σ      6
```

### Yo veo el sol.

PT: Eu vejo o sol.

```
Vulgultra  yo  veo  o  solon
src    [an]  [es]  [pt]  [ext]
es     yo  ver  el/la  sol
pt     eu  ver  o  sol
σ      6
```

### La mujer come pez.

PT: A mulher come peixe.

```
Vulgultra  a  na  meke  peson
src    [pt]  [lld]  [rup]  [ast]
es     el/la  mujer  comer  pez
pt     a  mulher  comer  peixe
σ      6
```

### El fuego es rojo.

PT: O fogo é vermelho.

```
Vulgultra  o  fo  e  roso
src    [pt]  [fr]  [pt]  [dlm]
es     el/la  fuego  es  rojo
pt     o  fogo  é  vermelho
σ      5
```

### Nosotros damos agua.

PT: Nós damos água.

```
Vulgultra  no  daens  ewan
src    [frp]  [an]  [glw]
es     nosotros  dar  agua
pt     nós  dar  água
σ      5
```

### El hombre es bueno.

PT: O homem é bom.

```
Vulgultra  o  omo  e  bono
src    [pt]  [eml]  [pt]  [fr]
es     el/la  hombre  es  bueno
pt     o  homem  é  bom
σ      6
```

### La noche es negra.

PT: A noite é preta.

```
Vulgultra  a  nota  e  nera
src    [pt]  [eml]  [pt]  [frp]
es     el/la  noche  es  negro
pt     a  noite  é  preto
σ      6
```

### Tú oyes el viento.

PT: Tu ouves o vento.

```
Vulgultra  tu  udas  o  venton
src    [an]  [ruq]  [pt]  [ca]
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
| perro | **kan** | `an` | 1 | **xyen** | `fr` | 1 |

## Tabla por concepto

| glosa | es | pt | fr | it | ca | Vulgultra | src | σ | por qué | bin |
|---|---|---|---|---|---|---|---|---:|---|---|
| a | a | a | à | a | a | **a** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| afilado | afilado | afiado | aigu | affilato | esmolat | **ag** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| agua | agua | água | eau | acqua | aigua | **ew** | `glw` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| ala | ala | asa | aile | ala | ala | **e** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| algunos | algunos | alguns | quelques | alcuni | alguns | **nek** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | — |
| allí | allí | ali | là | lì | allà | **li** | `it` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| amarillo | amarillo | amarelo | jaune | giallo | groc | **xon** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| ancho | ancho | largo | large | largo | ample | **larg** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| animal | animal | animal | animal | animale | animal | **bet** | `glw` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| apretar | apretar | apertar | presser | spremere | prémer | **stren** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| apuñalar | apuñalar | esfaquear | poignarder | pugnalare | apunyalar | **pung** | `ruq` | 1 | única legal a σ=1 | opaco |
| aquí | aquí | aqui | ici | qui | aquí | **ka** | `co` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| arena | arena | areia | sable | sabbia | sorra | **svlon** | `wa` | 1 | única legal a σ=1 | opaco |
| atar | atar | atar | lier | legare | lligar | **lyer** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| año | año | ano | année | anno | any | **an** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| beber | beber | beber | boire | bere | beure | **bor** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| blanco | blanco | branco | blanc | bianco | blanc | **blank** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| boca | boca | boca | bouche | bocca | boca | **bux** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| bosque | bosque | floresta | forêt | foresta | bosc | **bosk** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| bueno | bueno | bom | bon | buono | bo | **bon** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| cabeza | cabeza | cabeça | tête | testa | cap | **kap** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| caer | caer | cair | tomber | cadere | caure | **kad** | `lmo` | 1 | única legal a σ=1 | adivinable |
| caliente | caliente | quente | chaud | caldo | calent | **kald** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| caminar | caminar | andar | marcher | camminare | caminar | **ir** | `rm` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| camino | camino | estrada | route | strada | camí | **rut** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| cantar | cantar | cantar | chanter | cantare | cantar | **kint** | `ruo` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| carne | carne | carne | viande | carne | carn | **xar** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| cavar | cavar | cavar | creuser | scavare | cavar | **ka** | `oc` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| cazar | cazar | caçar | chasser | cacciare | caçar | **kasar** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| ceniza | ceniza | cinza | cendre | cenere | cendra | **sner** | `pms` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| cerca | cerca | perto | près | vicino | prop | **pre** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| chupar | chupar | chupar | sucer | succhiare | xuclar | **sug** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| cielo | cielo | céu | ciel | cielo | cel | **syel** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| cinco | cinco | cinco | cinq | cinque | cinc | **sink** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| cola | cola | rabo | queue | coda | cua | **kwa** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| comer | comer | comer | manger | mangiare | menjar | **mek** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| con | con | com | avec | con | amb | **kon** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| congelar | congelar | congelar | geler | gelare | gelar | **gler** | `nrf` | 1 | única legal a σ=1 | opaco |
| contar | contar | contar | compter | contare | comptar | **kontar** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| corazón | corazón | coração | cœur | cuore | cor | **kor** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| correcto | correcto | correto | correct | corretto | correcte | **yust** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| cortar | cortar | cortar | couper | tagliare | tallar | **talx** | `ruo` | 1 | única legal a σ=1 | opaco |
| corteza | corteza | casca | écorce | corteccia | escorça | **skwaz** | `wa` | 1 | única legal a σ=1 | opaco |
| corto | corto | curto | court | corto | curt | **kurt** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| coser | coser | costurar | coudre | cucire | cosir | **kos** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| cuatro | cuatro | quatro | quatre | quattro | quatre | **kat** | `glw` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| cuello | cuello | pescoço | cou | collo | coll | **kol** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| cuerda | cuerda | corda | corde | corda | corda | **kord** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| cuerno | cuerno | chifre | corne | corno | banya | **korn** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| cuándo | cuándo | quando | quand | quando | quan | **kand** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| cómo | cómo | como | comment | come | com | **kum** | `nrf` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| dar | dar | dar | donner | dare | donar | **dar** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| decir | decir | dizer | dire | dire | dir | **dir** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| delgado | delgado | fino | mince | sottile | prim | **fin** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| derecha | derecha | direita | droite | destra | dreta | **dret** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| diente | diente | dente | dent | dente | dent | **dent** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| dormir | dormir | dormir | dormir | dormire | dormir | **dorm** | `ruq` | 1 | única legal a σ=1 | adivinable |
| dos | dos | dois | deux | due | dos | **dwi** | `scn` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| día | día | dia | jour | giorno | dia | **dya** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| dónde | dónde | onde | où | dove | on | **an** | `an` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| el | el | o | le | il | el | **el** | `ast` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| ellos | ellos | eles | ils | loro | ells | **lor** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| empujar | empujar | empurrar | pousser | spingere | empènyer | **sping** | `lmo` | 1 | única legal a σ=1 | opaco |
| en | en | em | dans | in | en | **en** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| entrañas | entrañas | tripas | entrailles | viscere | budells | **tripas** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| escupir | escupir | cuspir | cracher | sputare | escopir | **spwe** | `pms` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| eso | eso | isso | cela | quello | aquell | **kwel** | `ist` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| espalda | espalda | costas | dos | schiena | esquena | **do** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| esposa | esposa | esposa | épouse | moglie | muller | **na** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| esposo | esposo | marido | mari | marito | marit | **om** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| esto | esto | isto | ceci | questo | aquest | **xu** | `nrf` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| estrecho | estrecho | estreito | étroit | stretto | estret | **stret** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| estrella | estrella | estrela | étoile | stella | estrella | **stla** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| flor | flor | flor | fleur | fiore | flor | **flor** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| flotar | flotar | flutuar | flotter | galleggiare | flotar | **flotar** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| fluir | fluir | fluir | couler | fluire | fluir | **xor** | `lmo` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| frotar | frotar | esfregar | frotter | strofinare | fregar | **frek** | `rup` | 1 | única legal a σ=1 | opaco |
| fruta | fruta | fruta | fruit | frutto | fruita | **frut** | `fur` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| frío | frío | frio | froid | freddo | fred | **fre** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| fuego | fuego | fogo | feu | fuoco | foc | **fo** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| gata | gata | gata | chatte | gatta | gata | **xat** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| gato | gato | gato | chat | gatto | gat | **gat** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| girar | girar | girar | tourner | girare | girar | **turn** | `ruo` | 1 | única legal a σ=1 | opaco |
| golpear | golpear | bater | frapper | colpire | pegar | **bat** | `lmo` | 1 | única legal a σ=1 | adivinable |
| grande | grande | grande | grand | grande | gran | **grand** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| grasa | grasa | gordura | graisse | grasso | greix | **gras** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| grueso | grueso | grosso | épais | spesso | gruixut | **gros** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| gusano | gusano | verme | ver | verme | cuc | **ver** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| hielo | hielo | gelo | glace | ghiaccio | gel | **glaz** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| hierba | hierba | erva | herbe | erba | herba | **erb** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| hinchar | hinchar | inchar | enfler | gonfiare | inflar | **gonfler** | `glw` | 2 | σ=2; desempate por segmentos del léxico global | opaco |
| hoja | hoja | folha | feuille | foglia | fulla | **fya** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| hombre | hombre | homem | homme | uomo | home | **om** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| hueso | hueso | osso | os | osso | os | **os** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| huevo | huevo | ovo | œuf | uovo | ou | **o** | `glw` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| humo | humo | fumo | fumée | fumo | fum | **fum** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| hígado | hígado | fígado | foie | fegato | fetge | **fwa** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| izquierda | izquierda | esquerda | gauche | sinistra | esquerra | **gox** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| jugar | jugar | jogar | jouer | giocare | jugar | **xur** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| lago | lago | lago | lac | lago | llac | **lak** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| lanzar | lanzar | atirar | jeter | lanciare | llançar | **lyar** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| largo | largo | longo | long | lungo | llarg | **long** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| lavar | lavar | lavar | laver | lavare | rentar | **la** | `gsc` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| lejos | lejos | longe | loin | lontano | lluny | **lon** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| lengua | lengua | língua | langue | lingua | llengua | **lang** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| liso | liso | liso | lisse | liscio | llis | **lis** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| lleno | lleno | cheio | plein | pieno | ple | **plen** | `an` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| lluvia | lluvia | chuva | pluie | pioggia | pluja | **plo** | `glw` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| luna | luna | lua | lune | luna | lluna | **lun** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| madre | madre | mãe | mère | madre | mare | **mer** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| malo | malo | mau | mauvais | cattivo | dolent | **maw** | `pt` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| mano | mano | mão | main | mano | mà | **man** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| mar | mar | mar | mer | mare | mar | **mar** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| matar | matar | matar | tuer | uccidere | matar | **tur** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| mojado | mojado | molhado | mouillé | bagnato | mullat | **ud** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| montaña | montaña | montanha | montagne | montagna | muntanya | **mont** | `fur` | 1 | única legal a σ=1 | adivinable |
| morder | morder | morder | mordre | mordere | mossegar | **mord** | `lld` | 1 | única legal a σ=1 | adivinable |
| morir | morir | morrer | mourir | morire | morir | **mor** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| muchos | muchos | muitos | beaucoup | molti | molts | **tant** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| mujer | mujer | mulher | femme | donna | dona | **na** | `lld` | 1 | única legal a σ=1 | opaco |
| nadar | nadar | nadar | nager | nuotare | nedar | **na** | `lij` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| nariz | nariz | nariz | nez | naso | nas | **nas** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| negro | negro | preto | noir | nero | negre | **ner** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| niebla | niebla | nevoeiro | brouillard | nebbia | boira | **brum** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| nieve | nieve | neve | neige | neve | neu | **ne** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| niño | niño | criança | enfant | bambino | nen | **fyo** | `ist` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| no | no | não | non | non | no | **no** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| noche | noche | noite | nuit | notte | nit | **not** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| nombre | nombre | nome | nom | nome | nom | **nom** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| nosotros | nosotros | nós | nous | noi | nosaltres | **no** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| nube | nube | nuvem | nuage | nuvola | núvol | **nor** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| nuevo | nuevo | novo | nouveau | nuovo | nou | **nov** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| ojo | ojo | olho | œil | occhio | ull | **wely** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| oler | oler | cheirar | sentir | odorare | ensumar | **senti** | `gsc` | 2 | σ=2; desempate por segmentos del léxico global | opaco |
| oreja | oreja | orelha | oreille | orecchio | orella | **or** | `wa` | 1 | única legal a σ=1 | adivinable |
| otro | otro | outro | autre | altro | altre | **ot** | `nrf` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| oír | oír | ouvir | entendre | sentire | sentir | **ud** | `ruq` | 1 | única legal a σ=1 | opaco |
| padre | padre | pai | père | padre | pare | **per** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| palo | palo | pau | bâton | bastone | pal | **paw** | `mwl` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| parar | parar | ficar | tenir | stare | estar | **star** | `vec` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| partir | partir | fender | fendre | spaccare | fendre | **ne** | `gsc` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| pecho | pecho | peito | sein | petto | pit | **pet** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| pelear | pelear | lutar | combattre | combattere | lluitar | **bat** | `pcd` | 1 | única legal a σ=1 | opaco |
| pelo | pelo | cabelo | cheveu | capello | cabell | **per** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| pensar | pensar | pensar | penser | pensare | pensar | **pensar** | `an` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| pequeño | pequeño | pequeno | petit | piccolo | petit | **mik** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| perra | perra | cadela | chienne | cagna | gossa | **xyen** | `fr` | 1 | única legal a σ=1 | opaco |
| perro | perro | cão | chien | cane | gos | **kan** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| persona | persona | pessoa | personne | persona | persona | **om** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| pesado | pesado | pesado | lourd | pesante | pesat | **lur** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| pez | pez | peixe | poisson | pesce | peix | **pes** | `ast` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| pie | pie | pé | pied | piede | peu | **pe** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| piedra | piedra | pedra | pierre | pietra | pedra | **pyerr** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| piel | piel | pele | peau | pelle | pell | **pel** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| pierna | pierna | perna | jambe | gamba | cama | **pyor** | `ruo` | 1 | única legal a σ=1 | adivinable |
| piojo | piojo | piolho | pou | pidocchio | poll | **pu** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| pluma | pluma | pena | plume | piuma | ploma | **plum** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| pocos | pocos | poucos | peu | pochi | pocs | **po** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| podrido | podrido | podre | pourri | marcio | podrit | **mers** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| polvo | polvo | pó | poussière | polvere | pols | **praf** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| porque | porque | porque | parce | perché | perquè | **ka** | `sc` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| pájaro | pájaro | pássaro | oiseau | uccello | ocell | **ul** | `rgn` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| quemar | quemar | queimar | brûler | bruciare | cremar | **ard** | `rup` | 1 | única legal a σ=1 | opaco |
| quién | quién | quem | qui | chi | qui | **ki** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| qué | qué | que | quoi | che | què | **ke** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| rascar | rascar | coçar | gratter | grattare | gratar | **gratar** | `ca` | 2 | σ=2; desempate por segmentos del léxico global | adivinable |
| raíz | raíz | raiz | racine | radice | arrel | **red** | `eml` | 1 | única legal a σ=1 | adivinable |
| recto | recto | direito | droit | dritto | recte | **drit** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| redondo | redondo | redondo | rond | rotondo | rodó | **ron** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| respirar | respirar | respirar | respirer | respirare | respirar | **spirar** | `dlm` | 2 | σ=2; desempate por segmentos del léxico global | adivinable |
| reír | reír | rir | rire | ridere | riure | **rir** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| rodilla | rodilla | joelho | genou | ginocchio | genoll | **zno** | `eml` | 1 | única legal a σ=1 | opaco |
| rojo | rojo | vermelho | rouge | rosso | roig | **ros** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| romo | romo | cego | émoussé | smussato | rom | **ems** | `gsc` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| río | río | rio | rivière | fiume | riu | **ryo** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| saber | saber | saber | savoir | sapere | saber | **xti** | `ro` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| sal | sal | sal | sel | sale | sal | **sal** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| sangre | sangre | sangue | sang | sangue | sang | **sang** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| secar | secar | enxugar | essuyer | asciugare | eixugar | **sterg** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| seco | seco | seco | sec | secco | sec | **sek** | `ca` | 1 | única legal a σ=1 | transparente |
| semilla | semilla | semente | graine | seme | llavor | **gren** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| sentar | sentar | sentar | asseoir | sedere | seure | **ed** | `ruo` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| ser | ser | ser | être | essere | ser | **ser** | `lad` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| serpiente | serpiente | serpente | serpent | serpente | serp | **serp** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| si | si | se | si | se | si | **se** | `dlm` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| sol | sol | sol | soleil | sole | sol | **sol** | `ext` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| sonreír | sonreír | sorrir | sourire | sorridere | somriure | **surir** | `fr` | 2 | σ=2; desempate por segmentos del léxico global | transparente |
| soplar | soplar | soprar | souffler | soffiare | bufar | **sfya** | `lmo` | 1 | única legal a σ=1 | opaco |
| sucio | sucio | sujo | sale | sporco | brut | **spork** | `eml` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| temer | temer | temer | craindre | temere | témer | **krend** | `wa` | 1 | única legal a σ=1 | opaco |
| tener | tener | ter | tenir | tenere | tenir | **ter** | `gl` | 1 | única legal a σ=1 | transparente |
| tierra | tierra | terra | terre | terra | terra | **ter** | `pcd` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| tirar | tirar | puxar | tirer | tirare | estirar | **tya** | `lij` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| todo | todo | todo | tout | tutto | tot | **tot** | `an` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| tres | tres | três | trois | tre | tres | **tres** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| tú | tú | tu | tu | tu | tu | **tu** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| uno | uno | um | un | uno | un | **un** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| uña | uña | unha | ongle | unghia | ungla | **ong** | `wa` | 1 | única legal a σ=1 | adivinable |
| venir | venir | vir | venir | venire | venir | **vir** | `gl` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| ver | ver | ver | voir | vedere | veure | **ver** | `es` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| verde | verde | verde | vert | verde | verd | **verd** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| viejo | viejo | velho | vieux | vecchio | vell | **vyo** | `fr` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| viento | viento | vento | vent | vento | vent | **vent** | `ca` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| vientre | vientre | ventre | ventre | pancia | ventre | **vent** | `pcd` | 1 | única legal a σ=1 | adivinable |
| vivir | vivir | viver | vivre | vivere | viure | **vi** | `lld` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| volar | volar | voar | voler | volare | volar | **zbor** | `rup` | 1 | única legal a σ=1 | opaco |
| vomitar | vomitar | vomitar | vomir | vomitare | vomitar | **vom** | `ruq` | 1 | única legal a σ=1 | opaco |
| vosotros | vosotros | vocês | vous | voi | vosaltres | **vo** | `frp` | 1 | σ=1; desempate por segmentos del léxico global | adivinable |
| y | y | e | et | e | i | **e** | `co` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| yacer | yacer | jazer | gésir | giacere | jeure | **zak** | `rup` | 1 | σ=1; desempate por segmentos del léxico global | opaco |
| yo | yo | eu | je | io | jo | **yo** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |
| árbol | árbol | árvore | arbre | albero | arbre | **ab** | `glw` | 1 | única legal a σ=1 | adivinable |
| él | él | ele | il | lui | ell | **el** | `an` | 1 | σ=1; desempate por segmentos del léxico global | transparente |

## Apéndice: SA ≠ greedy-phones

| glosa | SA | src | σ | greedy-phones | src | σ | razón |
|---|---|---|---:|---|---|---:|---|
| afilado | ag | `frp` | 1 | eg | `fr` | 1 | misma σ, otra forma |
| agua | ew | `glw` | 1 | o | `fr` | 1 | misma σ, otra forma |
| allí | li | `it` | 1 | ci | `co` | 1 | misma σ, otra forma |
| amarillo | xon | `fr` | 1 | grok | `ca` | 1 | misma σ, otra forma |
| año | an | `eml` | 1 | any | `ca` | 1 | misma σ, otra forma |
| beber | bor | `pcd` | 1 | bwar | `fr` | 1 | misma σ, otra forma |
| blanco | blank | `dlm` | 1 | blak | `ca` | 1 | misma σ, otra forma |
| bueno | bon | `fr` | 1 | bo | `ca` | 1 | misma σ, otra forma |
| caminar | ir | `rm` | 1 | yi | `lld` | 1 | misma σ, otra forma |
| camino | rut | `fr` | 1 | vya | `dlm` | 1 | misma σ, otra forma |
| carne | xar | `frp` | 1 | karn | `ca` | 1 | misma σ, otra forma |
| cavar | ka | `oc` | 1 | ka | `gsc` | 1 | misma σ, otra forma |
| cerca | pre | `fr` | 1 | prop | `ca` | 1 | misma σ, otra forma |
| chupar | sug | `rup` | 1 | scer | `eml` | 1 | misma σ, otra forma |
| cielo | syel | `fr` | 1 | sel | `ca` | 1 | misma σ, otra forma |
| cinco | sink | `fr` | 1 | sik | `ca` | 1 | misma σ, otra forma |
| comer | mek | `rup` | 1 | mink | `ruo` | 1 | misma σ, otra forma |
| coser | kos | `rup` | 1 | kwir | `eml` | 1 | misma σ, otra forma |
| cuello | kol | `eml` | 1 | koly | `ca` | 1 | misma σ, otra forma |
| cuándo | kand | `dlm` | 1 | kwan | `an` | 1 | misma σ, otra forma |
| cómo | kum | `nrf` | 1 | kom | `ca` | 1 | misma σ, otra forma |
| delgado | fin | `dlm` | 1 | prim | `ca` | 1 | misma σ, otra forma |
| dos | dwi | `scn` | 1 | dos | `an` | 1 | misma σ, otra forma |
| el | el | `ast` | 1 | o | `an` | 1 | misma σ, otra forma |
| ellos | lor | `eml` | 1 | els | `an` | 1 | misma σ, otra forma |
| escupir | spwe | `pms` | 1 | spwar | `dlm` | 1 | misma σ, otra forma |
| eso | kwel | `ist` | 1 | kol | `dlm` | 1 | misma σ, otra forma |
| espalda | do | `fr` | 1 | dri | `dlm` | 1 | misma σ, otra forma |
| esposa | na | `lld` | 1 | mwir | `fur` | 1 | misma σ, otra forma |
| esposo | om | `lld` | 1 | mar | `fur` | 1 | misma σ, otra forma |
| esto | xu | `nrf` | 1 | cest | `dlm` | 1 | misma σ, otra forma |
| estrecho | stret | `eml` | 1 | strent | `dlm` | 1 | misma σ, otra forma |
| fruta | frut | `fur` | 1 | frot | `eml` | 1 | misma σ, otra forma |
| frío | fre | `frp` | 1 | fred | `ca` | 1 | misma σ, otra forma |
| fuego | fo | `fr` | 1 | fok | `ca` | 1 | misma σ, otra forma |
| grande | grand | `eml` | 1 | gran | `an` | 1 | misma σ, otra forma |
| grasa | gras | `eml` | 1 | grexx | `ca` | 1 | misma σ, otra forma |
| gusano | ver | `fr` | 1 | kuk | `ca` | 1 | misma σ, otra forma |
| hielo | glaz | `fr` | 1 | xel | `ca` | 1 | misma σ, otra forma |
| hinchar | gonfler | `glw` | 2 | incar | `an` | 2 | misma σ, otra forma |
| hoja | fya | `lld` | 1 | foy | `eml` | 1 | misma σ, otra forma |
| huevo | o | `glw` | 1 | ob | `ca` | 1 | misma σ, otra forma |
| izquierda | gox | `fr` | 1 | sank | `dlm` | 1 | misma σ, otra forma |
| lago | lak | `dlm` | 1 | lyak | `ca` | 1 | misma σ, otra forma |
| largo | long | `eml` | 1 | lyarg | `ca` | 1 | misma σ, otra forma |
| lejos | lon | `pcd` | 1 | lyuny | `ca` | 1 | misma σ, otra forma |
| liso | lis | `dlm` | 1 | lyis | `ca` | 1 | misma σ, otra forma |
| lluvia | plo | `glw` | 1 | plov | `frp` | 1 | misma σ, otra forma |
| malo | maw | `pt` | 1 | ri | `dlm` | 1 | misma σ, otra forma |
| montaña | mont | `fur` | 1 | mont | `dlm` | 1 | misma σ, otra forma |
| morir | mor | `rup` | 1 | mwi | `lij` | 1 | misma σ, otra forma |
| muchos | tant | `eml` | 1 | mols | `ca` | 1 | misma σ, otra forma |
| nadar | na | `lij` | 1 | ned | `eml` | 1 | misma σ, otra forma |
| negro | ner | `frp` | 1 | fox | `dlm` | 1 | misma σ, otra forma |
| nieve | ne | `frp` | 1 | neb | `ca` | 1 | misma σ, otra forma |
| niño | fyo | `ist` | 1 | nen | `ca` | 1 | misma σ, otra forma |
| noche | not | `eml` | 1 | nit | `ca` | 1 | misma σ, otra forma |
| nosotros | no | `frp` | 1 | nu | `dlm` | 1 | misma σ, otra forma |
| nube | nor | `ro` | 1 | nwax | `fr` | 1 | misma σ, otra forma |
| nuevo | nov | `eml` | 1 | nob | `ca` | 1 | misma σ, otra forma |
| ojo | wely | `frp` | 1 | uly | `ca` | 1 | misma σ, otra forma |
| oler | senti | `gsc` | 2 | oler | `an` | 2 | misma σ, otra forma |
| palo | paw | `mwl` | 1 | pal | `ca` | 1 | misma σ, otra forma |
| parar | star | `vec` | 1 | tar | `ast` | 1 | misma σ, otra forma |
| pecho | pet | `dlm` | 1 | pit | `ca` | 1 | misma σ, otra forma |
| pelo | per | `ro` | 1 | pet | `gsc` | 1 | misma σ, otra forma |
| pequeño | mik | `ro` | 1 | muk | `dlm` | 1 | misma σ, otra forma |
| pie | pe | `eml` | 1 | pye | `an` | 1 | misma σ, otra forma |
| piel | pel | `eml` | 1 | pyel | `an` | 1 | misma σ, otra forma |
| piojo | pu | `fr` | 1 | poly | `ca` | 1 | misma σ, otra forma |
| pocos | po | `fr` | 1 | pok | `dlm` | 1 | misma σ, otra forma |
| polvo | praf | `ro` | 1 | pols | `ca` | 1 | misma σ, otra forma |
| porque | ka | `sc` | 1 | pars | `fr` | 1 | misma σ, otra forma |
| quién | ki | `ca` | 1 | kyen | `an` | 1 | misma σ, otra forma |
| rascar | gratar | `ca` | 2 | raskar | `an` | 2 | misma σ, otra forma |
| redondo | ron | `fr` | 1 | tond | `eml` | 1 | misma σ, otra forma |
| rojo | ros | `dlm` | 1 | roxc | `ca` | 1 | misma σ, otra forma |
| romo | ems | `gsc` | 1 | rom | `ca` | 1 | misma σ, otra forma |
| sangre | sang | `fr` | 1 | sag | `ca` | 1 | misma σ, otra forma |
| secar | sterg | `rup` | 1 | sger | `eml` | 1 | misma σ, otra forma |
| semilla | gren | `fr` | 1 | zmens | `eml` | 1 | misma σ, otra forma |
| sentar | ed | `ruo` | 1 | ster | `eml` | 1 | misma σ, otra forma |
| ser | ser | `lad` | 1 | ser | `an` | 1 | misma σ, otra forma |
| si | se | `dlm` | 1 | si | `an` | 1 | misma σ, otra forma |
| sol | sol | `ext` | 1 | sol | `an` | 1 | misma σ, otra forma |
| sonreír | surir | `fr` | 2 | somyar | `dlm` | 2 | misma σ, otra forma |
| sucio | spork | `eml` | 1 | brut | `ca` | 1 | misma σ, otra forma |
| tierra | ter | `pcd` | 1 | terr | `fr` | 1 | misma σ, otra forma |
| venir | vir | `gl` | 1 | nyir | `eml` | 1 | misma σ, otra forma |
| ver | ver | `es` | 1 | ver | `ast` | 1 | misma σ, otra forma |
| viejo | vyo | `fr` | 1 | vely | `ca` | 1 | misma σ, otra forma |
| vosotros | vo | `frp` | 1 | vu | `fr` | 1 | misma σ, otra forma |
| y | e | `co` | 1 | i | `an` | 1 | misma σ, otra forma |

## Caveats

- La glosa del scorecard es española; el `id` inglés del gold list no es fuente.
- El inglés no es lengua fuente. El latín está reservado y no entra en el knapsack.
- Epitran usa la lect hermana cuando no hay mapa propio (Oil←fr, retorromance y dálmata←it, asturiano←es, oriental←ro): `água`→`aga`, `olho`→`olo`, `ojo`/`rojo`→`okso`/`rokso`. `chat`→`xa` es la ortografía de `ʃ`.
- Las desinencias comparan tablas de lect atestiguadas y una tabla productiva hecha con segmentos observados; esta última no afirma que sus combinaciones sean morfemas atestiguados. El recocido solo mueve raíces dentro del corte de σ mínima.
