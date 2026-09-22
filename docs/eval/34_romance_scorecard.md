# Vulgultra Swadesh — 36 daughter lects

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

Una raíz no se elige “porque sí”. El recocido minimiza

$$
E = 1000\sum_r \sigma(r) + 40|\Phi| + 1(N_{\mathrm{src}}-n_{\mathrm{lects}}) + 0.02\,\overline{\mathrm{gap}}
+ 200\sum_e \sigma(e) + 100000\cdot\mathrm{coll} + 2000\cdot\mathrm{viol} + 500\sum_{\mathrm{row}}\max(0,2-d)
$$

| término | peso | qué hace en la práctica |
|---|---:|---|
| **σ raíces** | 1000 | una sílaba extra gana a todo lo de abajo |
| **\|Φ\|** | 40 | 40×23=920 < 1000: inventario global, nunca compra una σ |
| **diversidad** | 1 | a igual σ e igual Φ, maximizar lects distintas (36 < 40) |
| support medio | 0.02 | más fino que un lect |
| σ desinencias | 200 | terminaciones 1σ |
| colisiones | 100000 | duro dentro de una fila |
| fonotáctica | 2000 | resto tras repair |
| distancia desinencias | 500 | dentro de una fila |

Orden: legal → min σ → min \|Φ\| → max lects → support.
Un lect oscuro gana solo en empate de σ que no agrande Φ.

## Veredicto

Frente a **español** y **portugués** (las lenguas de inspección): el mixto tiene **223** sílabas de raíz vs ES 450 y PT 442, con **0** violaciones (ES 0, PT 0).

Frente a **francés**: always-fr suma 327σ con **0** violaciones. El mixto es 104σ más corto, con 0 violaciones. Italiano suma 518σ (0 viol.).

Calidad del optimizador: set-cover Σσ=223 |Φ|=22 lects=36 E=257981; SA Σσ=223 |Φ|=22 lects=36 E=257981 (acuerdo con set-cover 213/213, con support-shortest 195/213). support-shortest suma 223σ. El shortest crudo llega a 223σ con 0 violaciones.

Desinencias enumeradas antes del recocido: tema nominal `o`, tiempos verbales `prs=frp,pst=ca,fut=eml,subj=ca,theme_i=ca,theme_a=ca`. Cada tiempo es una fila; el SA no las mueve.

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
`set-cover` es el init: mínima σ, luego menos fonemas nuevos, luego un lect nuevo.
`support-shortest` es el antiguo legal-shortest ordenado por support.

| política | Σσ raíces | media σ | viol | \|Φ\| | lects | E_root | E_norm | E_end | E_coll | E_tact | E_dist | E_total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sa | 223 | 1.05 | 0 | 22 | 36 | 223000 | 1 | 10600 | 0 | 6000 | 17500 | 257981 |
| set-cover | 223 | 1.05 | 0 | 22 | 36 | 223000 | 1 | 10600 | 0 | 6000 | 17500 | 257981 |
| support-shortest | 223 | 1.05 | 0 | 22 | 24 | 223000 | 1 | 10600 | 0 | 6000 | 17500 | 257993 |
| shortest | 223 | 1.05 | 0 | 22 | 24 | 223000 | 1 | 10600 | 0 | 6000 | 17500 | 257993 |
| always-es | 450 | 2.11 | 0 | 21 | 2 | 450000 | 1 | 10600 | 0 | 6000 | 17500 | 484975 |
| always-pt | 442 | 2.08 | 0 | 22 | 2 | 442000 | 1 | 10600 | 0 | 6000 | 17500 | 477015 |
| always-fr | 327 | 1.54 | 0 | 22 | 4 | 327000 | 1 | 10600 | 0 | 6000 | 17500 | 362013 |
| always-it | 518 | 2.43 | 0 | 23 | 1 | 518000 | 1 | 10600 | 0 | 6000 | 17500 | 553056 |
| always-ca | 363 | 1.70 | 0 | 22 | 4 | 363000 | 1 | 10600 | 0 | 6000 | 17500 | 398013 |
| always-ro | 445 | 2.09 | 0 | 23 | 1 | 445000 | 1 | 10600 | 0 | 6000 | 17500 | 480056 |
| always-gl | 427 | 2.00 | 0 | 21 | 2 | 427000 | 1 | 10600 | 0 | 6000 | 17500 | 461975 |
| always-oc | 373 | 1.75 | 0 | 22 | 2 | 373000 | 1 | 10600 | 0 | 6000 | 17500 | 408015 |
| init | 223 | 1.05 | 0 | 22 | 36 | 223000 | 1 | 10600 | 0 | 6000 | 17500 | 257981 |

Energía inicial reportada por el CLI Rust: **257981** (comparar con SA E_total = 257981).

## Acuerdo

- Conceptos: **213**
- ES y PT adaptados idénticos: 51/213
- SA = ES (ortografía Vulgultra): 24/213
- SA = PT: 27/213
- SA = FR: 53/213
- SA = IT: 9/213
- SA = shortest (crudo): 195/213
- SA = set-cover: 213/213
- SA ≠ set-cover: 0/213

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

| glosa | es | pt | fr | it | ca | Vulgultra | src | σ | sup | por qué | bin |
|---|---|---|---|---|---|---|---|---:|---:|---|---|
| a | a | a | à | a | a | **a** | `an` | 1 | 31 | σ=1, support=31 | transparente |
| afilado | afilado | afiado | aigu | affilato | esmolat | **ag** | `frp` | 1 | 4 | σ=1, support=4 | opaco |
| agua | agua | água | eau | acqua | aigua | **ew** | `glw` | 1 | 2 | σ=1, support=2 | adivinable |
| ala | ala | asa | aile | ala | ala | **e** | `fr` | 1 | 5 | σ=1, support=5 | adivinable |
| algunos | algunos | alguns | quelques | alcuni | alguns | **nek** | `dlm` | 1 | 1 | σ=1, support=1 (empate con fr,frp,glw,pcd) | — |
| allí | allí | ali | là | lì | allà | **li** | `it` | 1 | 1 | σ=1 pero support 1 < 12 | transparente |
| amarillo | amarillo | amarelo | jaune | giallo | groc | **xon** | `fr` | 1 | 4 | σ=1, support=4 | opaco |
| ancho | ancho | largo | large | largo | ample | **larg** | `dlm` | 1 | 8 | σ=1, support=8 | transparente |
| animal | animal | animal | animal | animale | animal | **bet** | `glw` | 1 | 3 | σ=1, support=3 | opaco |
| apretar | apretar | apertar | presser | spremere | prémer | **stren** | `fur` | 1 | 1 | σ=1, support=1 (empate con lmo,ruq) | opaco |
| apuñalar | apuñalar | esfaquear | poignarder | pugnalare | apunyalar | **pung** | `ruq` | 1 | 1 | única legal a σ=1 | opaco |
| aquí | aquí | aqui | ici | qui | aquí | **ka** | `co` | 1 | 4 | σ=1, support=4 | adivinable |
| arena | arena | areia | sable | sabbia | sorra | **svlon** | `wa` | 1 | 1 | única legal a σ=1 | opaco |
| atar | atar | atar | lier | legare | lligar | **lyer** | `fr` | 1 | 3 | σ=1, support=3 | adivinable |
| año | año | ano | année | anno | any | **an** | `eml` | 1 | 12 | σ=1, support=12 | transparente |
| beber | beber | beber | boire | bere | beure | **bor** | `pcd` | 1 | 2 | σ=1, support=2 | adivinable |
| blanco | blanco | branco | blanc | bianco | blanc | **blank** | `dlm` | 1 | 8 | σ=1, support=8 | transparente |
| boca | boca | boca | bouche | bocca | boca | **bux** | `fr` | 1 | 3 | σ=1, support=3 | adivinable |
| bosque | bosque | floresta | forêt | foresta | bosc | **bosk** | `ca` | 1 | 8 | σ=1, support=8 | transparente |
| bueno | bueno | bom | bon | buono | bo | **bon** | `fr` | 1 | 13 | σ=1, support=13 | transparente |
| cabeza | cabeza | cabeça | tête | testa | cap | **kap** | `ca` | 1 | 7 | σ=1, support=7 | opaco |
| caer | caer | cair | tomber | cadere | caure | **kad** | `lmo` | 1 | 4 | única legal a σ=1 | adivinable |
| caliente | caliente | quente | chaud | caldo | calent | **kald** | `dlm` | 1 | 6 | σ=1, support=6 | opaco |
| caminar | caminar | andar | marcher | camminare | caminar | **ir** | `rm` | 1 | 1 | σ=1, support=1 (empate con lld,ruo) | opaco |
| camino | camino | estrada | route | strada | camí | **rut** | `fr` | 1 | 4 | σ=1, support=4 | opaco |
| cantar | cantar | cantar | chanter | cantare | cantar | **kint** | `ruo` | 1 | 1 | σ=1, support=1 (empate con ruq) | adivinable |
| carne | carne | carne | viande | carne | carn | **xar** | `frp` | 1 | 4 | σ=1, support=4 (empate con ca,lmo,pms,rm) | adivinable |
| cavar | cavar | cavar | creuser | scavare | cavar | **ka** | `oc` | 1 | 2 | σ=1, support=2 (empate con rup,ruq) | adivinable |
| cazar | cazar | caçar | chasser | cacciare | caçar | **kasar** | `an` | 2 | 10 | σ=2, support=10 | transparente |
| ceniza | ceniza | cinza | cendre | cenere | cendra | **sner** | `pms` | 1 | 1 | σ=1, support=1 (empate con wa) | adivinable |
| cerca | cerca | perto | près | vicino | prop | **pre** | `fr` | 1 | 6 | σ=1, support=6 | adivinable |
| chupar | chupar | chupar | sucer | succhiare | xuclar | **sug** | `rup` | 1 | 2 | σ=1, support=2 | opaco |
| cielo | cielo | céu | ciel | cielo | cel | **syel** | `fr` | 1 | 5 | σ=1, support=5 | transparente |
| cinco | cinco | cinco | cinq | cinque | cinc | **sink** | `fr` | 1 | 4 | σ=1, support=4 | transparente |
| cola | cola | rabo | queue | coda | cua | **kwa** | `ca` | 1 | 4 | σ=1, support=4 | adivinable |
| comer | comer | comer | manger | mangiare | menjar | **mek** | `rup` | 1 | 1 | σ=1, support=1 (empate con ruo) | adivinable |
| con | con | com | avec | con | amb | **kon** | `an` | 1 | 10 | σ=1, support=10 | transparente |
| congelar | congelar | congelar | geler | gelare | gelar | **gler** | `nrf` | 1 | 2 | única legal a σ=1 | opaco |
| contar | contar | contar | compter | contare | comptar | **kontar** | `an` | 2 | 10 | σ=2, support=10 | transparente |
| corazón | corazón | coração | cœur | cuore | cor | **kor** | `ca` | 1 | 7 | σ=1, support=7 | opaco |
| correcto | correcto | correto | correct | corretto | correcte | **yust** | `fur` | 1 | 2 | σ=1, support=2 (empate con glw,nrf) | opaco |
| cortar | cortar | cortar | couper | tagliare | tallar | **talx** | `ruo` | 1 | 2 | única legal a σ=1 | opaco |
| corteza | corteza | casca | écorce | corteccia | escorça | **skwaz** | `wa` | 1 | 1 | única legal a σ=1 | opaco |
| corto | corto | curto | court | corto | curt | **kurt** | `ca` | 1 | 10 | σ=1, support=10 | transparente |
| coser | coser | costurar | coudre | cucire | cosir | **kos** | `rup` | 1 | 2 | σ=1, support=2 | adivinable |
| cuatro | cuatro | quatro | quatre | quattro | quatre | **kat** | `glw` | 1 | 3 | σ=1, support=3 | adivinable |
| cuello | cuello | pescoço | cou | collo | coll | **kol** | `eml` | 1 | 6 | σ=1, support=6 | opaco |
| cuerda | cuerda | corda | corde | corda | corda | **kord** | `fr` | 1 | 4 | σ=1, support=4 | transparente |
| cuerno | cuerno | chifre | corne | corno | banya | **korn** | `fr` | 1 | 11 | σ=1, support=11 | adivinable |
| cuándo | cuándo | quando | quand | quando | quan | **kand** | `dlm` | 1 | 6 | σ=1, support=6 | transparente |
| cómo | cómo | como | comment | come | com | **kum** | `nrf` | 1 | 5 | σ=1, support=5 | adivinable |
| dar | dar | dar | donner | dare | donar | **dar** | `an` | 1 | 11 | σ=1, support=11 | transparente |
| decir | decir | dizer | dire | dire | dir | **dir** | `ca` | 1 | 10 | σ=1, support=10 | adivinable |
| delgado | delgado | fino | mince | sottile | prim | **fin** | `dlm` | 1 | 6 | σ=1, support=6 | transparente |
| derecha | derecha | direita | droite | destra | dreta | **dret** | `dlm` | 1 | 3 | σ=1, support=3 | adivinable |
| diente | diente | dente | dent | dente | dent | **dent** | `ca` | 1 | 5 | σ=1, support=5 | transparente |
| dormir | dormir | dormir | dormir | dormire | dormir | **dorm** | `ruq` | 1 | 1 | única legal a σ=1 | adivinable |
| dos | dos | dois | deux | due | dos | **dwi** | `scn` | 1 | 4 | σ=1 pero support 4 < 7 | adivinable |
| día | día | dia | jour | giorno | dia | **dya** | `an` | 1 | 8 | σ=1, support=8 | transparente |
| dónde | dónde | onde | où | dove | on | **an** | `an` | 1 | 1 | σ=1 pero support 1 < 2 | adivinable |
| el | el | o | le | il | el | **el** | `ast` | 1 | 9 | σ=1, support=9 | transparente |
| ellos | ellos | eles | ils | loro | ells | **lor** | `eml` | 1 | 4 | σ=1, support=4 | adivinable |
| empujar | empujar | empurrar | pousser | spingere | empènyer | **sping** | `lmo` | 1 | 1 | única legal a σ=1 | opaco |
| en | en | em | dans | in | en | **en** | `an` | 1 | 12 | σ=1, support=12 (empate con co,dlm,eml,fur) | transparente |
| entrañas | entrañas | tripas | entrailles | viscere | budells | **tripas** | `an` | 2 | 6 | σ=2, support=6 | transparente |
| escupir | escupir | cuspir | cracher | sputare | escopir | **spwe** | `pms` | 1 | 1 | σ=1, support=1 (empate con dlm,rup,ruq) | opaco |
| eso | eso | isso | cela | quello | aquell | **kwel** | `ist` | 1 | 5 | σ=1, support=5 | opaco |
| espalda | espalda | costas | dos | schiena | esquena | **do** | `fr` | 1 | 6 | σ=1, support=6 | opaco |
| esposa | esposa | esposa | épouse | moglie | muller | **na** | `lld` | 1 | 1 | σ=1, support=1 (empate con fur,lmo,rgn) | opaco |
| esposo | esposo | marido | mari | marito | marit | **om** | `lld` | 1 | 2 | σ=1, support=2 | opaco |
| esto | esto | isto | ceci | questo | aquest | **xu** | `nrf` | 1 | 2 | σ=1, support=2 (empate con eml,fur,ist,lmo) | adivinable |
| estrecho | estrecho | estreito | étroit | stretto | estret | **stret** | `eml` | 1 | 2 | σ=1, support=2 (empate con dlm,fur,ruo,ruq) | adivinable |
| estrella | estrella | estrela | étoile | stella | estrella | **stla** | `lld` | 1 | 1 | σ=1, support=1 (empate con wa) | opaco |
| flor | flor | flor | fleur | fiore | flor | **flor** | `an` | 1 | 17 | σ=1, support=17 | transparente |
| flotar | flotar | flutuar | flotter | galleggiare | flotar | **flotar** | `an` | 2 | 8 | σ=2, support=8 | transparente |
| fluir | fluir | fluir | couler | fluire | fluir | **xor** | `lmo` | 1 | 1 | σ=1, support=1 (empate con ruq) | opaco |
| frotar | frotar | esfregar | frotter | strofinare | fregar | **frek** | `rup` | 1 | 2 | única legal a σ=1 | opaco |
| fruta | fruta | fruta | fruit | frutto | fruita | **frut** | `fur` | 1 | 6 | σ=1, support=6 | transparente |
| frío | frío | frio | froid | freddo | fred | **fre** | `frp` | 1 | 3 | σ=1, support=3 (empate con ca,eml,lmo) | adivinable |
| fuego | fuego | fogo | feu | fuoco | foc | **fo** | `fr` | 1 | 5 | σ=1, support=5 (empate con ca,ro,ruo,rup) | adivinable |
| gata | gata | gata | chatte | gatta | gata | **xat** | `fr` | 1 | 2 | σ=1, support=2 (empate con nrf,pcd) | adivinable |
| gato | gato | gato | chat | gatto | gat | **gat** | `ca` | 1 | 5 | σ=1, support=5 | transparente |
| girar | girar | girar | tourner | girare | girar | **turn** | `ruo` | 1 | 1 | única legal a σ=1 | opaco |
| golpear | golpear | bater | frapper | colpire | pegar | **bat** | `lmo` | 1 | 1 | única legal a σ=1 | adivinable |
| grande | grande | grande | grand | grande | gran | **grand** | `eml` | 1 | 5 | σ=1, support=5 | transparente |
| grasa | grasa | gordura | graisse | grasso | greix | **gras** | `eml` | 1 | 6 | σ=1, support=6 | transparente |
| grueso | grueso | grosso | épais | spesso | gruixut | **gros** | `dlm` | 1 | 9 | σ=1, support=9 | adivinable |
| gusano | gusano | verme | ver | verme | cuc | **ver** | `fr` | 1 | 4 | σ=1, support=4 (empate con eml,frp,lmo,pms) | adivinable |
| hielo | hielo | gelo | glace | ghiaccio | gel | **glaz** | `fr` | 1 | 4 | σ=1, support=4 | opaco |
| hierba | hierba | erva | herbe | erba | herba | **erb** | `fr` | 1 | 4 | σ=1, support=4 | adivinable |
| hinchar | hinchar | inchar | enfler | gonfiare | inflar | **gonfler** | `glw` | 2 | 4 | σ=2, support=4 | opaco |
| hoja | hoja | folha | feuille | foglia | fulla | **fya** | `lld` | 1 | 2 | σ=1, support=2 (empate con glw,pcd) | adivinable |
| hombre | hombre | homem | homme | uomo | home | **om** | `eml` | 1 | 10 | σ=1, support=10 | adivinable |
| hueso | hueso | osso | os | osso | os | **os** | `ca` | 1 | 10 | σ=1, support=10 | adivinable |
| huevo | huevo | ovo | œuf | uovo | ou | **o** | `glw` | 1 | 3 | σ=1, support=3 (empate con eml,rm,ruo) | adivinable |
| humo | humo | fumo | fumée | fumo | fum | **fum** | `ca` | 1 | 10 | σ=1, support=10 | transparente |
| hígado | hígado | fígado | foie | fegato | fetge | **fwa** | `fr` | 1 | 3 | σ=1, support=3 | opaco |
| izquierda | izquierda | esquerda | gauche | sinistra | esquerra | **gox** | `fr` | 1 | 5 | σ=1, support=5 | opaco |
| jugar | jugar | jogar | jouer | giocare | jugar | **xur** | `fr` | 1 | 3 | σ=1, support=3 | adivinable |
| lago | lago | lago | lac | lago | llac | **lak** | `dlm` | 1 | 14 | σ=1, support=14 | adivinable |
| lanzar | lanzar | atirar | jeter | lanciare | llançar | **lyar** | `ca` | 1 | 1 | σ=1, support=1 (empate con lmo,ruq) | adivinable |
| largo | largo | longo | long | lungo | llarg | **long** | `eml` | 1 | 10 | σ=1, support=10 | transparente |
| lavar | lavar | lavar | laver | lavare | rentar | **la** | `gsc` | 1 | 2 | σ=1, support=2 (empate con rup,ruq) | adivinable |
| lejos | lejos | longe | loin | lontano | lluny | **lon** | `pcd` | 1 | 2 | σ=1, support=2 | adivinable |
| lengua | lengua | língua | langue | lingua | llengua | **lang** | `fr` | 1 | 4 | σ=1, support=4 | adivinable |
| liso | liso | liso | lisse | liscio | llis | **lis** | `dlm` | 1 | 12 | σ=1, support=12 | transparente |
| lleno | lleno | cheio | plein | pieno | ple | **plen** | `an` | 1 | 8 | σ=1, support=8 | adivinable |
| lluvia | lluvia | chuva | pluie | pioggia | pluja | **plo** | `glw` | 1 | 1 | σ=1, support=1 (empate con frp,nrf,wa) | opaco |
| luna | luna | lua | lune | luna | lluna | **lun** | `fr` | 1 | 5 | σ=1, support=5 | transparente |
| madre | madre | mãe | mère | madre | mare | **mer** | `fr` | 1 | 4 | σ=1, support=4 | adivinable |
| malo | malo | mau | mauvais | cattivo | dolent | **maw** | `pt` | 1 | 1 | σ=1, support=1 (empate con dlm,fur,pms,rm) | transparente |
| mano | mano | mão | main | mano | mà | **man** | `an` | 1 | 13 | σ=1, support=13 | transparente |
| mar | mar | mar | mer | mare | mar | **mar** | `an` | 1 | 16 | σ=1, support=16 | transparente |
| matar | matar | matar | tuer | uccidere | matar | **tur** | `fr` | 1 | 4 | σ=1, support=4 | adivinable |
| mojado | mojado | molhado | mouillé | bagnato | mullat | **ud** | `ro` | 1 | 3 | σ=1, support=3 | opaco |
| montaña | montaña | montanha | montagne | montagna | muntanya | **mont** | `fur` | 1 | 2 | única legal a σ=1 | adivinable |
| morder | morder | morder | mordre | mordere | mossegar | **mord** | `lld` | 1 | 1 | única legal a σ=1 | adivinable |
| morir | morir | morrer | mourir | morire | morir | **mor** | `rup` | 1 | 2 | σ=1, support=2 | adivinable |
| muchos | muchos | muitos | beaucoup | molti | molts | **tant** | `eml` | 1 | 2 | σ=1, support=2 | opaco |
| mujer | mujer | mulher | femme | donna | dona | **na** | `lld` | 1 | 1 | única legal a σ=1 | opaco |
| nadar | nadar | nadar | nager | nuotare | nedar | **na** | `lij` | 1 | 1 | σ=1, support=1 (empate con eml,pms) | adivinable |
| nariz | nariz | nariz | nez | naso | nas | **nas** | `ca` | 1 | 11 | σ=1, support=11 | adivinable |
| negro | negro | preto | noir | nero | negre | **ner** | `frp` | 1 | 2 | σ=1, support=2 (empate con pcd,wa) | adivinable |
| niebla | niebla | nevoeiro | brouillard | nebbia | boira | **brum** | `frp` | 1 | 1 | σ=1, support=1 (empate con wa) | opaco |
| nieve | nieve | neve | neige | neve | neu | **ne** | `frp` | 1 | 3 | σ=1, support=3 (empate con eml,lmo,rgn) | adivinable |
| niño | niño | criança | enfant | bambino | nen | **fyo** | `ist` | 1 | 1 | σ=1, support=1 (empate con ca,fur,lld,lmo) | adivinable |
| no | no | não | non | non | no | **no** | `an` | 1 | 8 | σ=1, support=8 | transparente |
| noche | noche | noite | nuit | notte | nit | **not** | `eml` | 1 | 3 | σ=1, support=3 | adivinable |
| nombre | nombre | nome | nom | nome | nom | **nom** | `ca` | 1 | 6 | σ=1, support=6 (empate con fr,frp,fur,glw) | transparente |
| nosotros | nosotros | nós | nous | noi | nosaltres | **no** | `frp` | 1 | 3 | σ=1, support=3 (empate con mwl,pt,ruo) | transparente |
| nube | nube | nuvem | nuage | nuvola | núvol | **nor** | `ro` | 1 | 4 | σ=1, support=4 (empate con fr,glw,nrf,pcd) | adivinable |
| nuevo | nuevo | novo | nouveau | nuovo | nou | **nov** | `eml` | 1 | 4 | σ=1, support=4 | transparente |
| ojo | ojo | olho | œil | occhio | ull | **wely** | `frp` | 1 | 3 | σ=1, support=3 | adivinable |
| oler | oler | cheirar | sentir | odorare | ensumar | **senti** | `gsc` | 2 | 4 | σ=2, support=4 (empate con eml,ist,rm,vec) | opaco |
| oreja | oreja | orelha | oreille | orecchio | orella | **or** | `wa` | 1 | 1 | única legal a σ=1 | adivinable |
| otro | otro | outro | autre | altro | altre | **ot** | `nrf` | 1 | 3 | σ=1, support=3 | adivinable |
| oír | oír | ouvir | entendre | sentire | sentir | **ud** | `ruq` | 1 | 1 | única legal a σ=1 | opaco |
| padre | padre | pai | père | padre | pare | **per** | `fr` | 1 | 4 | σ=1, support=4 (empate con gl,gsc,mwl,pt) | adivinable |
| palo | palo | pau | bâton | bastone | pal | **paw** | `mwl` | 1 | 3 | σ=1, support=3 | transparente |
| parar | parar | ficar | tenir | stare | estar | **star** | `vec` | 1 | 5 | σ=1, support=5 | adivinable |
| partir | partir | fender | fendre | spaccare | fendre | **ne** | `gsc` | 1 | 1 | σ=1, support=1 (empate con wa) | opaco |
| pecho | pecho | peito | sein | petto | pit | **pet** | `dlm` | 1 | 6 | σ=1, support=6 | adivinable |
| pelear | pelear | lutar | combattre | combattere | lluitar | **bat** | `pcd` | 1 | 2 | única legal a σ=1 | opaco |
| pelo | pelo | cabelo | cheveu | capello | cabell | **per** | `ro` | 1 | 4 | σ=1, support=4 | adivinable |
| pensar | pensar | pensar | penser | pensare | pensar | **pensar** | `an` | 2 | 12 | σ=2, support=12 | transparente |
| pequeño | pequeño | pequeno | petit | piccolo | petit | **mik** | `ro` | 1 | 3 | σ=1, support=3 | opaco |
| perra | perra | cadela | chienne | cagna | gossa | **xyen** | `fr` | 1 | 4 | única legal a σ=1 | opaco |
| perro | perro | cão | chien | cane | gos | **kan** | `an` | 1 | 10 | σ=1, support=10 | transparente |
| persona | persona | pessoa | personne | persona | persona | **om** | `dlm` | 1 | 2 | σ=1, support=2 | opaco |
| pesado | pesado | pesado | lourd | pesante | pesat | **lur** | `fr` | 1 | 4 | σ=1, support=4 | opaco |
| pez | pez | peixe | poisson | pesce | peix | **pes** | `ast` | 1 | 6 | σ=1, support=6 | transparente |
| pie | pie | pé | pied | piede | peu | **pe** | `eml` | 1 | 12 | σ=1, support=12 (empate con an,ast,es,ext) | transparente |
| piedra | piedra | pedra | pierre | pietra | pedra | **pyerr** | `fr` | 1 | 4 | σ=1, support=4 | adivinable |
| piel | piel | pele | peau | pelle | pell | **pel** | `eml` | 1 | 7 | σ=1, support=7 (empate con an,ast,es,ext) | transparente |
| pierna | pierna | perna | jambe | gamba | cama | **pyor** | `ruo` | 1 | 1 | única legal a σ=1 | adivinable |
| piojo | piojo | piolho | pou | pidocchio | poll | **pu** | `fr` | 1 | 5 | σ=1, support=5 | opaco |
| pluma | pluma | pena | plume | piuma | ploma | **plum** | `fr` | 1 | 3 | σ=1, support=3 | transparente |
| pocos | pocos | poucos | peu | pochi | pocs | **po** | `fr` | 1 | 3 | σ=1, support=3 (empate con dlm,eml,frp,glw) | adivinable |
| podrido | podrido | podre | pourri | marcio | podrit | **mers** | `eml` | 1 | 1 | σ=1, support=1 (empate con lld,lmo) | opaco |
| polvo | polvo | pó | poussière | polvere | pols | **praf** | `ro` | 1 | 3 | σ=1, support=3 | adivinable |
| porque | porque | porque | parce | perché | perquè | **ka** | `sc` | 1 | 2 | σ=1, support=2 (empate con fr,glw) | opaco |
| pájaro | pájaro | pássaro | oiseau | uccello | ocell | **ul** | `rgn` | 1 | 1 | σ=1 pero support 1 < 2 | opaco |
| quemar | quemar | queimar | brûler | bruciare | cremar | **ard** | `rup` | 1 | 1 | única legal a σ=1 | opaco |
| quién | quién | quem | qui | chi | qui | **ki** | `ca` | 1 | 16 | σ=1, support=16 | adivinable |
| qué | qué | que | quoi | che | què | **ke** | `an` | 1 | 12 | σ=1, support=12 | transparente |
| rascar | rascar | coçar | gratter | grattare | gratar | **gratar** | `ca` | 2 | 6 | σ=2, support=6 (empate con eml,fr,glw,nrf) | adivinable |
| raíz | raíz | raiz | racine | radice | arrel | **red** | `eml` | 1 | 1 | única legal a σ=1 | adivinable |
| recto | recto | direito | droit | dritto | recte | **drit** | `dlm` | 1 | 4 | σ=1, support=4 (empate con eml,fur,gsc,rgn) | opaco |
| redondo | redondo | redondo | rond | rotondo | rodó | **ron** | `fr` | 1 | 6 | σ=1, support=6 | opaco |
| respirar | respirar | respirar | respirer | respirare | respirar | **spirar** | `dlm` | 2 | 1 | σ=2, support=1 (empate con wa) | adivinable |
| reír | reír | rir | rire | ridere | riure | **rir** | `fr` | 1 | 9 | σ=1, support=9 | transparente |
| rodilla | rodilla | joelho | genou | ginocchio | genoll | **zno** | `eml` | 1 | 1 | única legal a σ=1 | opaco |
| rojo | rojo | vermelho | rouge | rosso | roig | **ros** | `dlm` | 1 | 5 | σ=1, support=5 | adivinable |
| romo | romo | cego | émoussé | smussato | rom | **ems** | `gsc` | 1 | 2 | σ=1, support=2 (empate con lld,rm) | adivinable |
| río | río | rio | rivière | fiume | riu | **ryo** | `an` | 1 | 5 | σ=1, support=5 | transparente |
| saber | saber | saber | savoir | sapere | saber | **xti** | `ro` | 1 | 1 | σ=1 pero support 1 < 2 | opaco |
| sal | sal | sal | sel | sale | sal | **sal** | `an` | 1 | 18 | σ=1, support=18 | transparente |
| sangre | sangre | sangue | sang | sangue | sang | **sang** | `fr` | 1 | 6 | σ=1, support=6 | transparente |
| secar | secar | enxugar | essuyer | asciugare | eixugar | **sterg** | `rup` | 1 | 2 | σ=1, support=2 | opaco |
| seco | seco | seco | sec | secco | sec | **sek** | `ca` | 1 | 15 | única legal a σ=1 | transparente |
| semilla | semilla | semente | graine | seme | llavor | **gren** | `fr` | 1 | 5 | σ=1, support=5 | opaco |
| sentar | sentar | sentar | asseoir | sedere | seure | **ed** | `ruo` | 1 | 1 | σ=1, support=1 (empate con eml,gsc,rup,ruq) | opaco |
| ser | ser | ser | être | essere | ser | **ser** | `lad` | 1 | 8 | σ=1, support=8 | transparente |
| serpiente | serpiente | serpente | serpent | serpente | serp | **serp** | `ca` | 1 | 5 | σ=1, support=5 | opaco |
| si | si | se | si | se | si | **se** | `dlm` | 1 | 16 | σ=1, support=16 | transparente |
| sol | sol | sol | soleil | sole | sol | **sol** | `ext` | 1 | 12 | σ=1, support=12 | transparente |
| sonreír | sonreír | sorrir | sourire | sorridere | somriure | **surir** | `fr` | 2 | 5 | σ=2, support=5 | transparente |
| soplar | soplar | soprar | souffler | soffiare | bufar | **sfya** | `lmo` | 1 | 1 | única legal a σ=1 | opaco |
| sucio | sucio | sujo | sale | sporco | brut | **spork** | `eml` | 1 | 5 | σ=1, support=5 | opaco |
| temer | temer | temer | craindre | temere | témer | **krend** | `wa` | 1 | 1 | única legal a σ=1 | opaco |
| tener | tener | ter | tenir | tenere | tenir | **ter** | `gl` | 1 | 2 | única legal a σ=1 | transparente |
| tierra | tierra | terra | terre | terra | terra | **ter** | `pcd` | 1 | 4 | σ=1, support=4 (empate con fr,glw) | transparente |
| tirar | tirar | puxar | tirer | tirare | estirar | **tya** | `lij` | 1 | 1 | σ=1 pero support 1 < 2 | adivinable |
| todo | todo | todo | tout | tutto | tot | **tot** | `an` | 1 | 7 | σ=1, support=7 | adivinable |
| tres | tres | três | trois | tre | tres | **tres** | `an` | 1 | 10 | σ=1, support=10 | transparente |
| tú | tú | tu | tu | tu | tu | **tu** | `an` | 1 | 21 | σ=1, support=21 | transparente |
| uno | uno | um | un | uno | un | **un** | `an` | 1 | 17 | σ=1, support=17 | transparente |
| uña | uña | unha | ongle | unghia | ungla | **ong** | `wa` | 1 | 1 | única legal a σ=1 | adivinable |
| venir | venir | vir | venir | venire | venir | **vir** | `gl` | 1 | 2 | σ=1, support=2 (empate con lld,lmo) | transparente |
| ver | ver | ver | voir | vedere | veure | **ver** | `es` | 1 | 6 | σ=1, support=6 | transparente |
| verde | verde | verde | vert | verde | verd | **verd** | `ca` | 1 | 8 | σ=1, support=8 | transparente |
| viejo | viejo | velho | vieux | vecchio | vell | **vyo** | `fr` | 1 | 2 | σ=1, support=2 (empate con gsc,oc) | adivinable |
| viento | viento | vento | vent | vento | vent | **vent** | `ca` | 1 | 6 | σ=1, support=6 (empate con fr,frp,glw,nrf) | transparente |
| vientre | vientre | ventre | ventre | pancia | ventre | **vent** | `pcd` | 1 | 2 | única legal a σ=1 | adivinable |
| vivir | vivir | viver | vivre | vivere | viure | **vi** | `lld` | 1 | 1 | σ=1, support=1 (empate con lmo) | adivinable |
| volar | volar | voar | voler | volare | volar | **zbor** | `rup` | 1 | 1 | única legal a σ=1 | opaco |
| vomitar | vomitar | vomitar | vomir | vomitare | vomitar | **vom** | `ruq` | 1 | 1 | única legal a σ=1 | opaco |
| vosotros | vosotros | vocês | vous | voi | vosaltres | **vo** | `frp` | 1 | 3 | σ=1, support=3 | adivinable |
| y | y | e | et | e | i | **e** | `co` | 1 | 22 | σ=1, support=22 | transparente |
| yacer | yacer | jazer | gésir | giacere | jeure | **zak** | `rup` | 1 | 1 | σ=1, support=1 (empate con ruq) | opaco |
| yo | yo | eu | je | io | jo | **yo** | `an` | 1 | 7 | σ=1, support=7 | transparente |
| árbol | árbol | árvore | arbre | albero | arbre | **ab** | `glw` | 1 | 2 | única legal a σ=1 | adivinable |
| él | él | ele | il | lui | ell | **el** | `an` | 1 | 10 | σ=1, support=10 | transparente |

## Apéndice: SA ≠ set-cover

Ninguna. SA coincidió con el set-cover en todos los conceptos.

## Caveats

- La glosa del scorecard es española; el `id` inglés del gold list no es fuente.
- El inglés no es lengua fuente. El latín está reservado y no entra en el knapsack.
- Epitran usa la lect hermana cuando no hay mapa propio (Oil←fr, retorromance y dálmata←it, asturiano←es, oriental←ro): `água`→`aga`, `olho`→`olo`, `ojo`/`rojo`→`okso`/`rokso`. `chat`→`xa` es la ortografía de `ʃ`.
- Las desinencias se enumeran por tiempo verbal (tema nominal o/u/e; cada fila de 6 personas es un lect). El recocido solo mueve raíces dentro del corte de σ mínima.
