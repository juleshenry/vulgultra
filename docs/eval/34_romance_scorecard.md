# Lacyo Swadesh — 34 lects Romance

Lexicón de origen mixto: una forma Lacyo por concepto, elegida
entre candidatos meaning-aligned de **fr / es / it / pt / ca / ro / gl / oc / an / ast / ext / lad / mwl / scn / vec / lmo / pms / lij / fur / eml / lld / ist / wa / pcd / nrm / frp / glw / gsc / la / rm / sc / rup / ruo / dlm** (34 lects).
El inglés no es lengua fuente. Las columnas ES/PT son de inspección.

## Qué minimiza el SA

Una raíz no se elige “porque sí”. El recocido minimiza

$$
E = 1000\sum_r \sigma(r) + 10\sum_r (N_{\mathrm{src}}-\mathrm{support}(r)) + 200\sum_e \sigma(e)
+ 100000\cdot\mathrm{coll} + 500000\cdot\mathrm{viol} + 500\sum_{i<j}\max(0,2-d(e_i,e_j))
$$

| término | peso | qué hace en la práctica |
|---|---:|---|
| **σ raíces** | 1000 | una sílaba extra gana a todo lo de abajo |
| **support** | 10 | a igual σ, el stem que cubre más lects (`gat` × ca/oc/lmo… vs `xa` × fr) |
| σ desinencias | 200 | terminaciones cortas |
| colisiones | 100000 | duro: dos casillas del paradigma no pueden ser homófonas |
| fonotáctica | 500000 | duro: forma ilegal fuera (por eso PT crudo pierde aunque sea corto) |
| distancia desinencias | 500 | personas de un mismo tiempo no se parecen demasiado |
| inventario \|Φ\| | **0** | no se minimiza; `/v/` se queda |

Orden lexicográfico de una **raíz**: legal → menos σ → más support
→ menos fonemas → código de lengua. Por eso portugués puede salir 0%:
casi siempre hay una hermana legal igual de corta o más corta.
`N_src` = 34. Un stem con support 8 cuesta `10×(34-8)=260`; una σ extra cuesta 1000.

## Veredicto

Frente a **español** y **portugués** (las lenguas de inspección): el mixto tiene **244** sílabas de raíz vs ES 268 y PT 274, con **0** violaciones (ES 12, PT 10).

Frente a **francés crudo**: always-fr suma 277σ pero con **13 violaciones** (E_tact enorme). El mixto es -33σ más largo y legal. Italiano crudo es peor (303σ, 14 viol.).

Calidad del optimizador (raíces): SA **no recuperó el greedy**. legal-shortest = 244σ / E=2843470; SA = 244σ / E=2843710 (0σ extra, acuerdo 198/213). El init ya partía de raíces legal-shortest (244σ); 500k iteraciones dejaron la temperatura alta (accept ~90%) y algunas raíces se alargaron mientras se limpiaban colisiones. El shortest crudo (ignora fonotáctica) llega a 233σ con 11 violaciones y no es un baseline de energía.

## Procedencia (raíces SA)

| fuente | raíces | % |
|---|---:|---:|
| `fr` | 25 | 11.7% |
| `es` | 1 | 0.5% |
| `it` | 1 | 0.5% |
| `pt` | 0 | 0.0% |
| `ca` | 27 | 12.7% |
| `ro` | 2 | 0.9% |
| `gl` | 4 | 1.9% |
| `oc` | 2 | 0.9% |
| `an` | 27 | 12.7% |
| `ast` | 6 | 2.8% |
| `ext` | 0 | 0.0% |
| `lad` | 0 | 0.0% |
| `mwl` | 1 | 0.5% |
| `scn` | 0 | 0.0% |
| `vec` | 0 | 0.0% |
| `lmo` | 6 | 2.8% |
| `pms` | 2 | 0.9% |
| `lij` | 2 | 0.9% |
| `fur` | 7 | 3.3% |
| `eml` | 14 | 6.6% |
| `lld` | 5 | 2.3% |
| `ist` | 0 | 0.0% |
| `wa` | 9 | 4.2% |
| `pcd` | 5 | 2.3% |
| `nrm` | 3 | 1.4% |
| `frp` | 13 | 6.1% |
| `glw` | 7 | 3.3% |
| `gsc` | 4 | 1.9% |
| `la` | 2 | 0.9% |
| `rm` | 0 | 0.0% |
| `sc` | 3 | 1.4% |
| `rup` | 13 | 6.1% |
| `ruo` | 0 | 0.0% |
| `dlm` | 22 | 10.3% |
| **total** | 213 | 100% |

## Totales por política

Las terminaciones de SA se mantienen fijas en las políticas de raíz
(salvo `init`: raíces más cortas legales + terminaciones aleatorias, semilla 42).

| política | Σσ raíces | media σ | viol | \|Φ\| | E_root | E_norm | E_end | E_coll | E_tact | E_dist | E_total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sa | 244 | 1.15 | 0 | 23 | 244000 | 46410 | 12800 | 1000000 | 1500000 | 40500 | 2843710 |
| legal-shortest | 244 | 1.15 | 0 | 22 | 244000 | 46170 | 12800 | 1000000 | 1500000 | 40500 | 2843470 |
| shortest | 233 | 1.09 | 11 | 22 | 233000 | 47160 | 12800 | 1000000 | 7000000 | 40500 | 8333460 |
| always-es | 268 | 1.26 | 12 | 23 | 268000 | 47890 | 12800 | 1000000 | 7500000 | 40500 | 8869190 |
| always-pt | 274 | 1.29 | 10 | 22 | 274000 | 48990 | 12800 | 1000000 | 6500000 | 40500 | 7876290 |
| always-fr | 277 | 1.30 | 13 | 22 | 277000 | 49800 | 12800 | 1000000 | 8000000 | 40500 | 9380100 |
| always-it | 303 | 1.42 | 14 | 23 | 303000 | 48890 | 12800 | 1000000 | 8500000 | 40500 | 9905190 |
| always-ca | 285 | 1.34 | 15 | 22 | 285000 | 49770 | 12800 | 1000000 | 9000000 | 40500 | 10388070 |
| always-ro | 367 | 1.72 | 16 | 23 | 367000 | 54450 | 12800 | 1000000 | 9500000 | 40500 | 10974750 |
| always-gl | 285 | 1.34 | 5 | 22 | 285000 | 49570 | 12800 | 1000000 | 4000000 | 40500 | 5387870 |
| always-oc | 253 | 1.19 | 18 | 22 | 253000 | 48810 | 12800 | 1000000 | 10500000 | 40500 | 11855110 |
| init | 244 | 1.15 | 0 | 22 | 244000 | 46170 | 11800 | 3800000 | 1500000 | 68500 | 5670470 |

Energía inicial reportada por el CLI Rust: **4250970** (comparar con SA E_total = 2843710).

## Acuerdo

- Conceptos: **213**
- ES y PT adaptados idénticos: 0/213
- SA = ES (ortografía Lacyo): 1/213
- SA = PT: 0/213
- SA = FR: 25/213
- SA = IT: 1/213
- SA = shortest (crudo): 190/213
- SA = legal-shortest: 198/213
- SA ≠ legal-shortest: 15/213

## Frases de demostración

Con conjugación y concordancia. Artículo cerrado **o/a** (PT), no el/la.
Copula 3sg **e** (é). Verbo = tema (infinitivo menos `-r`) + desinencia.

### El gato rojo sonríe.

PT: O gato vermelho sorri.

```
Lacyo  o  gat  roxo  sure
src    [pt]  [ca]  [frp]  [fr]
es     el/la  gato  rojo  sonreír
pt     o  gato  vermelho  sorrir
σ      6
```

### El perro es grande.

PT: O cão é grande.

```
Lacyo  o  kan  e  grando
src    [pt]  [an]  [pt]  [eml]
es     el/la  perro  es  grande
pt     o  cão  é  grande
σ      5
```

### El agua es fría.

PT: A água é fria.

```
Lacyo  a  ya  e  freda
src    [pt]  [nrm]  [pt]  [ca]
es     el/la  agua  es  frío
pt     a  água  é  frio
σ      5
```

### Yo veo el sol.

PT: Eu vejo o sol.

```
Lacyo  xo  veo  o  sol
src    [ca]  [ast]  [pt]  [an]
es     yo  ver  el/la  sol
pt     eu  ver  o  sol
σ      5
```

### La mujer come pez.

PT: A mulher come peixe.

```
Lacyo  a  na  meke  pes
src    [pt]  [lld]  [rup]  [ast]
es     el/la  mujer  comer  pez
pt     a  mulher  comer  peixe
σ      5
```

### El fuego es rojo.

PT: O fogo é vermelho.

```
Lacyo  o  fok  e  roxo
src    [pt]  [ca]  [pt]  [frp]
es     el/la  fuego  es  rojo
pt     o  fogo  é  vermelho
σ      5
```

### Nosotros damos agua.

PT: Nós damos água.

```
Lacyo  no  damos  ya
src    [frp]  [an]  [nrm]
es     nosotros  dar  agua
pt     nós  dar  água
σ      4
```

### El hombre es bueno.

PT: O homem é bom.

```
Lacyo  o  om  e  bono
src    [pt]  [dlm]  [pt]  [dlm]
es     el/la  hombre  es  bueno
pt     o  homem  é  bom
σ      5
```

### La noche es negra.

PT: A noite é preta.

```
Lacyo  a  not  e  nera
src    [pt]  [eml]  [pt]  [frp]
es     el/la  noche  es  negro
pt     a  noite  é  preto
σ      5
```

### Tú oyes el viento.

PT: Tu ouves o vento.

```
Lacyo  tu  oas  o  vent
src    [an]  [an]  [pt]  [ca]
es     tú  oír  el/la  viento
pt     tu  ouvir  o  vento
σ      5
```

## Género (sustantivos pueden mezclar fuentes; verbos no)

Par masculino/femenino elegido por sílabas, independiente.
Ejemplo permitido: M `gat` [ca] + F `chatte` [fr].
Los verbos no se parten así: un lexema, una conjugación entera.

| glosa | M Lacyo | src | σ | F Lacyo | src | σ |
|---|---|---|---:|---|---|---:|
| gato | **gat** | `ca` | 1 | **xat** | `fr` | 1 |
| perro | **kan** | `an` | 1 | **kana** | `sc` | 2 |

## Tabla por concepto

| glosa | es | pt | fr | it | ca | Lacyo | src | σ | sup | por qué | bin |
|---|---|---|---|---|---|---|---|---:|---:|---|---|
| a | a | a | à | a | a | **a** | `an` | 1 | 34 | única legal a σ=1 | — |
| afilado | afilado | afiado | aigu | affilato | esmolat | **ag** | `frp` | 1 | 7 | única legal a σ=1 | opaco |
| agua | agua | água | eau | acqua | aigua | **ya** | `nrm` | 1 | 4 | σ=1, support=4 | — |
| ala | ala | asa | aile | ala | ala | **a** | `gl` | 1 | 7 | única legal a σ=1 | — |
| algunos | algunos | alguns | quelques | alcuni | alguns | **kek** | `glw` | 1 | 6 | σ=1, support=6 | opaco |
| allí | allí | ali | là | lì | allà | **li** | `it` | 1 | 20 | única legal a σ=1 | — |
| amarillo | amarillo | amarelo | jaune | giallo | groc | **xon** | `fr` | 1 | 5 | σ=1, support=5 | opaco |
| ancho | ancho | largo | large | largo | ample | **larg** | `dlm` | 1 | 22 | σ=1, support=22 | opaco |
| animal | animal | animal | animal | animale | animal | **byes** | `wa` | 1 | 1 | σ=1 pero support 1 < 4 | — |
| apretar | apretar | apertar | presser | spremere | prémer | **serer** | `pcd` | 2 | 3 | σ=2, support=3 (empate con ca) | — |
| apuñalar | apuñalar | esfaquear | poignarder | pugnalare | apunyalar | **punya** | `lij` | 2 | 1 | σ=2 pero support 1 < 2 | opaco |
| aquí | aquí | aqui | ici | qui | aquí | **ki** | `lij` | 1 | 17 | σ=1, support=17 | — |
| arena | arena | areia | sable | sabbia | sorra | **rena** | `sc` | 2 | 8 | σ=2, support=8 | — |
| atar | atar | atar | lier | legare | lligar | **leg** | `rup` | 1 | 4 | única legal a σ=1 | — |
| año | año | ano | année | anno | any | **any** | `ca` | 1 | 27 | única legal a σ=1 | — |
| beber | beber | beber | boire | bere | beure | **ber** | `frp` | 1 | 10 | σ=1, support=10 | — |
| blanco | blanco | branco | blanc | bianco | blanc | **blank** | `fr` | 1 | 20 | σ=1, support=20 | — |
| boca | boca | boca | bouche | bocca | boca | **bok** | `wa` | 1 | 18 | σ=1, support=18 | — |
| bosque | bosque | floresta | forêt | foresta | bosc | **box** | `fur` | 1 | 5 | σ=1, support=5 | opaco |
| bueno | bueno | bom | bon | buono | bo | **bon** | `dlm` | 1 | 24 | única legal a σ=1 | — |
| cabeza | cabeza | cabeça | tête | testa | cap | **kap** | `ca` | 1 | 8 | σ=1, support=8 | — |
| caer | caer | cair | tomber | cadere | caure | **kad** | `lmo` | 1 | 2 | única legal a σ=1 | — |
| caliente | caliente | quente | chaud | caldo | calent | **kald** | `dlm` | 1 | 15 | σ=1, support=15 | — |
| caminar | caminar | andar | marcher | camminare | caminar | **yi** | `lld` | 1 | 1 | σ=1, support=1 (empate con rm) | — |
| camino | camino | estrada | route | strada | camí | **vya** | `sc` | 1 | 4 | σ=1, support=4 (empate con fr) | opaco |
| cantar | cantar | cantar | chanter | cantare | cantar | **kantar** | `an` | 2 | 23 | única legal a σ=2 | — |
| carne | carne | carne | viande | carne | carn | **karn** | `ca` | 1 | 22 | σ=1, support=22 | — |
| cavar | cavar | cavar | creuser | scavare | cavar | **sap** | `rup` | 1 | 1 | única legal a σ=1 | — |
| cazar | cazar | caçar | chasser | cacciare | caçar | **kasa** | `gsc` | 2 | 15 | σ=2, support=15 | — |
| ceniza | ceniza | cinza | cendre | cenere | cendra | **send** | `wa` | 1 | 2 | única legal a σ=1 | — |
| cerca | cerca | perto | près | vicino | prop | **prep** | `oc` | 1 | 9 | única legal a σ=1 | adivinable |
| chupar | chupar | chupar | sucer | succhiare | xuclar | **sug** | `rup` | 1 | 1 | única legal a σ=1 | — |
| cielo | cielo | céu | ciel | cielo | cel | **sel** | `ca` | 1 | 14 | única legal a σ=1 | — |
| cinco | cinco | cinco | cinq | cinque | cinc | **sink** | `fr` | 1 | 19 | σ=1, support=19 | — |
| cola | cola | rabo | queue | coda | cua | **ko** | `fr` | 1 | 11 | σ=1, support=11 | — |
| comer | comer | comer | manger | mangiare | menjar | **mek** | `rup` | 1 | 1 | única legal a σ=1 | — |
| con | con | com | avec | con | amb | **kun** | `eml` | 1 | 22 | σ=1, support=22 | — |
| congelar | congelar | congelar | geler | gelare | gelar | **gler** | `nrm` | 1 | 2 | única legal a σ=1 | opaco |
| contar | contar | contar | compter | contare | comptar | **kontar** | `an` | 2 | 20 | σ=2, support=20 | — |
| corazón | corazón | coração | cœur | cuore | cor | **kor** | `ca` | 1 | 19 | σ=1, support=19 | opaco |
| correcto | correcto | correto | correct | corretto | correcte | **xus** | `pcd` | 1 | 4 | única legal a σ=1 | — |
| cortar | cortar | cortar | couper | tagliare | tallar | **kortar** | `ast` | 2 | 7 | σ=2 pero support 7 < 8 | — |
| corteza | corteza | casca | écorce | corteccia | escorça | **kaxka** | `mwl` | 2 | 2 | σ=2 pero support 2 < 9 | — |
| corto | corto | curto | court | corto | curt | **kurt** | `ca` | 1 | 25 | única legal a σ=1 | — |
| coser | coser | costurar | coudre | cucire | cosir | **kos** | `rup` | 1 | 2 | única legal a σ=1 | opaco |
| cuatro | cuatro | quatro | quatre | quattro | quatre | **kat** | `glw` | 1 | 5 | única legal a σ=1 | — |
| cuello | cuello | pescoço | cou | collo | coll | **kol** | `eml` | 1 | 15 | σ=1, support=15 | opaco |
| cuerda | cuerda | corda | corde | corda | corda | **kord** | `fr` | 1 | 20 | σ=1, support=20 | — |
| cuerno | cuerno | chifre | corne | corno | banya | **korn** | `dlm` | 1 | 23 | σ=1, support=23 | adivinable |
| cuándo | cuándo | quando | quand | quando | quan | **kand** | `dlm` | 1 | 15 | σ=1, support=15 | — |
| cómo | cómo | como | comment | come | com | **kom** | `ca` | 1 | 19 | única legal a σ=1 | — |
| dar | dar | dar | donner | dare | donar | **dar** | `an` | 1 | 24 | única legal a σ=1 | — |
| decir | decir | dizer | dire | dire | dir | **dir** | `ca` | 1 | 18 | σ=1, support=18 | adivinable |
| delgado | delgado | fino | mince | sottile | prim | **fin** | `dlm` | 1 | 20 | σ=1, support=20 | opaco |
| derecha | derecha | direita | droite | destra | dreta | **dret** | `dlm` | 1 | 10 | única legal a σ=1 | — |
| diente | diente | dente | dent | dente | dent | **dent** | `ca` | 1 | 24 | única legal a σ=1 | — |
| dormir | dormir | dormir | dormir | dormire | dormir | **dormir** | `an` | 2 | 27 | única legal a σ=2 | — |
| dos | dos | dois | deux | due | dos | **dos** | `an` | 1 | 25 | única legal a σ=1 | — |
| día | día | dia | jour | giorno | dia | **di** | `dlm` | 1 | 16 | σ=1, support=16 | — |
| dónde | dónde | onde | où | dove | on | **un** | `gsc` | 1 | 5 | σ=1, support=5 | — |
| el | el | o | le | il | el | **el** | `ast` | 1 | 18 | única legal a σ=1 | — |
| ellos | ellos | eles | ils | loro | ells | **els** | `an` | 1 | 8 | σ=1, support=8 (empate con lld) | — |
| empujar | empujar | empurrar | pousser | spingere | empènyer | **puser** | `fr` | 2 | 5 | σ=2, support=5 | — |
| en | en | em | dans | in | en | **en** | `an` | 1 | 28 | σ=1, support=28 | — |
| entrañas | entrañas | tripas | entrailles | viscere | budells | **tripas** | `an` | 2 | 9 | σ=2, support=9 | opaco |
| escupir | escupir | cuspir | cracher | sputare | escopir | **kraxer** | `fr` | 2 | 3 | σ=2, support=3 (empate con gl,glw) | — |
| eso | eso | isso | cela | quello | aquell | **kel** | `fur` | 1 | 10 | σ=1, support=10 | adivinable |
| espalda | espalda | costas | dos | schiena | esquena | **do** | `fr` | 1 | 7 | σ=1, support=7 | — |
| esposa | esposa | esposa | épouse | moglie | muller | **na** | `lld` | 1 | 1 | única legal a σ=1 | opaco |
| esposo | esposo | marido | mari | marito | marit | **mar** | `fur` | 1 | 9 | σ=1, support=9 | — |
| esto | esto | isto | ceci | questo | aquest | **ik** | `la` | 1 | 1 | σ=1 pero support 1 < 4 | — |
| estrecho | estrecho | estreito | étroit | stretto | estret | **estret** | `ca` | 2 | 5 | σ=2, support=5 | adivinable |
| estrella | estrella | estrela | étoile | stella | estrella | **etway** | `fr` | 2 | 3 | única legal a σ=2 | — |
| flor | flor | flor | fleur | fiore | flor | **flor** | `an` | 1 | 24 | σ=1, support=24 | — |
| flotar | flotar | flutuar | flotter | galleggiare | flotar | **flotar** | `an` | 2 | 14 | σ=2, support=14 | — |
| fluir | fluir | fluir | couler | fluire | fluir | **xor** | `lmo` | 1 | 4 | única legal a σ=1 | — |
| frotar | frotar | esfregar | frotter | strofinare | fregar | **frek** | `rup` | 1 | 3 | única legal a σ=1 | opaco |
| fruta | fruta | fruta | fruit | frutto | fruita | **frut** | `fur` | 1 | 26 | única legal a σ=1 | — |
| frío | frío | frio | froid | freddo | fred | **fred** | `ca` | 1 | 15 | única legal a σ=1 | — |
| fuego | fuego | fogo | feu | fuoco | foc | **fok** | `ca` | 1 | 15 | única legal a σ=1 | — |
| gata | gata | gata | chatte | gatta | gata | **xat** | `fr` | 1 | 5 | única legal a σ=1 | — |
| gato | gato | gato | chat | gatto | gat | **gat** | `ca` | 1 | 21 | σ=1, support=21 | — |
| girar | girar | girar | tourner | girare | girar | **virar** | `dlm` | 2 | 8 | σ=2, support=8 | — |
| golpear | golpear | bater | frapper | colpire | pegar | **bat** | `lmo` | 1 | 9 | única legal a σ=1 | — |
| grande | grande | grande | grand | grande | gran | **grand** | `eml` | 1 | 23 | única legal a σ=1 | — |
| grasa | grasa | gordura | graisse | grasso | greix | **gras** | `eml` | 1 | 23 | única legal a σ=1 | opaco |
| grueso | grueso | grosso | épais | spesso | gruixut | **gros** | `dlm` | 1 | 14 | única legal a σ=1 | — |
| gusano | gusano | verme | ver | verme | cuc | **verm** | `eml` | 1 | 17 | σ=1, support=17 | — |
| hielo | hielo | gelo | glace | ghiaccio | gel | **gla** | `fur` | 1 | 7 | σ=1, support=7 | — |
| hierba | hierba | erva | herbe | erba | herba | **erb** | `fr` | 1 | 20 | σ=1, support=20 | — |
| hinchar | hinchar | inchar | enfler | gonfiare | inflar | **gonflar** | `frp` | 2 | 8 | σ=2, support=8 | — |
| hoja | hoja | folha | feuille | foglia | fulla | **foy** | `eml` | 1 | 6 | σ=1, support=6 | opaco |
| hombre | hombre | homem | homme | uomo | home | **om** | `dlm` | 1 | 23 | σ=1, support=23 | — |
| hueso | hueso | osso | os | osso | os | **os** | `ca` | 1 | 23 | única legal a σ=1 | — |
| huevo | huevo | ovo | œuf | uovo | ou | **ov** | `eml` | 1 | 17 | σ=1, support=17 | — |
| humo | humo | fumo | fumée | fumo | fum | **fum** | `ca` | 1 | 28 | única legal a σ=1 | — |
| hígado | hígado | fígado | foie | fegato | fetge | **fwa** | `fr` | 1 | 5 | σ=1, support=5 | opaco |
| izquierda | izquierda | esquerda | gauche | sinistra | esquerra | **sank** | `dlm` | 1 | 4 | σ=1 pero support 4 < 5 | — |
| jugar | jugar | jogar | jouer | giocare | jugar | **xur** | `fr` | 1 | 3 | única legal a σ=1 | — |
| lago | lago | lago | lac | lago | llac | **lag** | `lmo` | 1 | 29 | única legal a σ=1 | — |
| lanzar | lanzar | atirar | jeter | lanciare | llançar | **tra** | `lmo` | 1 | 1 | única legal a σ=1 | adivinable |
| largo | largo | longo | long | lungo | llarg | **long** | `dlm` | 1 | 20 | única legal a σ=1 | — |
| lavar | lavar | lavar | laver | lavare | rentar | **lavar** | `an` | 2 | 25 | σ=2, support=25 | — |
| lejos | lejos | longe | loin | lontano | lluny | **lon** | `pcd` | 1 | 3 | única legal a σ=1 | opaco |
| lengua | lengua | língua | langue | lingua | llengua | **lang** | `fr` | 1 | 5 | σ=1, support=5 | — |
| liso | liso | liso | lisse | liscio | llis | **lis** | `dlm` | 1 | 22 | única legal a σ=1 | — |
| lleno | lleno | cheio | plein | pieno | ple | **plen** | `an` | 1 | 22 | única legal a σ=1 | — |
| lluvia | lluvia | chuva | pluie | pioggia | pluja | **plo** | `glw` | 1 | 4 | única legal a σ=1 | — |
| luna | luna | lua | lune | luna | lluna | **lun** | `fr` | 1 | 27 | única legal a σ=1 | — |
| madre | madre | mãe | mère | madre | mare | **mar** | `frp` | 1 | 14 | única legal a σ=1 | — |
| malo | malo | mau | mauvais | cattivo | dolent | **mal** | `dlm` | 1 | 12 | σ=1, support=12 | — |
| mano | mano | mão | main | mano | mà | **man** | `an` | 1 | 29 | única legal a σ=1 | — |
| mar | mar | mar | mer | mare | mar | **mar** | `an` | 1 | 32 | única legal a σ=1 | — |
| matar | matar | matar | tuer | uccidere | matar | **tur** | `fr` | 1 | 6 | σ=1, support=6 | — |
| mojado | mojado | molhado | mouillé | bagnato | mullat | **ud** | `ro` | 1 | 3 | única legal a σ=1 | opaco |
| montaña | montaña | montanha | montagne | montagna | muntanya | **mont** | `dlm` | 1 | 3 | única legal a σ=1 | — |
| morder | morder | morder | mordre | mordere | mossegar | **mord** | `lld` | 1 | 9 | única legal a σ=1 | — |
| morir | morir | morrer | mourir | morire | morir | **mor** | `rup` | 1 | 2 | única legal a σ=1 | — |
| muchos | muchos | muitos | beaucoup | molti | molts | **tant** | `eml` | 1 | 6 | σ=1, support=6 | opaco |
| mujer | mujer | mulher | femme | donna | dona | **na** | `lld` | 1 | 1 | única legal a σ=1 | opaco |
| nadar | nadar | nadar | nager | nuotare | nedar | **ne** | `pms` | 1 | 3 | única legal a σ=1 | — |
| nariz | nariz | nariz | nez | naso | nas | **na** | `frp` | 1 | 18 | única legal a σ=1 | — |
| negro | negro | preto | noir | nero | negre | **ner** | `frp` | 1 | 12 | única legal a σ=1 | — |
| niebla | niebla | nevoeiro | brouillard | nebbia | boira | **brum** | `frp` | 1 | 3 | σ=1, support=3 | opaco |
| nieve | nieve | neve | neige | neve | neu | **nev** | `eml` | 1 | 16 | única legal a σ=1 | — |
| niño | niño | criança | enfant | bambino | nen | **cit** | `pms` | 1 | 1 | σ=1 pero support 1 < 2 | opaco |
| no | no | não | non | non | no | **no** | `an` | 1 | 21 | σ=1, support=21 | — |
| noche | noche | noite | nuit | notte | nit | **not** | `eml` | 1 | 11 | σ=1, support=11 | adivinable |
| nombre | nombre | nome | nom | nome | nom | **nom** | `ca` | 1 | 21 | única legal a σ=1 | — |
| nosotros | nosotros | nós | nous | noi | nosaltres | **no** | `frp` | 1 | 18 | única legal a σ=1 | — |
| nube | nube | nuvem | nuage | nuvola | núvol | **nor** | `ro` | 1 | 3 | σ=1 pero support 3 < 4 | opaco |
| nuevo | nuevo | novo | nouveau | nuovo | nou | **nov** | `dlm` | 1 | 13 | única legal a σ=1 | — |
| ojo | ojo | olho | œil | occhio | ull | **uy** | `glw` | 1 | 4 | σ=1, support=4 | adivinable |
| oler | oler | cheirar | sentir | odorare | ensumar | **senti** | `gsc` | 2 | 12 | σ=2, support=12 | — |
| oreja | oreja | orelha | oreille | orecchio | orella | **or** | `wa` | 1 | 1 | única legal a σ=1 | opaco |
| otro | otro | outro | autre | altro | altre | **ot** | `nrm` | 1 | 5 | única legal a σ=1 | — |
| oír | oír | ouvir | entendre | sentire | sentir | **oir** | `an` | 2 | 8 | σ=2, support=8 (empate con ca) | — |
| padre | padre | pai | père | padre | pare | **par** | `frp` | 1 | 15 | σ=1, support=15 | — |
| palo | palo | pau | bâton | bastone | pal | **pal** | `ca` | 1 | 10 | σ=1, support=10 | — |
| parar | parar | ficar | tenir | stare | estar | **tar** | `ast` | 1 | 6 | única legal a σ=1 | adivinable |
| partir | partir | fender | fendre | spaccare | fendre | **fend** | `wa` | 1 | 1 | σ=1, support=1 (empate con gsc) | opaco |
| pecho | pecho | peito | sein | petto | pit | **pet** | `dlm` | 1 | 13 | σ=1, support=13 | — |
| pelear | pelear | lutar | combattre | combattere | lluitar | **bat** | `pcd` | 1 | 4 | única legal a σ=1 | opaco |
| pelo | pelo | cabelo | cheveu | capello | cabell | **pel** | `oc` | 1 | 9 | única legal a σ=1 | — |
| pensar | pensar | pensar | penser | pensare | pensar | **pensa** | `fur` | 2 | 20 | σ=2, support=20 | — |
| pequeño | pequeño | pequeno | petit | piccolo | petit | **muk** | `dlm` | 1 | 3 | σ=1, support=3 | — |
| perra | perra | cadela | chienne | cagna | gossa | **kana** | `sc` | 2 | 14 | σ=2, support=14 | — |
| perro | perro | cão | chien | cane | gos | **kan** | `an` | 1 | 19 | σ=1, support=19 | — |
| persona | persona | pessoa | personne | persona | persona | **om** | `dlm` | 1 | 3 | única legal a σ=1 | — |
| pesado | pesado | pesado | lourd | pesante | pesat | **lur** | `fr` | 1 | 4 | σ=1, support=4 (empate con rm) | — |
| pez | pez | peixe | poisson | pesce | peix | **pes** | `ast` | 1 | 11 | única legal a σ=1 | — |
| pie | pie | pé | pied | piede | peu | **pe** | `eml` | 1 | 28 | única legal a σ=1 | — |
| piedra | piedra | pedra | pierre | pietra | pedra | **pyerr** | `fr` | 1 | 5 | σ=1, support=5 | — |
| piel | piel | pele | peau | pelle | pell | **pel** | `eml` | 1 | 27 | única legal a σ=1 | — |
| pierna | pierna | perna | jambe | gamba | cama | **krus** | `la` | 1 | 1 | única legal a σ=1 | — |
| piojo | piojo | piolho | pou | pidocchio | poll | **po** | `wa` | 1 | 7 | σ=1, support=7 | — |
| pluma | pluma | pena | plume | piuma | ploma | **plum** | `fr` | 1 | 15 | σ=1, support=15 | — |
| pocos | pocos | poucos | peu | pochi | pocs | **pok** | `dlm` | 1 | 14 | σ=1, support=14 | — |
| podrido | podrido | podre | pourri | marcio | podrit | **mars** | `lld` | 1 | 6 | única legal a σ=1 | opaco |
| polvo | polvo | pó | poussière | polvere | pols | **pu** | `gl` | 1 | 4 | σ=1, support=4 | — |
| porque | porque | porque | parce | perché | perquè | **pars** | `fr` | 1 | 2 | σ=1, support=2 | — |
| pájaro | pájaro | pássaro | oiseau | uccello | ocell | **pulx** | `rup` | 1 | 1 | única legal a σ=1 | opaco |
| quemar | quemar | queimar | brûler | bruciare | cremar | **ard** | `rup` | 1 | 3 | única legal a σ=1 | — |
| quién | quién | quem | qui | chi | qui | **ki** | `ca` | 1 | 20 | única legal a σ=1 | — |
| qué | qué | que | quoi | che | què | **ke** | `an` | 1 | 23 | σ=1, support=23 | — |
| rascar | rascar | coçar | gratter | grattare | gratar | **gratar** | `ca` | 2 | 16 | σ=2, support=16 | opaco |
| raíz | raíz | raiz | racine | radice | arrel | **red** | `eml` | 1 | 1 | única legal a σ=1 | — |
| recto | recto | direito | droit | dritto | recte | **dret** | `eml` | 1 | 14 | única legal a σ=1 | adivinable |
| redondo | redondo | redondo | rond | rotondo | rodó | **ront** | `fur` | 1 | 8 | σ=1, support=8 | — |
| respirar | respirar | respirar | respirer | respirare | respirar | **sufler** | `wa` | 2 | 1 | única legal a σ=2 | — |
| reír | reír | rir | rire | ridere | riure | **rir** | `fr` | 1 | 18 | única legal a σ=1 | — |
| rodilla | rodilla | joelho | genou | ginocchio | genoll | **rodya** | `ast` | 2 | 3 | σ=2 pero support 3 < 4 | opaco |
| rojo | rojo | vermelho | rouge | rosso | roig | **rox** | `frp` | 1 | 11 | única legal a σ=1 | — |
| romo | romo | cego | émoussé | smussato | rom | **rom** | `ca` | 1 | 8 | σ=1, support=8 | opaco |
| río | río | rio | rivière | fiume | riu | **rib** | `ca` | 1 | 7 | σ=1, support=7 | — |
| saber | saber | saber | savoir | sapere | saber | **saver** | `frp` | 2 | 22 | σ=2, support=22 | — |
| sal | sal | sal | sel | sale | sal | **sal** | `an` | 1 | 27 | única legal a σ=1 | — |
| sangre | sangre | sangue | sang | sangue | sang | **sang** | `fr` | 1 | 16 | única legal a σ=1 | — |
| secar | secar | enxugar | essuyer | asciugare | eixugar | **sexer** | `glw` | 2 | 3 | σ=2 pero support 3 < 4 | — |
| seco | seco | seco | sec | secco | sec | **sek** | `ca` | 1 | 25 | única legal a σ=1 | — |
| semilla | semilla | semente | graine | seme | llavor | **gren** | `fr` | 1 | 6 | σ=1, support=6 | opaco |
| sentar | sentar | sentar | asseoir | sedere | seure | **sed** | `rup` | 1 | 1 | única legal a σ=1 | — |
| ser | ser | ser | être | essere | ser | **ser** | `an` | 1 | 14 | σ=1, support=14 | — |
| serpiente | serpiente | serpente | serpent | serpente | serp | **serp** | `ca` | 1 | 11 | única legal a σ=1 | — |
| si | si | se | si | se | si | **se** | `dlm` | 1 | 31 | σ=1, support=31 | — |
| sol | sol | sol | soleil | sole | sol | **sol** | `an` | 1 | 20 | única legal a σ=1 | — |
| sonreír | sonreír | sorrir | sourire | sorridere | somriure | **surir** | `fr` | 2 | 12 | σ=2, support=12 | — |
| soplar | soplar | soprar | souffler | soffiare | bufar | **soplar** | `es` | 2 | 8 | σ=2, support=8 | transparente |
| sucio | sucio | sujo | sale | sporco | brut | **brut** | `ca` | 1 | 1 | σ=1 pero support 1 < 5 | — |
| temer | temer | temer | craindre | temere | témer | **krend** | `wa` | 1 | 4 | única legal a σ=1 | — |
| tener | tener | ter | tenir | tenere | tenir | **ter** | `gl` | 1 | 2 | única legal a σ=1 | — |
| tierra | tierra | terra | terre | terra | terra | **terr** | `fr` | 1 | 21 | σ=1, support=21 | — |
| tirar | tirar | puxar | tirer | tirare | estirar | **trag** | `rup` | 1 | 1 | única legal a σ=1 | — |
| todo | todo | todo | tout | tutto | tot | **tut** | `gsc` | 1 | 21 | única legal a σ=1 | — |
| tres | tres | três | trois | tre | tres | **tre** | `frp` | 1 | 30 | única legal a σ=1 | — |
| tú | tú | tu | tu | tu | tu | **tu** | `an` | 1 | 32 | σ=1, support=32 | — |
| uno | uno | um | un | uno | un | **un** | `an` | 1 | 31 | única legal a σ=1 | — |
| uña | uña | unha | ongle | unghia | ungla | **ong** | `wa` | 1 | 5 | única legal a σ=1 | — |
| venir | venir | vir | venir | venire | venir | **vir** | `gl` | 1 | 3 | σ=1, support=3 | — |
| ver | ver | ver | voir | vedere | veure | **ver** | `ast` | 1 | 13 | σ=1, support=13 | — |
| verde | verde | verde | vert | verde | verd | **verd** | `ca` | 1 | 27 | única legal a σ=1 | — |
| viejo | viejo | velho | vieux | vecchio | vell | **vye** | `glw` | 1 | 8 | única legal a σ=1 | adivinable |
| viento | viento | vento | vent | vento | vent | **vent** | `ca` | 1 | 24 | única legal a σ=1 | — |
| vientre | vientre | ventre | ventre | pancia | ventre | **vent** | `pcd` | 1 | 2 | única legal a σ=1 | — |
| vivir | vivir | viver | vivre | vivere | viure | **viv** | `lmo` | 1 | 10 | única legal a σ=1 | — |
| volar | volar | voar | voler | volare | volar | **volar** | `an` | 2 | 21 | única legal a σ=2 | — |
| vomitar | vomitar | vomitar | vomir | vomitare | vomitar | **vomit** | `rup` | 2 | 13 | σ=2, support=13 | — |
| vosotros | vosotros | vocês | vous | voi | vosaltres | **vo** | `frp` | 1 | 16 | única legal a σ=1 | adivinable |
| y | y | e | et | e | i | **i** | `an` | 1 | 33 | única legal a σ=1 | — |
| yacer | yacer | jazer | gésir | giacere | jeure | **zak** | `rup` | 1 | 1 | única legal a σ=1 | — |
| yo | yo | eu | je | io | jo | **xo** | `ca` | 1 | 12 | única legal a σ=1 | — |
| árbol | árbol | árvore | arbre | albero | arbre | **ab** | `glw` | 1 | 3 | única legal a σ=1 | — |
| él | él | ele | il | lui | ell | **el** | `an` | 1 | 19 | σ=1, support=19 | — |

## Apéndice: SA ≠ legal-shortest

| glosa | SA | src | σ | legal-shortest | src | σ | razón |
|---|---|---|---:|---|---|---:|---|
| animal | byes | `wa` | 1 | bet | `glw` | 1 | misma σ, otra fuente |
| apuñalar | punya | `lij` | 2 | pontar | `ist` | 2 | misma σ, otra fuente |
| camino | vya | `sc` | 1 | rut | `fr` | 1 | misma σ, otra fuente |
| cortar | kortar | `ast` | 2 | taya | `lmo` | 2 | misma σ, otra fuente |
| corteza | kaxka | `mwl` | 2 | xorsa | `eml` | 2 | misma σ, otra fuente |
| ellos | els | `an` | 1 | i | `lld` | 1 | misma σ, otra fuente |
| escupir | kraxer | `fr` | 2 | kraxi | `glw` | 2 | misma σ, otra fuente |
| esto | ik | `la` | 1 | so | `glw` | 1 | misma σ, otra fuente |
| izquierda | sank | `dlm` | 1 | gox | `fr` | 1 | misma σ, otra fuente |
| niño | cit | `pms` | 1 | fi | `lmo` | 1 | misma σ, otra fuente |
| nube | nor | `ro` | 1 | nul | `fur` | 1 | misma σ, otra fuente |
| partir | fend | `wa` | 1 | ne | `gsc` | 1 | misma σ, otra fuente |
| rodilla | rodya | `ast` | 2 | xenu | `fr` | 2 | misma σ, otra fuente |
| secar | sexer | `glw` | 2 | sukar | `dlm` | 2 | misma σ, otra fuente |
| sucio | brut | `ca` | 1 | sal | `fr` | 1 | misma σ, otra fuente |

## Caveats

- La glosa del scorecard es española; el `id` inglés del gold list no es fuente.
- Epitran G2P es aproximado: `água`→`aga`, `olho`→`olo`, `ojo`/`rojo`→`okso`/`rokso` (`/x/`→`ks`), `où` se pierde (`ù` no mapea). `chat`→`xa` es la ortografía fonémica (`ʃ`=`x`).
- La especificación trata los diptongos como fonemas-unidad; el código cuenta cada vocal.
- Lacyo no tiene género: un solo artículo (`def_art`) para todas las frases.
- Las frases muestran raíces, no formas flexionadas.
- Rumano queda fuera de esta corrida (no hay G2P cableado).
- Cooling por defecto (`0.999997`, 500k iters) no enfría: el greedy de raíces es mejor que SA en este run. Un follow-up es 2M iters o mutar raíces con menos frecuencia que terminaciones.
