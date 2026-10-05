# Grid columns re-sourced, 5 October 2026

Six columns were checked cell by cell against the lect's English Wiktionary Swadesh list and its
glossed Wiktionary entries (`scripts/audit_grid_sources.py`; current state in
[`eval/grid_sources.md`](eval/grid_sources.md)). This file records what changed.

A cell was kept if the list has its form for that concept or a Wiktionary entry glosses the form with
the concept. Otherwise it took the list's form. Istriot and Dalmatian held invented forms (Istriot
*dormar, vivar, vedar*; Dalmatian *flotar, fluir, gelar*), so there a cell with no source was emptied.
In the other four, a cell the list does not cover was left alone.

| Lect | Source list | Revision | Kept | Respelled | Replaced | Emptied |
|---|---|---|---:|---:|---:|---:|
| Istriot (`ist`) | Module:Swadesh/data/ist | 92115115 | 40 | 8 | 73 | 92 |
| Dalmatian (`dlm`) | Appendix:Dalmatian Swadesh list | 85554048 | 90 | 0 | 99 | 24 |
| Piedmontese (`pms`) | Module:Swadesh/data/pms | 62358233 | 151 | 7 | 55 | 0 |
| Ligurian (`lij`) | Module:Swadesh/data/lij | 62358247 | 89 | 54 | 70 | 0 |
| Emilian (`eml`) | Module:Swadesh/data/egl | 91988132 | 63 | 42 | 106 | 2 |
| Ladin (`lld`) | Module:Swadesh/data/lld | 90957698 | 204 | 4 | 5 | 0 |

Not changed: Gallo, Picard, Franco-Provençal and Extremaduran. None has a usable Swadesh list
(Wiktionary's Gallo list is filled with Walloon words), and their dictionaries on disk are in another
spelling or too small for a miss to mean anything. The audit confirms 30, 13, 20 and 87 of their 213
cells; the rest are unconfirmed, not known to be wrong.

One Gallo cell was plainly wrong and is fixed: *dog* held *chat*, the cat word. It is now *chien*,
which the French Wiktionary's Gallo entry glosses "Chien".

## Istriot

| concept | was | now | |
|---|---|---|---|
| i | mi | i | replaced |
| he | lu | lù | respelled |
| you_pl | vu | vui | replaced |
| they | li | luri | replaced |
| this | sto | stu | replaced |
| that | quel | quil | replaced |
| here | qua | lai | replaced |
| who | chi | – | emptied |
| what | cossa | – | emptied |
| where | ndove | – | emptied |
| when | quando | – | emptied |
| how | come | – | emptied |
| not | no | nu | replaced |
| all | tuto | doûto | replaced |
| many | tanti | – | emptied |
| some | alcuni | alquanto | replaced |
| few | pochi | puoco | replaced |
| one | un | oûn | replaced |
| three | trì | tri | respelled |
| five | zinque | sinque | replaced |
| thick | grosso | – | emptied |
| heavy | pezante | – | emptied |
| small | picolo | peîcio | replaced |
| short | corto | baso | replaced |
| narrow | stretto | strento | replaced |
| thin | fino | – | emptied |
| person | persona | – | emptied |
| child | fio | peîcio | replaced |
| wife | mujere | muier | replaced |
| husband | mario | mareî | replaced |
| fish | pese | piso | replaced |
| bird | osel | uzai | replaced |
| louse | pedocio | gèndana | replaced |
| snake | bisato | bìsa | replaced |
| worm | verme | vièrmo | replaced |
| forest | bosco | – | emptied |
| stick | baston | bastón | respelled |
| fruit | fruto | – | emptied |
| seed | seme | – | emptied |
| leaf | foja | – | emptied |
| root | raixa | – | emptied |
| bark | scorza | – | emptied |
| flower | fior | fiùr | replaced |
| grass | erba | gièrba | replaced |
| rope | corda | curda | replaced |
| skin | pele | – | emptied |
| meat | carne | carno | replaced |
| blood | sangue | – | emptied |
| bone | osso | uosso | replaced |
| fat | graso | – | emptied |
| egg | ovo | ùo | replaced |
| horn | corno | cuorno | replaced |
| tail | coa | – | emptied |
| feather | pena | – | emptied |
| hair | cavei | – | emptied |
| ear | orecia | – | emptied |
| nose | naso | – | emptied |
| mouth | boca | bóca | respelled |
| tooth | dente | – | emptied |
| tongue | lengua | lèngua | respelled |
| fingernail | ongia | – | emptied |
| foot | pie | – | emptied |
| leg | gamba | ganba | replaced |
| knee | zenocio | zanucio | replaced |
| belly | panza | – | emptied |
| guts | buele | budèi | replaced |
| neck | colo | còlo | respelled |
| back | schena | – | emptied |
| breast | peto | – | emptied |
| heart | cuor | core | replaced |
| liver | fegato | – | emptied |
| drink | beve | bévi | replaced |
| eat | magnar | magnà | replaced |
| bite | mordar | mursagà | replaced |
| suck | suciar | – | emptied |
| spit | sputar | – | emptied |
| vomit | vomitar | – | emptied |
| blow | bufar | – | emptied |
| breathe | respirar | – | emptied |
| laugh | rider | – | emptied |
| see | vedar | vidi | replaced |
| hear | sentar | uldì | replaced |
| know | saver | savì | replaced |
| think | pensar | pansà | replaced |
| smell | sentir | – | emptied |
| fear | temar | – | emptied |
| sleep | dormar | – | emptied |
| live | vivar | – | emptied |
| die | morar | – | emptied |
| kill | masar | – | emptied |
| fight | combater | – | emptied |
| hunt | cazar | – | emptied |
| hit | bater | bati | replaced |
| cut | tajar | talgià | replaced |
| split | spacar | talgià | replaced |
| stab | pontar | – | emptied |
| scratch | gratar | – | emptied |
| dig | cavar | badilà | replaced |
| swim | nadar | – | emptied |
| fly | volar | – | emptied |
| walk | caminar | – | emptied |
| come | vegnir | vignì | replaced |
| lie | giacer | – | emptied |
| sit | setar | – | emptied |
| stand | star | – | emptied |
| turn | girar | vultà | replaced |
| fall | cadar | cascà | replaced |
| give | dar | dà | replaced |
| hold | tegner | – | emptied |
| squeeze | strenzar | – | emptied |
| rub | fregar | – | emptied |
| wash | lavar | – | emptied |
| wipe | sugar | – | emptied |
| pull | tirar | – | emptied |
| push | spenzar | – | emptied |
| throw | butar | butà | replaced |
| tie | ligar | – | emptied |
| sew | cusar | – | emptied |
| count | contar | – | emptied |
| say | dir | deî | replaced |
| sing | cantar | – | emptied |
| play | zugar | – | emptied |
| float | galegiar | – | emptied |
| flow | scorar | – | emptied |
| freeze | gelar | – | emptied |
| swell | gonfiar | – | emptied |
| moon | luna | – | emptied |
| star | stela | stila | replaced |
| river | fiume | fioûme | replaced |
| lake | lago | – | emptied |
| sea | mar | mare | replaced |
| sand | sabia | – | emptied |
| dust | polvare | – | emptied |
| earth | tera | tiera | replaced |
| cloud | nuvola | nenbo | replaced |
| fog | nebia | – | emptied |
| sky | sielo | sil | replaced |
| snow | neve | bringiera | replaced |
| ice | giazzo | giasso | replaced |
| smoke | fumo | foûmo | replaced |
| fire | fogo | fògo | respelled |
| ash | senare | buistro | replaced |
| burn | brusar | ardi | replaced |
| road | strada | veîa | replaced |
| mountain | montagna | monto | replaced |
| green | verde | virdo | replaced |
| warm | caldo | – | emptied |
| cold | fredo | frido | replaced |
| full | pien | – | emptied |
| new | novo | nùvo | replaced |
| old | vecio | viecio | replaced |
| bad | cativo | – | emptied |
| rotten | marso | – | emptied |
| dirty | sporco | – | emptied |
| straight | drito | – | emptied |
| round | tondo | tunduleîno | replaced |
| sharp | pontuo | – | emptied |
| dull | otuso | – | emptied |
| smooth | liso | – | emptied |
| wet | bagna | bagnà | respelled |
| dry | seco | arso | replaced |
| correct | giusto | – | emptied |
| near | visin | atacà | replaced |
| far | lontan | – | emptied |
| right | drita | – | emptied |
| left | sanca | – | emptied |
| with | co | cun | replaced |
| because | parché | asoché | replaced |
| copula | esser | – | emptied |
| cat | gato | – | emptied |
| cat_f | gata | – | emptied |
| dog_f | cagna | – | emptied |
| smile | sorider | – | emptied |

## Dalmatian

| concept | was | now | |
|---|---|---|---|
| this | cest | cost | replaced |
| here | kai | kauk | replaced |
| there | la | luk | replaced |
| where | do | jo | replaced |
| how | ko | kal | replaced |
| some | nek | certioin | replaced |
| few | pok | – | emptied |
| other | ater | jultro | replaced |
| big | veira | maur | replaced |
| wide | larg | luarg | replaced |
| thick | gros | dais | replaced |
| heavy | pesant | pesunt | replaced |
| small | muc | pedlo | replaced |
| short | curt | kort | replaced |
| narrow | strent | – | emptied |
| thin | fin | – | emptied |
| person | om | jomno | replaced |
| child | feto | kratoir | replaced |
| wife | muier | mulier | replaced |
| husband | marit | marait | replaced |
| mother | mama | njena | replaced |
| father | tata | tuota | replaced |
| animal | animal | biastia | replaced |
| louse | pedoc | pedoklo | replaced |
| snake | saip | – | emptied |
| forest | bosk | buask | replaced |
| stick | bak | stal | replaced |
| fruit | fruta | froit | replaced |
| seed | samen | grun | replaced |
| rope | fune | kanapial | replaced |
| fat | gruass | gruas | replaced |
| feather | pena | – | emptied |
| fingernail | ongla | jongla | replaced |
| leg | gamba | guonb | replaced |
| knee | zenucl | denaklo | replaced |
| wing | ala | jal | replaced |
| guts | budel | alaite | replaced |
| back | dri | duas | replaced |
| breast | pet | tat | replaced |
| drink | beivre | bar | replaced |
| eat | mangur | mancur | replaced |
| bite | muarder | moscuar | replaced |
| suck | sucer | zupigur | replaced |
| spit | spuar | spoit | replaced |
| vomit | vomitar | gomituor | replaced |
| blow | bufar | sublar | replaced |
| breathe | spirar | fiutar | replaced |
| laugh | ridur | redro | replaced |
| see | veder | vedar | replaced |
| hear | sentir | senter | replaced |
| know | savir | sapar | replaced |
| think | pensar | piansar | replaced |
| smell | odur | tufuor | replaced |
| fear | temer | taimo | replaced |
| sleep | samno | dormer | replaced |
| die | murir | morer | replaced |
| kill | ucider | masuor | replaced |
| fight | punar | cuombatter | replaced |
| hunt | cazar | capur | replaced |
| hit | bater | botur | replaced |
| cut | taiar | taljur | replaced |
| split | fender | spartar | replaced |
| stab | puinal | – | emptied |
| scratch | gratar | gratuar | replaced |
| dig | cavar | pasnur | replaced |
| swim | nadar | – | emptied |
| fly | volar | svolur | replaced |
| walk | kaminar | kaminur | replaced |
| come | venur | venir | replaced |
| lie | jacer | – | emptied |
| sit | seder | sentur | replaced |
| stand | star | stur | replaced |
| turn | virar | – | emptied |
| fall | kader | kadar | replaced |
| give | dar | duor | replaced |
| hold | tener | tenar | replaced |
| squeeze | smechar | shtrengar | replaced |
| rub | fregar | jongar | replaced |
| wash | lavar | lavuar | replaced |
| wipe | sukar | – | emptied |
| pull | tirar | strasinur | replaced |
| push | spinger | – | emptied |
| throw | jitar | truar | replaced |
| tie | ligar | liguar | replaced |
| sew | kusir | koser | replaced |
| count | kuntar | embruar | replaced |
| say | dikar | dekro | replaced |
| sing | kantar | kantur | replaced |
| play | jugar | jukur | replaced |
| float | flotar | – | emptied |
| flow | fluir | – | emptied |
| freeze | gelar | glazir | replaced |
| swell | gonfiar | – | emptied |
| salt | sal | suol | replaced |
| dust | pulvar | pulvro | replaced |
| cloud | nuba | neo | replaced |
| fog | nebla | – | emptied |
| smoke | fum | – | emptied |
| ash | cenisa | kanaisa | replaced |
| burn | ardur | ardar | replaced |
| road | via | kale | replaced |
| mountain | mont | muant | replaced |
| warm | kald | cuald | replaced |
| good | bin | bun | replaced |
| rotten | putrid | muas | replaced |
| dirty | sordid | spuarc | replaced |
| straight | drit | drat | replaced |
| round | rotund | – | emptied |
| sharp | akut | – | emptied |
| dull | otuz | – | emptied |
| smooth | lis | – | emptied |
| wet | moliat | joit | replaced |
| dry | sek | sak | replaced |
| correct | korekt | drat | replaced |
| near | vesin | alic | replaced |
| far | lontan | distuont | replaced |
| right | dret | diastro | replaced |
| left | sanc | zuonca | replaced |
| because | perke | perko | replaced |
| copula | sar | – | emptied |
| cat_f | giata | – | emptied |
| dog_f | kuana | – | emptied |
| smile | somiar | – | emptied |

## Piedmontese

| concept | was | now | |
|---|---|---|---|
| this | sòn | cost | replaced |
| where | andova | andoa | replaced |
| how | coma | com | replaced |
| many | tanti | tant | replaced |
| some | cheich | chèich | respelled |
| thick | gross | tëgg | replaced |
| heavy | pesant | grev | replaced |
| husband | marì | òm | replaced |
| louse | pijòss | poj | replaced |
| snake | sërpi | sërpent | replaced |
| fruit | frut | fruta | replaced |
| seed | smen | smens | replaced |
| flower | flor | fior | replaced |
| rope | còrda | corda | respelled |
| feather | pluma | piuma | replaced |
| head | cap | testa | replaced |
| ear | orija | aurija | replaced |
| foot | pé | pe | respelled |
| knee | genoj | gënoj | respelled |
| guts | budej | boele | replaced |
| suck | sucé | ciucé | replaced |
| spit | spué | spuvé | replaced |
| blow | sfilé | bufé | replaced |
| breathe | respiré | arspiré | replaced |
| smell | sente | snufié | replaced |
| fear | teme | tëmme | replaced |
| sleep | dormì | deurme | replaced |
| kill | massé | massè | respelled |
| fight | combat | combate | replaced |
| hunt | cacé | cassé | replaced |
| split | spaché | spartì | replaced |
| stab | pugnale | stileté | replaced |
| scratch | grate | sgrafigné | replaced |
| dig | cavé | sgavé | replaced |
| swim | né | noé | replaced |
| lie | giacé | cogesse | replaced |
| fall | tomé | tombè | replaced |
| squeeze | sëranché | spërme | replaced |
| rub | freghé | fërté | replaced |
| wipe | seché | suvé | replaced |
| push | spinghe | possé | replaced |
| throw | campé | frandé | replaced |
| tie | lioré | gropé | replaced |
| float | galegé | floté | replaced |
| flow | scórre | score | replaced |
| freeze | gelé | geilé | replaced |
| swell | gonfié | anfié | replaced |
| stone | per | pera | replaced |
| earth | tèra | mond | replaced |
| fog | nebia | nëbbia | replaced |
| smoke | fùm | fum | respelled |
| road | strada | stra | replaced |
| red | rùss | ross | replaced |
| day | di | dì | respelled |
| rotten | marse | marsent | replaced |
| dirty | spòrch | anflà | replaced |
| round | tondo | riond | replaced |
| sharp | pontù | avuss | replaced |
| dull | òtus | sirognà | replaced |
| smooth | lis | seuli | replaced |
| near | visin | aranda | replaced |
| left | snistra | gàucia | replaced |

## Ligurian

| concept | was | now | |
|---|---|---|---|
| he | lé | lê | respelled |
| we | niatri | niâtri | respelled |
| you_pl | viatri | viâtri | respelled |
| that | quello | quéllo | respelled |
| there | là | la | respelled |
| where | donde | dôve | replaced |
| when | quando | quànde | replaced |
| how | comme | cómme | respelled |
| all | tutto | tùtto | respelled |
| many | tanti | tànto | replaced |
| some | arguni | quàrche | replaced |
| few | pöchi | pöco | replaced |
| other | atro | âtro | respelled |
| two | doi | doî | respelled |
| three | trei | tréi | respelled |
| four | quattro | quàttro | respelled |
| five | çinque | çìnque | respelled |
| big | grende | grànde | replaced |
| long | longo | lóngo | respelled |
| wide | largo | làrgo | respelled |
| thick | gròsso | drûo | replaced |
| heavy | pesante | pezànte | replaced |
| small | piccin | piccìn | respelled |
| short | curto | cùrto | respelled |
| narrow | stretto | stréito | replaced |
| thin | fin | sotî | replaced |
| child | figgeu | figeu | replaced |
| wife | moggê | mogê | replaced |
| husband | marìo | marîo | respelled |
| louse | piòggio | pighéuggio | replaced |
| snake | serpente | serpénte | respelled |
| worm | vèrme | verme | respelled |
| forest | bòsco | bosco | respelled |
| stick | baston | bacco | replaced |
| fruit | frûto | frûta | replaced |
| seed | semente | armella | replaced |
| leaf | fögia | féuggia | replaced |
| root | ræxe | réixe | replaced |
| bark | scòrza | scorsa | replaced |
| grass | èrba | erba | respelled |
| rope | còrda | corda | respelled |
| skin | pélle | pelle | respelled |
| bone | òsso | osso | respelled |
| fat | gràsso | grascia | replaced |
| horn | còrno | corno | respelled |
| tail | cóa | côa | respelled |
| feather | pìnn-a | penna | replaced |
| hair | cavéllo | cavello | respelled |
| head | tésta | testa | respelled |
| ear | éuggio | oêgia | replaced |
| mouth | bòcca | bocca | respelled |
| tooth | dénte | dente | respelled |
| fingernail | óngia | ongia | respelled |
| leg | gàmba | ganba | replaced |
| knee | zenòggio | zenoggio | respelled |
| hand | màn | man | respelled |
| belly | pànsa | pansa | respelled |
| guts | böélle | intestin | replaced |
| neck | còllo | collo | respelled |
| breast | pétto | pêto | replaced |
| liver | fêgato | figæto | replaced |
| bite | mòrde | adentâ | replaced |
| suck | sücciâ | susâ | replaced |
| spit | spütâ | spuâ | replaced |
| blow | sciùsciâ | sciusciâ | respelled |
| breathe | respirâ | respiâ | replaced |
| see | vedde | védde | respelled |
| smell | sentî | ödoâ | replaced |
| live | vivve | vîve | replaced |
| kill | amassâ | amasâ | replaced |
| fight | combatte | conbatte | replaced |
| hit | bàtte | batte | respelled |
| cut | taggiâ | tagiâ | replaced |
| split | spaccâ | dividde | replaced |
| stab | pugnâ | cotelâ | replaced |
| scratch | grattâ | gratâ | replaced |
| dig | cavâ | scavâ | replaced |
| swim | nâ | nuâ | replaced |
| fly | volâ | xoâ | replaced |
| lie | giacê | destendise | replaced |
| sit | setâse | asetâse | replaced |
| turn | gîâ | gjâ | replaced |
| fall | caze | càzze | replaced |
| hold | tègne | tegnî | replaced |
| squeeze | strenze | spremme | replaced |
| rub | fregâ | fretâ | replaced |
| wipe | asciugâ | sciugâ | replaced |
| pull | tîâ | tiâ | respelled |
| push | spinge | spinze | replaced |
| throw | lançiâ | tiâ | replaced |
| play | giugâ | zugâ | replaced |
| float | galegiâ | galezâ | replaced |
| freeze | geâ | zeâ | replaced |
| moon | lunn-a | lùnn-a | respelled |
| rain | ciêuve | ægoa | replaced |
| stone | préia | prîa | replaced |
| sand | sàbia | ænn-a | replaced |
| dust | póive | pûa | replaced |
| fog | nébbia | nêgia | replaced |
| wind | vénto | vento | respelled |
| ice | giàccio | giassa | replaced |
| smoke | fùmme | fumme | respelled |
| fire | feugo | fêugo | respelled |
| ash | çénn-e | çeine | replaced |
| burn | brûxâ | brüxâ | respelled |
| road | stràdda | stradda | respelled |
| mountain | montàgna | montagna | respelled |
| red | róusso | rosso | replaced |
| green | vérde | verde | respelled |
| white | giànco | gianco | respelled |
| day | giórno | giorno | respelled |
| year | ànno | anno | respelled |
| full | pien | pìn | replaced |
| good | bón | bon | respelled |
| bad | câttivo | catîvo | replaced |
| rotten | marcio | marso | replaced |
| dirty | spòrco | sücido | replaced |
| straight | drito | drîto | respelled |
| round | tónndo | rióndo | replaced |
| sharp | pontûo | afilòu | replaced |
| dull | òtûso | smusòu | replaced |
| left | mànca | mancìnn-a | replaced |
| copula | ëse | êse | respelled |
| dog_f | càgna | cagna | respelled |

## Emilian

| concept | was | now | |
|---|---|---|---|
| i | me | mé | respelled |
| you_sg | te | té | respelled |
| he | lò | ló | respelled |
| they | lór | lôr | respelled |
| here | chè | qué | replaced |
| what | còsa | côsa | respelled |
| where | indû | dóvv | replaced |
| not | mia | an | replaced |
| all | tòt | tótt | replaced |
| many | tânt | tant | respelled |
| some | alcùṅ | socuànt | replaced |
| few | pôch | pôc | replaced |
| two | dū | dû | respelled |
| three | trī | trî | respelled |
| four | quàter | quâter | respelled |
| big | grând | grand | respelled |
| wide | lârgh | lèrg | replaced |
| thick | gròs | féss | replaced |
| heavy | pezànt | paiṡ | replaced |
| small | picól | cén | replaced |
| narrow | strét | stratt | replaced |
| man | òm | òmen | replaced |
| person | persòuna | parsåṅna | replaced |
| child | putèn | cínno | replaced |
| wife | mùjer | mujêr | respelled |
| animal | animêl | animèl | respelled |
| fish | pès | pass | replaced |
| bird | uzèl | uṡèl | replaced |
| dog | càn | can | respelled |
| louse | piôć | bdòc' | replaced |
| snake | sêrp | sarpänt | replaced |
| worm | vêrm | lunbrîṡ | replaced |
| tree | êlber | élber | respelled |
| forest | bòsch | furèsta | replaced |
| stick | bastòn | bastån | replaced |
| fruit | frót | frûta | replaced |
| seed | smènz | smänt | replaced |
| leaf | fój | fójja | replaced |
| root | rèdṣ | radîṡ | replaced |
| bark | scòrza | scôrza | respelled |
| flower | fiôr | fiåur | replaced |
| rope | còrda | côrda | respelled |
| meat | chêrna | chèren | replaced |
| blood | sàngv | sangv | respelled |
| fat | gràs | grâs | respelled |
| egg | óv | ôv | respelled |
| horn | còren | côrna | replaced |
| tail | còa | cô | replaced |
| feather | pèna | panna | replaced |
| hair | cavì | cavî | respelled |
| head | co | cô | respelled |
| ear | urécia | uraccia | replaced |
| eye | òć | òc' | replaced |
| nose | nâs | nèṡ | replaced |
| mouth | bòca | båcca | replaced |
| tooth | dèint | dänt | replaced |
| tongue | lèngua | längua | replaced |
| fingernail | óngia | ónngia | replaced |
| foot | pè | pà | replaced |
| leg | gàmba | ganba | replaced |
| knee | znòć | źnòć | respelled |
| hand | màn | man | respelled |
| wing | êla | èglia | replaced |
| belly | pànsa | panza | replaced |
| guts | budèl | intestén | replaced |
| back | schéna | schéṅna | replaced |
| liver | fêghet | fégghet | replaced |
| drink | bèver | bàvver | replaced |
| bite | mòrder | muṡghèr | replaced |
| suck | sücièr | sucèr | replaced |
| blow | sufièr | supièr | replaced |
| laugh | rìder | rédder | replaced |
| see | vèder | vàdder | replaced |
| hear | sintìr | sénter | replaced |
| know | savèir | savair | replaced |
| smell | sentìr | naṡèr | replaced |
| fear | tmèr | – | emptied |
| sleep | durmìr | durmîr | respelled |
| live | vìver | vîver | respelled |
| die | murìr | murîr | respelled |
| fight | cumbàter | cunbâter | replaced |
| hunt | cacèr | cazièr | replaced |
| hit | bàter | bâter | respelled |
| split | spachèr | divîder | replaced |
| stab | pugnèl | pugnalèr | replaced |
| scratch | gratèr | ṡgranfgnèr | replaced |
| dig | cavèr | scavèr | replaced |
| swim | nèd | nudèr | replaced |
| come | gnìr | vgnîr | replaced |
| lie | giacèr | dstànndres | replaced |
| sit | stèr | sêder | replaced |
| stand | stèr | – | emptied |
| hold | tnìr | tgnîr | replaced |
| squeeze | strénzer | scuizèr | replaced |
| rub | freghèr | sfarghèr | replaced |
| wipe | süghèr | sughèr | respelled |
| push | spénzer | spénnżer | replaced |
| throw | butèr | trèr | replaced |
| tie | ligèr | lighèr | replaced |
| sew | cuṣìr | cûṡer | replaced |
| say | dìr | dîr | respelled |
| play | zughèr | żughèr | respelled |
| float | galegièr | galegèr | replaced |
| flow | scòrer | pasèr | replaced |
| freeze | gelèr | żlèr | replaced |
| sun | sōl | sól | respelled |
| moon | lòna | lóṅna | replaced |
| star | stèla | strèla | replaced |
| river | fiòm | fiómm | replaced |
| lake | lêgh | lèg | replaced |
| salt | sêl | sèl | respelled |
| stone | prêda | sâs | replaced |
| sand | sàbia | sâbia | respelled |
| cloud | nìvula | nóvvla | replaced |
| wind | vèint | vänt | replaced |
| snow | nêv | naiv | replaced |
| ice | giaz | giâz | respelled |
| fire | fôg | fûg | replaced |
| ash | sànder | zànnder | replaced |
| burn | bruṣèr | bruṡèr | respelled |
| road | strèda | strè | replaced |
| mountain | muntàgna | muntâgna | respelled |
| red | ròs | råss | replaced |
| green | vèrd | vaird | replaced |
| yellow | zôl | żâl | replaced |
| white | biànc | bianc | respelled |
| black | négher | naigher | replaced |
| year | àn | ân | respelled |
| cold | frèdd | fredd | respelled |
| full | pîn | pén | replaced |
| new | nóv | nôv | respelled |
| old | vêć | vèc' | replaced |
| good | bòṅ | bón | respelled |
| bad | cativ | catîv | respelled |
| rotten | mèrs | mèrz | replaced |
| dirty | spôrc | malnàtt | replaced |
| straight | drét | drétt | replaced |
| round | tónd | tånnd | replaced |
| sharp | puntûd | arfilè | replaced |
| dull | otûṣ | ṡmusè | replaced |
| smooth | lès | léss | replaced |
| wet | bagnê | mói | replaced |
| dry | sèc | sacc | replaced |
| correct | gióst | giósst | replaced |
| near | vṣèin | avṡén | replaced |
| right | dréta | drétta | replaced |
| left | sanca | stanca | replaced |
| with | cun | con | replaced |
| because | perché | parché | replaced |
| name | nòm | nómm | replaced |

## Ladin

| concept | was | now | |
|---|---|---|---|
| woman | ëna | femena | replaced |
| wife | ëna | femena | replaced |
| tongue | rujeneda | lënga | replaced |
| hear | udí | udir | replaced |
| know | savëi | savei | respelled |
| sleep | durmí | dormir | replaced |
| earth | tëra | tera | respelled |
| mountain | crëp | crep | respelled |
| green | vert | vërt | respelled |

## Second pass the same day: Saenko 2015 and the Extremaduran dictionary

`scripts/audit_grid_sources.py` now also reads Saenko's annotated Swadesh lists (110 concepts for 20 of
the grid's lects) and compares Extremaduran through the spelling differences between the grid and the
Carmona dictionary (*ombri*/*hombri*, *quatru*/*cuatru*, *yerva*/*yerba*). It reports on all 36 columns;
the counts are in [`eval/grid_sources.md`](eval/grid_sources.md).

- Istro-Romanian: 18 cells from Saenko (see `sources_ruo.md`).
- Dalmatian: *snake* serpiant and one more cell filled from Saenko. Most of his Dalmatian spellings
  are Bartoli's phonetic notation and are not used.
- Emilian: *fear* tmèr and *stand* stèr restored. They had been emptied because the list cites both
  only inside a phrase.
- Extremaduran: 129 of 213 cells confirmed against the dictionary, none changed.
- Ladin: 84 cells confirmed (Saenko's Gardenese and Fassano), none changed. The column is Val Badia
  and the lists are other valleys, so the 129 unconfirmed cells are not known to be wrong.

Two PDFs were fetched for Picard and Gallo and kept under `data/sources/pdf/`: a 33-page extract of
Dawson and Smirnova, *Dictionnaire fondamental français-picard* (Agence régionale de la langue
picarde, 2020), and *Motier Galo-Françaez* (Atelier de gallo, Héric, 2019), a local glossary with
IPA. 74 Picard and 83 Gallo grid forms occur somewhere in their text. That shows the words exist, not
that they carry the grid's meaning, so neither column is counted as confirmed by them.

## Third pass the same day: IE-CoR, Apertium, Stich 2001, the other Wiktionaries

Sources added to `scripts/audit_grid_sources.py`:

- **IE-CoR** (lexibank/iecor, CC-BY-4.0): 170 meanings with spelling and IPA for Franco-Provençal,
  Milanese, Ladin, Walloon, Friulian, two Sardinian varieties, Dalmatian, Megleno-Romanian, French,
  Portuguese, Italian, Spanish, Catalan and Romanian.
- **Apertium bilingual dictionaries** already under `vendor/`: Occitan–Spanish, where the Occitan
  dictionary marks which entries are Gascon; Spanish–Aragonese; Spanish–Asturian.
- **Stich 2001**, *Francoprovençal: proposition d'une orthographe supra-dialectale standardisée*
  (thesis, Paris V; PDF from arpitania.eu). It defines the ORB spelling the column uses, and holds a
  Swadesh list in ORB with English glosses (204 cells) and an ORB–French dictionary (15,689 forms).
- **Entries for these lects in other Wiktionaries**, from the local dumps: French (Gallo 11,422,
  Franco-Provençal 2,771, Picard 1,927, Mirandese 964, Norman 577), Portuguese (Mirandese 4,702),
  Spanish (Ladino 784, Extremaduran 467), Italian (Lombard 1,182). An earlier extraction missed
  every page whose first section was the lect.
- **Two dictionaries fetched as PDFs**: Ricaud, *Mon canepin de galo* (archive.org), a thematic
  Gallo–French lexicon; *Tiot diqchionnaire chti* (paroledechti.com, via the Wayback Machine).

What changed in the grid:

- **Franco-Provençal** follows Stich's list: 129 cells kept, 14 respelled, 59 replaced, 11 left
  unconfirmed. The old column had French calques (*lourd, cœur, vomir, tombar, brûlar, poussiére,
  gôche*) where ORB has *pesent, cor, dègolar, chêre, broular, puça, gôcho*.
- **Gascon** had no source at all; 136 of its cells are now confirmed.

What the audit now shows and did not change:

- **Picard, Mirandese and Gallo are padded from the big lect next door.** Of Picard's 195
  unconfirmed cells, 100 are letter for letter French; of Mirandese's 138, 90 are Portuguese; of
  Gallo's 174, 89 are French. The dictionaries have other words for those concepts (Mirandese *sangre,
  uosso, frol, pierna, lhabar* where the grid has *sangue, osso, flor, perna, labar*; Gallo *graund,
  saun, plum, coûe* where it has *grand, sang, plume, qeoue*). There is no Swadesh list for these
  three, only dictionaries, which offer several candidates per concept in more than one spelling. The
  candidates are listed per cell in [`eval/grid_sources.md`](eval/grid_sources.md) for picking by hand.
- Norman (42 of 116 unconfirmed cells are French) and Ladino (48 of 102 are Spanish) show the same
  signature more weakly; Ladino is close to Spanish anyway.
- Ladin, Lombard, Romansh, Walloon, Venetan and Friulian have many unconfirmed cells but almost none
  identical to the sister lect: there the gap is spelling or variety, not padding.

Also fetched and not used: *Dicionário de Mirandês-Português* (Ferreira and Ferreira, edition 0.1,
2004), of which the PDF holds only the letter M.

## Fourth pass: Picard, Mirandese and Gallo picked by hand

No Swadesh list exists for these three, so each column was rebuilt from one reference source, cell by
cell, and the audit now verifies every cell instead of changing any (mode *picked*). The per-cell
evidence is in [`eval/grid_sources.md`](eval/grid_sources.md).

Three tiers of evidence, strongest first:

1. **Glossed.** A dictionary headword glossed with the concept, or the title of the concept's article
   in the lect's Wikipedia (Wikidata sitelinks).
2. **Example.** The form stands in a sentence of the lect whose French translation has the concept's
   word.
3. **Corpus.** The form occurs in the lect's Wikipedia. The text shows the word exists in the lect; the
   meaning rests on the cognate. A form identical to the big sister lect's needs three tokens, a form
   of the lect's own needs one.

A cell with none of the three is empty.

| lect | reference | glossed | example | corpus | empty |
|---|---|---:|---:|---:|---:|
| Mirandese | Portuguese Wiktionary's Mirandese entries (4,702); Mirandese Wikipedia (3.4 million words) | 125 | 0 | 75 | 13 |
| Picard | Chés Diseux, "mes mots à mi": Amiens area, 3,900 entries with translated examples | 141 | 26 | 25 | 21 |
| Gallo | French Wiktionary's Gallo entries, ABCD spelling first; Ricaud, *Mon canepin de galo* | 119 | 38 | 0 | 56 |

**Mirandese.** 77 cells changed. The old column mixed Portuguese and Spanish guesses: *sangue, osso,
ovo, flor, perna, fuego, bueno, vientre, pescuezo, can* where Mirandese has *sangre, uosso, uobo,
frol, pierna, fuogo, buono, barriga, cachaço, perro*. The spelling is the 1999 convention throughout
(*lh-* for Latin *l-*, the diphthongs *ie* and *uo*, *b* for *v*). The Mirandese Wikipedia was partly
adapted from the Portuguese one and carries Portuguese spellings beside the Mirandese ones (*lago* 164
times, *lhago* 155), which is why a form identical to Portuguese needs three tokens. Emptied for want
of any attestation: *worm, bite, suck, smell, split, stab, scratch, lie, tie, sharp, dull, wet,
smile*.

**Picard.** The old column was already Amiens Picard (*troés, quoé, minger, vir, ichi*) with French
filled in around it. Chés Diseux is one speaker's vocabulary of that area, which makes the column one
variety in one spelling. He leaves out words spelled as in French, so those cells rest on his example
sentences or on the Picard Wikipedia (*long, pied, nez, tête, sang, rire, dire, jour*). One cell is
from the Nord and not from Amiens: *bone* oche (Tiot diqchionnaire). The word list writes a nasal
vowel before *n* with a dot (*grain.ne, tchien.ne, gan.ne*); the grid keeps his spelling.

**Gallo.** The thinnest of the three. The French Wiktionary's 11,400 Gallo entries name their spelling
system (ABCD 7,284, ELG 2,085, MOGA 328), but are dense only for words in A and B; Ricaud's thematic
lexicon covers the body, weather and everyday verbs in a spelling of his own. The column therefore
mixes two French-like spellings, and 56 cells are empty, among them words that are probably the same
as French (*sang, os, corde, lac*) but which no source at hand attests. ELG forms were passed over
where the French reader would misread them (*saun, plum, naijae*). Chubri's ChuMétiv database was
tried: it is a dialect inventory, and plain words appear in it only inside phrases.

Also found and not yet used: fr.wiktionary gives a pronunciation for many Gallo and Picard entries,
and the Motier of Héric gives IPA throughout.

