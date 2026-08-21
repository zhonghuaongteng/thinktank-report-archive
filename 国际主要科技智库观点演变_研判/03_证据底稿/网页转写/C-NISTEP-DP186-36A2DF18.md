# COVID-19 / SARS-CoV-2 関連のプレプリントを用いた研究動向の試行的分析

- 发布机构：National Institute of Science and Technology Policy
- 报告编号：DP:186
- 发布日期：2020-06-01
- 官方落地页：http://hdl.handle.net/11035/00006646
- 官方PDF：https://nistep.repo.nii.ac.jp/record/6696/files/NISTEP-DP186-FullJ.pdf
- 获取方式：NISTEP官方仓储PDF的Jina代理全文

Title: NISTEP-DP186-FullJ.pdf

URL Source: https://nistep.repo.nii.ac.jp/record/6696/files/NISTEP-DP186-FullJ.pdf

Published Time: Mon, 15 May 2023 13:45:21 GMT

Number of Pages: 16

Markdown Content:
## DISCUSSION PAPER No.186

# COVID-19 / SARS-CoV-2 関連の

# プレプリントを用いた研究動向の試行的分析

# A Trial of early detection system for research trends through the preprints data

# ─ Research status around COVID-19 / SARS-CoV-2

# 2020 年 6 月

# 文部科学省 科学技術・学術政策研究所 小柴 等，林 和弘，伊藤 裕子 本 DISCUSSION PAPER は、所内での討論に用いるとともに、関係の方々からの御意見を頂くこ とを目的に作成したものである。

また、本 DISCUSSION PAPER の内容は、執筆者の見解に基づいてまとめられたものであり、必 ずしも機関の公式の見解を示すものではないことに留意されたい。

The DISCUSSION PAPER series are published for discussion within the National Institute of Science and Technology Policy (NISTEP) as well as receiving comments from the community. It should be noticed that the opinions in this DISCUSSION PAPER are the sole responsibility of the author(s) and do not necessarily reflect the official views of NISTEP.

【執筆者】

小柴 等 第 2 調査研究グループ

林 和弘 科学技術予測センター 伊藤 裕子 科学技術予測センター

【Authors】 KOSHIBA Hitoshi 2nd Policy-Oriented Research Group, National Institute of Science and Technology Policy (NISTEP), MEXT HAYASHI Kazuhiro Science and Technology Foresight Center, National Institute of Science and Technology Policy (NISTEP), MEXT ITO Yuko Science and Technology Foresight Center, National Institute of Science and Technology Policy (NISTEP), MEXT

本報告書の引用を行う際には、以下を参考に出典を明記願います。 Please specify reference as the following example when citing this paper. 小柴 等，林 和弘，伊藤 裕子 「COVID-19 / SARS-CoV-2 関連のプレプリントを用いた研究 動向の試行的分析」， NISTEP DISCUSSION PAPER，No.186，文部科学省科学技術・学術政策 研究所．

> DOI: http://doi.org/10.15108/dp186

KOSHIBA Hitoshi, HAYASHI Kazuhiro, ITO Yuko, “A Trial of early detection system for research trends through the preprints data ─ Research status around COVID-19 / SARS-CoV-2,” NISTEP DISCUSSION PAPER, No.186, National Institute of Science and Technology Policy, Tokyo.

> DOI: http://doi.org/10.15108/dp186

## COVID-19 / SARS-CoV-2 関連のプレプリントを用いた研究動向の試行的分析

文部科学省 科学技術・学術政策研究所

小柴 等， 林 和弘， 伊藤 裕子 要旨 近年，査読前の論文草稿であるプレプリントをとりまとめて公開するプレプリントサーバの活用 が進んでいる。ジャーナル論文の投稿に先立つというプレプリントの性質上，ジャーナル論文を対 象とした研究動向分析と比較して早期に研究動向を把握できる可能性があり，そのため新興の （エマージングな）研究領域の補足に有用と考えられる。 こうした背景のもと，本報では COVID-19 関連のプレプリントを対象に，自然言語処理を用いた エマージング領域の把握を試行した。 その結果，既存の分析と同様に，疫学調査のステップに合致する動向を得ることができた。そ れに加えて，通常の査読論文も含めて分析した先行研究では明確には検出ができていなかった， 医薬・ワクチン開発に関するトピックを抽出することができた。 今回の試行により，プレプリントを利用したエマージング研究内容のメタ把握が実現できる可能 性が示唆された。

## A Trial of early detection system for research trends through the preprints data

## ─ Research status around COVID-19 / SARS-CoV-2

KOSHIBA Hitoshi, HAYASHI Kazuhiro, ITO Yuko National Institute of Science and Technology Policy (NISTEP), MEXT

ABSTRACT

In recent years, the use of preprint servers, which compile and publish preprints of pre-reviewed drafts of articles before peer review is in progress. Due to the nature of the preprint, which precedes the submission of a journal article, the research on journal articles in comparison with trend analysis, it is possible to understand research trends at an earlier stage, and therefore it can be used to supplement emerging research areas. It is thought to be useful. In this report, we attempted to understand the emerging regions of COVID-19 related preprints by using natural language processing. As a result, we were able to obtain the trend consistent with the epidemiological survey step as well as the existing analysis. In addition, we were able to detect the emergent regions, which had not been clearly detected in previous studies that also included ordinary peer-reviewed papers. In addition, we were able to extract topics related to drug and vaccine development. This trial demonstrated the possibility of realizing a meta-understanding of emerging research content using preprints. 目次

> 1はじめに 12データ‧手法 2

2.1 対象 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22.2 分散表現辞書の作成 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

> 3結果‧考察 4

3.1 PPS 記事の分析結果 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 53.2 既存の分析との比較 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8

> 4まとめ 9

i1 はじめに

EBPM (Evidence based Policy Making) を推進するためには，データの蓄積・把握が重要である．科学技術 に関わる政策立案やファンディングの検討のためには研究動向の把握が必要である． しかし，研究分野を複数またがるような，学際的なエマージング研究を定量的に把握することは容易では ない．現状では例えば，ある研究分野に投稿された論文が，どのような分野の論文から引用されているか に基づいて，エマージングな研究領域を定義したり [Small85, 伊神 09, 治部 12] ，その融合度を定義したり

[Okamura19] ，といった手法が提案されており，これらはある程度有効に機能している． ただし，これらは引用関係を用いるという特性上，論文の公開から分析までに一定以上の期間を要する．仮 に引用情報を用いないとしても，査読という性質上，投稿してから出版までには通常数ヶ月，長ければ 1 年を超える期間を要する．さらに，解析に手間がかかることから多くの場合引用数ベースでトップ 10% や 1%

など，上位の論文に絞らなければ解析が難しいという面もある．したがって，例えば 2019 年末から始まった

COVID-19 の流行のような緊急性の高い案件について，比較的短期に分野間の融合の状況を見る，といったこ とには使いづらい側面もある． ここで，近年プレプリントサーバ (Preprint Server, PPS) の活用が進みつつあることに着目する． “プレプリ ントとは，主に査読付きジャーナルに投稿する前の草稿原稿のこと ” であり “このプレプリントを掲載して 誰でも読めるようにする ” サービスが PPS である [林 20] ．投稿前の草稿という特性上，査読論文に比べてそ の信頼性は必ずしも担保されないが，代わりに最新の情報を得られる可能性がある． PPS は有名なものでは

1990 年代初めから運用されている arXiv などが存在し，近年では，医学や化学などの分野でも PPS が開設さ れ始めている．こうした情勢によりプレプリントだけでもある程度の情報量を確保することが可能となりつつ あり，有識者の間でもプレプリントの動向把握をしておくことの重要性を指摘する声がある [文科 19] ．特に

COVID-19 を機に関連するプレプリントの登録数は飛躍的に増大しており，動向把握のための情報源として重 要な位置を占めつつある． このようにプレプリントを用いることで，査読付き論文と比較するとより最新の情報が得られるものの，動 向把握についても別手法が必要となる．すなわち，引用・被引用関係からの動向把握を行う限り，分析に資す るだけの引用がなされるまで数年の期間が必要であり，プレプリントの先行性は誤差の範囲にとどまる可能性 が高くなるためである．そこで，引用情報を用いない研究動向自体の把握については，自然言語処理を用いて 実現する．具体的にはプレプリントの各記事に付与されたタイトルや概要を手がかりとして，ここからトピッ クを抽出し，それらをベースとして分析する．具体的な手法は文献 [小柴 20a] を踏襲する． この手法は前述した先行研究 [Small85, 伊神 09, 治部 12, Okamura19] と異なり，数値的な判断が困難である ほか，トピックの意味解釈を要する点に難点があるが，その一方で，最低限一定量のタイトル・概要のみがあ れば分析ができるため，引用関係の分析に比べて短期で，かつ様々なデータソースを横断的に分析できる点に 利点がある．したがって，先行研究と並列する別種の評価情報として機能することが考えられる．分析可能な データ数の面においても，例えば文献 [小柴 19] では同様の手法で約 5.6 千万件の文献を分析しており，十分 に機能することが期待される． 以上より本稿では， COVID-19 に関するプレプリントの各記事を用いて内容の近さで論文をマッピング・分 類することにより，エマージング研究のメタ把握を試みた．

COVID19 は， 2019 年 12 月に中国武漢で大流行した重症急性呼吸器症状を特徴とする新型コロナウイルス （SARS-CoV ）による感染症であり，その後世界中に感染拡大しパンデミックとなった． 2020 年 6 月 2 日現在

1で， 216 の国や地域で約 620 万人が感染し， 37 万人以上が亡くなっている． 結果，医療のみならず経済の面においても大きな影響を与えており，同一の現象に対して様々な分野から取 り組みが行われている様子や，融合している様子が観察できることが期待できる．

## 2 データ‧手法

データおよびその詳細は文献 [小柴 20b] の通りであるが，以下でも改めて解説する．

2.1 対象

arXiv, medRxiv, bioRxiv, chemRxiv, SSRN (Social Science Research Network) という 5 つの PPS を対象に した． これらについては文献 [林 20] でまとめられているとおり，それぞれ図 1 の分野に強みを有する． 名称 創設年 2020年1月現在の 運営母体 分野 システム DOI

arXiv 1991 コーネル大学 物理学に始まり，情報学，経済学等 多分野に広がる オリジナル ☓

SSRN 1994 Elsevier 社会科学に始まり多分野に広がる オリジナル （ColdFusion） ○

BioRxiv 2013 コールド・スプリング・ハーバー研究所 生命科学を 中心とした分野 HighWirePress ○

ChemRxiv 2017 米国化学会，英国化学会，ドイツ化学 会，日本化学会，中国化学会 化学を 中心とした分野 figshare ○

MedRxiv 2019 米イエール大学， コールド・スプリングハーバー研究所， BMJ(British Medical Journal) 医学を 中心とした分野 HighWirePress ○

> （ 文献[林20] 図表3をもとに作成 ）

図 1 PPS と主要分野

さらに，これらの PPS の多くは今回の COVID-19 / SARS-CoV-2 に関連する記事について，独自にとりま とめたリンク集を生成している（図 2 参照） ．

chemRxiv については，データ収集を行った 2020 年 5 月 25 日時点で， chemRxiv 独自のリストは見当たら なかったが，論文等文献検索サービスである Dimensions 1) がとりまとめて公開している COVID-19 関連の データセット 2) に chemRxiv 上の記事が出てくるため，これを利用した 3) ．その上で各リストに掲載された各記事の投稿日，タイトル，概要などの書誌情報を収集し，分析することに した． ここで， SSRN については図 3 に示すとおり， “Preprints with THE LANCET” との表示がついた記事も散見 される．

Lancet は医学系の著名雑誌の一つであり，相対的に人文社会系のプレプリントが多いと考えられる SSRN

> 1)

https://app.dimensions.ai/

> 2)

https://dimensions.figshare.com/articles/Dimensions_COVID-19_publications_datasets_and_clinical_ trials/11961063

> 3)

chemRxiv は figshare というシステムを採用しているが， Dimensions ，figshare の運用母体は両方とも “Digital Science” 社である．

2図 2 収集対象

の中では異質と言える．そこで本報告においては， “Preprints with THE LANCET” との表示がついた記事につ いて，これを “SSRN Lancet” と切り分けて扱うことにした．

> 図

3 SSRN における Lancet のプレプリント

収集した記事の中には 2018 年など古い情報も見られたため，記事を 2020 年 1 月以降のものに限定し，結 果として，それぞれ表 1 に示した記事数を得た． これら記事に関する 2020 年 第 4 週以降の週次投稿数推移を図 4 に示した．

3PPS Num arXiv 936 bioRxiv 716 chemRxiv 175 PPS Num medRxiv 2837 SSRN 612 SSRN Lancet 496

表 1 PSS ごとの記事数 (2020 年 5 月 25 日時点 )                         BS9JW 443/ 443/-BODFU NFE3YJW CJP3YJW DIFN3YJW

BS9JW 443/ 443/-BODFU NFE3YJW CJP3YJW DIFN3YJW

                                                                                                                               

8FFL

図 4 PPS ごとの週次投稿数推移

2.2 分散表現辞書の作成

収集した記事のタイトル，概要をベースとして単語ベースの分散表現辞書を構築し，記事単位での分散表現 を構築した． 参考にした文献 [小柴 20a] では， pubMed のデータに基づいて単語ベースの分散表現辞書を構築していたが， 今回は arXiv や SSRN などの記事も対象としているため，医療系に閉じない多様な話題が含まれることが想 定され， pubMed のデータでは十分な表現獲得が行われない可能性がある．そこで今回は収集した記事のタイ トル，概要をベースとして単語ベースの分散表現辞書を構築した．手法には FastText[Bojanowski17, Joulin16]

を用い，記事数が 6 千件程度であることから，次元数を 100 として構築した． また，文献 [小柴 20a] では各記事の概要の記述量に差があることから TF-IDF を用いて特徴語の上位 20 件までをもちい，記事ごとの分散表現を構築していたが，今回はストップワードを除外した上で，全単語を用い て記事ごとの分散表現を構築している． これらから，単純に文献 [小柴 20a] の結果と比較ができない点には注意が必要である．

## 3 結果‧考察

分析の結果について以下に述べる．

43.1 PPS 記事の分析結果

構築した記事ごとの分散表現について， UMAP[McInnes18] で 2 次元に圧縮し， PPS ごとに可視化したもの を図 5 に示す． arXiv bioRxiv chemRxiv medRxiv SSRN SSRN Lancet

> 図

5 論文の分布（ PPS 単位）

図 5 を見ると， medRxiv 以外は PPS の種類ごとに近くに固まっている様子が見て取れる． SSRN,SSRN Lancet, chemRxiv, bioRxiv それぞれにおいて，塊が読み取りやすく，それぞれの PPS の持つ分野のプレプリ ントが集まっていることが示唆される．一方， medRxiv は他の 5 種類の PPS を繋ぐように広がっている様子 が示された．このことは， medRxiv は対象としている分野が幅広いことを示し，また， COVID-19 関連につい ては分野横断的で学際的な研究が含まれることを示唆している可能性がある． 仮に PPS と分野，若しくはトピックが対応しているとすると，そうした分野・トピックの違いが用語の違い に表れて，このような偏在を示した可能性がある．そこで，文献 [小柴 20a] と同様に， k-means++[Arthur07]

を用いて記事を 16 分類し，それらの分類ごとに頻出語のワードクラウドを作成することでトピックの抽出を 試みた． 結果を図 6 から 8 に示した． また，図 7,8 には頻出語に加え，著者のうち，医学・薬学に知見を持つものがワードクラウドから推測でき るトピックのラベル（解釈）を付与した． これら，トピックの解釈を含めた結果について，図 9 に示した． 図 9 を見ると，左端に治療薬やワクチンの島が隣接しており，さらに，治療薬やワクチンの開発に必要な ゲノム解析や，感染機構に関連すると思われるトピックが並んでいる．右に目を向けると，社会・経済・政策 や肺画像診断のトピックがあり，両者に関連しそうな情報・データ分析がそれらの中間に位置している．こ れらの結果を鑑みると，トピックの分類はある程度は納得がゆくものである．なお， WHO 論文分析の文献

[小柴 20a] と比較すると，そこは示されなかったトピックや，内容がさらに明確になったトピック等，全体の

1/3 程度は異なっている．

512 345 678910 11 12 13 14 15 16 図 6 論文の分布（トピック単位） sars cov protein bind spike ace2 virus cell coronavirus human receptor covid antibody vaccine viral host rbd use target infection epitope domain study sequence interaction identify ncov structure rna novel peptide show base high may result potential mutation model analysis cause site genome provide pandemic also structural development design disease entry predict h3 response coronaviruses glycoprotein molecular neutralize drug respiratory specific region suggest affinity two reveal present new severe acid report immune surface s1 could syndrome acute hla highly complex global different develop include gene data population enzyme residue amino antiviral conserve found therapeutic fusion outbreak approach infect effective understand inhibitor patient candidate health spread well convert replication angiotensin variant bat one find across method animal like mediate level test emerge demonstrate first relate mechanism computational state antigen cross simulation mers treatment prediction compare induce tool strain dynamics analyse non lead however membrane unique s2 species indicate insight energy inhibit important among available similar abstract activity change assay mhc molecule several increase evolution need strong know humans motif world higher thus role protease rapid tmprss2 evolutionary block might function nucleocapsid currently strategy cleavage process isolate range potent possible interact form contain subunit screen effect perform pathogen genomic china silico associate selection dock clinical key recently wuhan detect multiple observe interface three functional determine feature allele enhance propose immunity identification critical transmission cov2 type positive cellular single neutralization conformation sup within expression class public encode analyze research therefore hcov common generate prevent facilitate glycosylation therapeutics death serum order express recent mrna diagnostic hace2 furin recognition major individual characterize rate low addition impact derive make support heparin likely via rapidly confirm system construct position significant mouse network zoonotic difference open broad help nucleotide investigate number database intermediate represent ability current covs ii large monoclonal dependent agent ligand emergence worldwide promise vitro potentially patient covid severe study disease clinical risk case group hospital outcome sars ci cov mortality result age use level include associate coronavirus treatment analysis higher data infection increase death method factor admission compare high pneumonia lymphocyte severity laboratory test characteristic conclusion non background china find cell symptom critical significantly count rate respiratory wuhan cohort il days confirm show lt vamong report retrospective years hospitalize acute injury blood control icu median time care model male early positive common identify ratio hypertension significant therapy may regression lower comorbidities meta mild two illness effect elevate review total medical die admit follow difference ventilation crp diabetes serum respectively score association discharge aim ill predict index interest value march analyze cause decrease health day found novel critically collect feature hospitalization statement develop ct cytokine also without first kidney infect dimer center relate however syndrome ethics need base older present one could receive protein pandemic observe moderate viral potential require february aki inflammatory failure objective onset suggest iqr evaluate perform neutrophil record demographic liver fund fever intensive interpretation reduce heart negative treat lung hcq type progression reactive evidence low pcr ldh system mean logistic three female likely population cardiac support indicate mechanical assess invasive january single university prognosis adjust analyse hr duration well function arb cancer primary normal parameter immune adult rr trial number measure drug diagnosis unit survival odds different independent change improve gt ards cd8 marker sex april cd4 survivor cough course enrol antiviral baseline within chronic remain status science condition pre observational poor predictor stage participant virus conduct renal hydroxychloroquine main range ml angiotensin sup outbreak epidemiological diagnose auc prognostic occur systematic approval specific chest prevalence pulmonary response provide declare plasma subset set lactate adverse nlr province author corticosteroid declaration individual predictive rna approve exist inhibitor indicator multivariate fatality organ proportion research covid pandemic health social crisis policy state economic public response coronavirus government impact global measure effect use country paper market risk distance also economy find people time provide home work spread data financial outbreak world result case business may lockdown first disease level shock need many increase model make study us individual sector law worker firm support one international new affect relate order take act system right virus large challenge evidence school healthcare change reduce suggest include base likely across unite emergency show closure care well however information current would rate face national activity period future research income high march stock focus develop could long political cost human stay control issue concern help two term less due supply present analysis article survey household three number local fund live discuss different china legal federal trade rule interest identify american benefit role epidemic address even test european price action consider potential examine part argue lead citizen critical low within service medium trust infection industry report require month cause implement job understand negative eu behavior estimate community early spend return demand decision population value give become intervention create respond society decline mobility among factor medical labor county experience company second gdp question significant short propose regulation analyze associate around occupation contact fiscal mitigate limit framework non consequence novel approach effort news group lower plan restriction situation investor place follow prevent force allow child account april compliance might small effective development program relief whether recent exist reform set threat strategy area save especially key come continue policymakers product perspective manufacture resource monetary private unemployment good uncertainty power important production mortality unprecedented credit since practice bank debt family expectation million review growth document greater capacity transmission context general patient implication years process governor online investment reaction strong higher security aim design adopt post event recovery sars test covcovid patient sample use pcr rt detection assay positive method result rna swab infection antibody viral virus igg clinical negative detect sensitivity case time diagnostic study coronavirus base igm diagnosis disease respiratory pool pandemic high specimen collect rapid symptom laboratory qpcr days develop one rate individual show acid nucleic specificity false kit extraction need two nasopharyngeal health confirm lamp control performance serological novel infect provide group perform identify specific population background serum also low onset data number limit compare approach report screen cause value available protein respectively reverse sequence acute increase evaluate current severe conclusion however protocol saliva include could amplification ct present early different require standard elisa ncov spread hospital molecular may level reagent analysis blood real first sensitive reaction response well care suspect gene demonstrate day find outbreak transcription asymptomatic large reduce diagnose target set higher load syndrome ci step three design quantitative nasal system determine accuracy measure public total rapidly tool strategy primer throat wastewater potential many sputum prevalence concentration single spike scale evaluation found treatment risk china diagnostics chain collection cost copy accurate country anti improve significantly range genome among worker antigen non alternative transmission symptomatic estimate suggest point global assess human lower polymerase currently combine follow commercial fast worldwide simple isothermal week monitor since information np stage without process cdc pathogen direct subject comparison validation effective world shortage aim efficiency within plasma four reliable highly new take validate pharyngeal become resource probe describe observe analyze rbd epidemic development critical throughput capacity community support interpretation nucleocapsid important infectious allow mediate stool help platform significant self several due shed overall titer propose emergency cohort per agreement median healthcare research minutes influenza optimize loop pneumonia cross people heat less participant supply remain region home indicate recommend long initial gold challenge establish enable would work obtain covid model social measure case epidemic distance spread number use pandemic country intervention infection control population disease strategy transmission health rate time contact outbreak test lockdown data reduce policy result impact estimate state individual public death study scenario effect level different effective quarantine infect isolation base show may capacity risk increase system peak sars cov virus care find coronavirus early also high implement need trace would non reduction economic mitigation new mobility patient one china could people method region days containment government two current dynamics provide develop analysis icu hospital critical report sub first community simulation city order include however require large parameter effectiveness work predict week healthcare period lead growth consider mortality bed world home travel daily limit march suggest approach immunity restriction take many across prevent novel long delay cost due infectious resource age well global us group present total mask april change curve response italy confirm epidemiological available contain potential unite evaluate allow reproduction even within compare pharmaceutical decision network make mitigate vaccine follow local demand term scale place identify mathematical low day decrease slow second simulate affect background understand value significant prediction give strict likely among month three end paper possible million help school factor implementation optimal national county wuhan human range propose strong outcome severe phase cause assess without stay important various physical npis apply average india less duration activity forecast vary specific found fatality expect asymptomatic around impose flatten wide project lower seir plan intensive account per aim pattern short effort person become interaction relax herd burden key south close rapid area susceptible hospitalization analyze symptom general conclusion exit economy higher achieve face action future assume since benefit suppression lift maintain medical determine currently evidence lock target efficacy remain uk avoid closure essential indicate tool wave structure situation inform focus investigate active support adopt sars cov virus sequence coronavirus genome covid viral human analysis infection use outbreak data study disease pandemic transmission mutation host spread protein novel respiratory case identify ncov genomic china result strain h3 population model coronaviruses sample severe base cause phylogenetic different time show variant may also genetic first isolate country syndrome available patient wuhan method health gene global bat report found cluster new suggest acute vaccine provide early infect two rna high relate world reveal test present find evidence emerge change public number observe pangolin understand evolution research region variation include cell origin group nucleotide within analyse epidemic among worldwide important pattern one epidemiological multiple rapid clinical associate approach potential december current type rate three well control whole molecular detect since evolutionary indicate response across march clade need information tree like gt compare mers state positive tool death sup development predict rapidly emergence abstract specific effective analyze know site humans target recent dynamics could occur measure diversity level single confirm large individual network increase spike effort event community introduction however distribution ace2 difference lineage possible structure people animal major surveillance around pathogen europe non share scale hcov become determine likely impact trace selection affect several acid frequency develop complete identification design usa similarity investigate database collect influenza local immune recombination factor highlight low describe estimate link significant late make source due synonymous structural might demonstrate infectious characterization lead amino circulate generate province similar four effect january currently follow us risk perform mutational city derive role highly insight detection set evolve full mechanism ongoing limit receptor many real still propose work code pneumonia implication date contact cov2 via knowledge conclusion system learn background take substitution strategy deep antiviral review involve support drug geographic contain distinct week interaction recently common february challenge apply platform future help track examine order appear importance key covid case ratecountry death infection number age population estimate test data mortality use study disease result sars pandemic model increase health report state cov risk time fatality factor high level temperature spread transmission analysis confirm higher method effect may china coronavirus county epidemic across show find patient bcg base cfr outbreak among region difference april associate per new also significant daily ci incidence suggest individual infect group compare policy impact different correlation lower average years march italy air measure us days relate include conclusion city vaccination prevalence total first background positive social specific association period virus control affect public due condition observe ratio identify people care adjust found humidity severe cause however provide reduce hospital outcome one variable relative non global early two community variation evidence available area regression unite influenza ifr low demographic healthcare million world large could growth range lt trend median current excess decrease system pollution value sup significantly potential well explain severity economic likely cumulative national density correlate province proportion day novel predict contact understand person develop change consider analyze negative weather relationship assess distance calculate mean overall respiratory would exposure household role sample local epidemiological respectively term three distribution need burden account investigate follow less parameter aim expect week analyse within limit indicate socioeconomic index vary symptom count strategy climate remain long york environmental human february morbidity linear clinical worldwide live examine capacity percentage approach worker influence sex set reduction sub similar lockdown estimation rr present income statistical dynamics european hubei quality recent intervention spatial objective uk bias month europe possible strong england interval lead vulnerability older date information give characteristic paper asymptomatic pattern future determine bed perform regional previous seasonal make obtain response wuhan life year icu travel conduct international publicly viral january detect might cluster many disparity apply vstructure ecological take drug sars cov covid protease use inhibitor bind potential study dock target protein compound virus coronavirus antiviral molecular viral base identify approve main treatment screen molecule novel result disease infection structure clinical mpro repurposing candidate pandemic model active effective site show anti activity rna may approach report high ncov design ligand cell interaction trial energy human fda replication inhibit also effect cause therapeutic silico two include vaccine like could present data test agent predict available simulation new provide hydroxychloroquine respiratory computational need suggest treat chloroquine analysis world development virtual enzyme know find three develop mechanism polymerase currently promise select combination discovery affinity health vitro ace2 infect host one natural possible lead patient found mol complex 3clpro efficacy spread severe method kcal structural global specific therapy receptor among ritonavir small remdesivir dose perform research hiv strategy syndrome exist spike acute outbreak inhibition acid form well database potent worldwide due top medicine free rdrp make indicate several time search china however identification h3 dynamics hit property lopinavir concentration lung propose prediction inhibitory sup work score library emerge rapidly chemical repurposed group rapid different nelfinavir process value experimental dependent key urgent demonstrate residue nucleotide role first crystal recently reveal pocket therapeutics act cov2 action evaluate essential exhibit hcq learn best control since generate current wuhan analogue recent therefore death many compare case conduct coronaviruses prevent follow reposition combat mode consider investigate strong investigation deep network people substrate broad ability bond across domain 3c potentially low evaluation apply plasma md calculation require evidence assay effort discover profile bound explore validate thus higher important similar highly clinically similarity toxicity public various already rank take number addition 3cl platform spectrum covid19 responsible block relate order significant interact option life drugbank become azithromycin risk cysteine reduce six level support plant represent triphosphate ec50 non give range combine 1 2 3 45 6 7 8

検出・検査 ゲノム解析 治療薬探索 国別比較 社会・経済・政策 患者治療効果 ワクチン開発 感染拡大

図 7 トピックとワードクラウド (1/2)

そこで，当初の疑問に立ち返り，トピックと PPS の対応について，図 10 にまとめた． 図 10 を見ると，たとえば chemRxiv は治療薬探索のトピックに強く結びついていることが分かる．また，

SSRN は社会・経済・政策と， SSRN Lancet は患者病状と， bioRxiv はワクチン開発と強く結びついている 事が分かる．逆に medRxiv はもともとの記事数の多さとも相まって，多少の濃淡があるものの広く様々なト ピックをカバーしていることが分かる． arXiv もやや幅広ではあるが，こちらは中身を見ると感染モデルや情

6covid use data pandemic study health social disease information public coronavirus spread base outbreak research model analysis medium time contact result also review epidemic case relate report paper system provide article method include test user trace virus search twitter people identify response online trial risk global sars country topic privacy present world evidence available cov find approach measure impact community number may help dataset patient crisis tool source network government learn first work medical literature develop application policy propose design control need new process clinical well novel two state make individual treatment one open location infection distance early rapid many knowledge publish scientific understand scale however assess tweet technology resource share show news current analyze publication support platform important decision digital china aim level large mobile different potential challenge question systematic interest change population symptom effect high web author across language real march inform intervention future describe solution protocol around healthcare conclusion term increase due conduct collect concern human surveillance live infect perform monitor track content screen enable mine exist transmission focus researcher specific daily group become since non issue evaluate science give cause activity build found official database via app set access analyse hospital text event quality economic limit critical problem order outcome effective strategy low three require allow effort apply map personal development follow take january internet factor post could major attention care generate misinformation http society chinese emerge discussion objective role discuss pattern create currently sentiment general apps fight communication background address like regard several days respiratory contain rapidly period consider machine natural various relevant explore video collection update pubmed situation face international key implementation lockdown prevention recent index significant management google release suggest even us area detect service infectious towards framework implement day possible technique phone stage insight affect person reveal record indicator extract bias emergency cov sars cell covid ace2 infection expression patient viral lung human gene disease virus coronavirus respiratory response severe immune protein receptor may study host result clinical analysis use tissue cause potential also suggest associate type level identify entry data infect express acute show tmprss2 increase rna epithelial found treatment target syndrome single drug pandemic include specific pathway novel cytokine high observe model airway inflammatory reveal ncov angiotensin system replication signal induce cellular mechanism could report provide case factor symptom age control enzyme find understand profile antiviral significantly compare kidney blood risk convert interferon sequence higher however inflammation relate pathogenesis well role therapy ifn bind pneumonia therapeutic demonstrate highly anti effect severity population health mouse base injury seq healthy outcome evidence mediate analyze sample might liver tract different molecular two indicate spread interaction among epithelium spike mortality susceptibility reduce significant association lead method present need organs damage network death activity protease new macrophage mild china antibody non development develop correlate characterize decrease genetic perform activation involve investigate vitro global animal treat test several determine function outbreak conclusion early across male key critical time change storm ii immunity difference pulmonary strategy transmission agent affect individual follow detect positive co regulate alveolar analyse candidate activate likely thus public remain innate effective monocyte failure vaccine background process lower cancer smoke inhibitor low sup therefore one neutrophil lymphocyte multiple impact mers route insight rapidly nasal group derive predict rate due know available distress subset wuhan inhibit small heart datasets major support like peripheral functional worldwide world load h3 underlie furthermore within progression facilitate number primary important il especially distribution inhibition addition approach current acid interest confirm plasma work possible signature reactive whether people metabolism help first marker require emerge genome december complement alter regulation dependent upper intestinal evaluate furin susceptible mainly strong recently digestive play patient covid study clinical case hospital disease sars infection symptom china cov severe data wuhan coronavirus interest statement include method find ethics report result test characteristic pneumonia confirm days fund medical treatment ct age group outcome respiratory risk background time review use laboratory fever analysis author approval positive science declaration years child feature ci rate show infect novel retrospective interpretation outbreak declare epidemiological model compare health approve identify one non admission care research university follow first early pcr median among mild two higher mortality asymptomatic support number chest common collect analyze national death province trial diagnosis onset high committee increase woman virus conclusion associate discharge january ncov factor pregnant base transmission cohort control present contact acute cough february hospitalize diagnose period severity may consent history compete negative critical inform image center rt need count project aim vmarch level admit significantly develop stage technology viral respectively cause hubei systematic epidemic total conduct illness foundation found also emergency spread type suspect three sample grant lung range lower score significant male none difference day different lymphocyte pandemic without provide perform people search evidence syndrome mean city acid natural describe icu adult nucleic however blood therapy iqr infectious proportion course system work meta progression demographic screen relate record effect new die obtain observe conflict swab area population commission december long department information pregnancy evaluate staff objective cell incidence receive scan predict manifestation public radiological assess hospitalization change waive key management prevalence exposure detection protocol enrol series decrease regression intensive primary treat design since influenza rna low could well unit occur ground symptomatic write potential measure general diarrhea individual sign reduce glass opacity medicine pediatric chinese remain prevention single older rapid moderate board ratio response designate lesion stay initial observational duration cluster estimate within close tongji institutional feb due ventilation less suggest development female covid image ct use patient learn model chest deep ray pneumonia method base disease result diagnosis test propose feature case data network train lung dataset coronavirus accuracy infection detection performance classification study scan clinical neural screen ai show sensitivity approach segmentation develop machine available achieve system high detect medical novel early algorithm tool set time world non cxr pandemic compute convolutional also infect class paper specificity prediction diagnostic provide tomography work different analysis spread radiologist hospital include identify validation evaluate improve predict diagnose two cov technique sars score health confirm normal cause datasets however present extract transfer pcr automatic one new accurate research perform positive severity challenge virus help large make limit auc compare task severe respiratory collect conclusion process lesion area framework viral obtain classify treatment architecture ci fast assessment find validate rate multi net rt report region due development open global rapid first number artificial information could demonstrate curve label expert relate stage specific increase automate several pre intelligence sample around promise control assist effective best domain real pulmonary need abnormality support design state suspect pattern efficient may characteristic three experiment outbreak aim well follow background community identification negative respectively call analyze cnn type decision public rapidly aid opacity classifier outcome publicly contain strategy symptom experimental assess scale application important reduce evaluation many resource critical attention purpose risk covid19 group highly source mortality value term role build art since scheme representation objective similar level corona cost automatically ground volume annotate become precision radiological recent possible order quantification care low computer potential segment healthcare people 3d initial worldwide current random quantitative end short china vector lu standard consider triage therefore good apply distinguish essential emerge overall fine utilize solution employ country knowledge http cap predictive ggo small cross human common great address size abnormal useful give second recently multiple covid health study risk anxiety pandemic use patient survey outbreak psychological disease mental result medical report participant among measure infection depression symptom coronavirus social ci factor level high public china impact method population care healthcare hospital worker work support stress data age associate include knowledge test questionnaire staff hcws find response background online epidemic cross conclusion respondent student increase quarantine people individual base interest sars general case higher sectional information years self relate score conduct distress fund statement prevalence perceive cov march analysis protective effect concern practice group assess also status need country rate ethics university research aim outcome national intervention provide severe community number positive nurse well lt total approval disorder compare contact state distance significantly wuhan transmission experience control identify adult one scale emergency april spread time may ppe show declaration first sample non likely gender evidence design exposure female week model perception respiratory family education medium clinical affect significant home regression review current infect personal respectively behavior early physician attitude child reduce live change collect interpretation lower face lockdown demographic physical worry strategy member service novel less difference author isolation government objective sleep declare follow virus woman estimate negative period however condition treatment resident province male different confirm complete prevent receive source system influence cause understand characteristic aor examine us two investigate range month cope life develop perform chinese could three cancer evaluate activity found cohort problem behaviour due mean february help acute professional area towards uk set suggest per take phase association global inform main days wear preventive program quality moderate logistic overall preparedness household post mask low rapid prevention crisis daily important infectious committee across would specific center management poor psychiatric department regard item screen access present city illness common since hubei school emotional approve policy science question assessment fear new belief recommendation improve key mask use covid respirator patient n95 sars cov ventilator virus respiratory test pandemic droplet method study result face fit model healthcare ventilation aerosol hospital medical filter pressure two surface ppe particle decontamination infection system transmission may uv filtration equipment design one control shortage rate coronavirus effective include surgical material available air supply airborne efficiency treatment however show need worker provide flow lung reduce risk spread also high room heat protective data time volume wear support disease personal disinfection measure viral single infect many clinical different could exposure fabric sup base present require level well sterilization tidal protection report environmental case reuse increase care current environment sample health protect public contamination large potential cycle non solution demand number make process demonstrate human perform find breathe outbreak sub size conclusion cloth limit performance standard evidence individual light alternative evaluate three contact approach gas give suggest produce propose found compliance factor resource guideline exist without novel set range acute concentration min ventilate condition layer background due ability efficacy cause possible would severe simple reduction world distance protocol critical simulate function significant lead global setting country per mean effect review split peroxide hydrogen relative production obtain temperature community mechanical positive provider textile procedure hcws lack modify cough minutes multiple blood unit quality contain contaminate source ffrs assess prevention area strategy isolation scale membrane estimate humidity dose crisis water within person safety syndrome inside low important rapidly develop several connect oxygen safe essential prevent generate social objective ensure determine worldwide negative load machine airway chain delivery common short operate consider collect people uvgi inactivate response help type work even quantitative first simulation setup remain ultraviolet conduct mvm various emergency via four dry inactivation vary mode circuit identify explore close less achieve experimental experiment thus home gt detect validate across treat rapid cm aim meet vapor case covid number china model epidemic estimate outbreak data wuhan time country infection use spread coronavirus disease transmission days confirm province rate infect report control measure city hubei death march february study health result january new method predict period base novel daily trend reproduction sars early population first intervention ncov italy peak ci pandemic public analysis total growth increase virus world may show cov april region find people day lockdown patient different effect high interval state background forecast also would infectious r0 quarantine value prediction risk end interest two south travel national cumulative level provide korea current effective reduce since scenario impact basic around global parameter reach government one dynamics individual outside include epidemiological take fatality mainland respectively india fit suggest chinese december decrease conclusion prevention compare could local cause average estimation three week fund iran social however feb analyze symptom strategy test mean implement need identify incubation stage expect import affect area severe situation date serial asymptomatic change available onset across occur start indicate curve policy found sub exponential pneumonia point follow among present rapidly distribution interpretation well range potential icu human support science future declare contact incidence develop spain statement phase due observe hospital unite work distance declaration jan month mathematical likely decline calculate response consider susceptible large double higher research system worldwide seir author recover collect approach million evaluate series aim delay medical cure understand non japan important propose within maximum second information make usa prevent still obtain assess give capacity become vary initial size community continue possible mortality major short actual rt per person emergency international isolation real limit critical france remain containment key care us pattern less close germany characteristic apply scale symptomatic effort emerge restriction reproductive proportion many ongoing significant mar respiratory foundation paper begin lower help surveillance accord cfr appear analyse order source model covid epidemic data case use number time infection spread country disease estimate base parameter outbreak infect rate pandemic prediction population different test study result measure show growth propose method predict dynamics forecast coronavirus china death individual analysis sir control italy transmission provide also network new peak infectious present evolution approach virus fit quarantine report sub effect state apply mathematical seir may make social simulation paper curve region real first two well policy daily health estimation world available epidemiological trend period confirm strategy total take lockdown system susceptible distance simple future describe develop current value one reproduction novel observe give level impact people consider term size possible exponential equation early public scenario intervention find dynamic analyze basic sars order recover series distribution risk change india city include days stage compare effective function global statistical day cov non process increase containment long obtain asymptomatic understand march april due however fatality point follow law work phase end us uncertainty several allow scale learn account spain behavior determine information set differential framework power government large mean range bayesian affect three short error contact evaluate development group application suggest cumulative introduce important could expose perform second patient algorithm local high need tool probability stochastic decision like within simulate type accurate better recovery wuhan initial indicate logistic across problem start limit situation r0 various dependent would accuracy incubation vary assume official many assess numerical delay found aim specific characteristic since know discuss capture factor sample thus isolation identify even design optimal useful around reduce recent require reliable community spatial mortality structure lead date standard unite province extend focus response uk condition south contagion implement pattern modify week european expect average regression calculate projection demonstrate germany become positive derive reveal investigate korea depend incidence main usa generate call propagation potential similar france effectiveness worldwide reach generalize 9 10 11 12 13 14 15 16

マスク・人工呼吸器 感染機構 肺画像診断 不安・心理 情報・データ分析 アウトブレイク 患者病状 感染モデル 図 8 トピックとワードクラウド (2/2) 12 345 678910 11 12 13 14 15 16

感染拡大 患者病状 ゲノム 解析 社会・経済 ・政策 治療薬 探索 情報・ データ分析 検出・検査 感染モデル 肺画像 診断 患者 治療効果 国別比較 不安・ 心理 マスク・ 人工呼吸器 ワクチン 開発 感染機構 アウトブレイク

図 9 論文の分布（トピック（解釈）単位）

報・データ分析など，メインは数理系に偏っている． これらを鑑みるとやはり， PPS とトピックの間にはある程度強いつながりを見て取ることができ，それらは

PPS のもともとの分野と関係している事が分かる．

COVID-19 という同じ対象であっても，当然，研究分野ごとにそれぞれの専門性を活かして作業に当たるこ とになるため，このこと自体には何ら驚きはない．一方で，社会・経済・政策などの話題にまで広がりがある

7,JOE 5PUBM                 BS9JW                  CJP3YJW                  DIFN3YJW                  NFE3YJW                  443/                  443/-BODFU                 

感染拡大 情報・データ分析 肺画像診断 患者治療効果 マスク・人工呼吸器 感染モデル 患者病状 検出・検査 国別比較 ワクチン開発 ゲノム解析 社会・経済・政策 治療薬探索 アウトブレイク 不安・心理 感染機構 図 10 トピックと PPS

こと， arXiv が仮に「データサイエンス」を意味すると考えた際に，感染拡大や肺画像診断，社会・経済・政 策など，様々な分野に進出し， COVID-19 研究がメタサイエンスの地位をある程度確立している様子が観察で きたこと，などは今回の発見と言える．

3.2 既存の分析との比較

ここでは文献 [小柴 20a] との比較を通じて， PPS の特徴について見る． まず，文献 [小柴 20a] では WHO の文献リストと，一部の PPS を対象としている．結果，期間について多少 の差異があるものの， bioRxiv, medRxiv の記事については大部分が共通していると考えられる．ただし， 2.2

節で述べたとおり，分散表現辞書の作成方法等にも差があり，単純に比較できない点には留意を要する． まず本分析におけるトピックの時系列推移を図 11 に示した． 5PUBM                                                                                                                                                                                                                                                                                                                                                    8FFL

感染拡大 情報・データ分析 肺画像診断 患者治療効果 マスク・人工呼吸器 感染モデル 患者病状 検出・検査 国別比較 ワクチン開発 ゲノム解析 社会・経済・政策 治療薬探索 アウトブレイク 不安・心理 感染機構

図 11 トピックの推移（週次）

感染拡大やゲノム解析が早く， その後， 検出・検査方法や臨床などの話題が続く点では， 既存の分析 [小柴 20a]

でも示された疫学調査のステップ 4) ．とほぼ同じ傾向を示していると言える．今回は，迅速査読を経て公開さ

4) 疫学調査の基本ステップ，国立感染症研究所 https://www.niid.go.jp/niid/images/idsc/kikikanri/H28/13-7.pdf (ac-

8れた論文もあること，そもそも一部のデータが共通していることもあって，時系列的な推移に大きな差はな かったと考えられる． 一方で，トピック自体については差も認められる．例えば， 「社会・経済・政策」のトピックは，前回の研 究では検出できていなかった．また，治療薬やワクチン開発に関するトピックも明確には検出できていなかっ た．前者に関しては SSRN という人文社会系に強い PPS を含めた結果，後者も chemRxiv を含めた結果と解 釈できる． ただし，治療薬やワクチン開発に関するトピックについては医療系が中心と想定できる既存の分析で検出で きていても不思議はない．これについては， PPS は査読論文に比較して，現場で判明した治療結果や分析結果 が短時間で（正誤や質は度外視で）報告する事が可能，といった特徴が関連していることも想定できる．

## 4 まとめ

本報では COVID-19 関連のプレプリントを対象に，自然言語処理を用いたエマージング領域の把握を試行 した． その結果，既存の分析と同様に，疫学調査のステップに合致する動向を得ることができた．それに加えて， 通常の査読論文も含めて分析した先行研究では明確には検出ができていなかった，医薬・ワクチン開発に関す るトピックを抽出することができた． 今回の試行により，プレプリントを利用したエマージング研究内容のメタ把握が実現できる可能性が示唆さ れた． 今後，他のエマージング研究でも今回の方法が適応可能か，また，従来の引用数ベースの分析結果の先行指 標として機能するのか，それとも，研究者の興味関心などを表す既存手法とは別の指標として機能するのか， といった点について検証を行いたい．

> cessed: 2020-04-30) および 文献 [柳川 18]

9参考文献

[Arthur07] Arthur, David and Vassilvitskii, Sergei ：K-means++: The Advantages of Careful Seeding. Proceedings of the Eighteenth Annual ACM-SIAM Symposium on Discrete Algorithms , pp,1027–1035, 2007. http: //dl.acm.org/citation.cfm?id=1283383.1283494

[Bojanowski17] Bojanowski, P., Grave, E., Joulin, A., and Mikolov, T.: Enriching word vectors with subword information, Transactions of the Association for Computational Linguistics , Vol. 5, pp. 135–146, 2017.

arXiv:1607.04606

[Joulin16] Joulin, A., Grave, E., Bojanowski, P., Douze, M., Jégou, H., and Mikolov, T.: FastText.zip: Compressing text classification models, arXiv preprint , 2016. arXiv:1612.03651

[McInnes18] Leland McInnes, John Healy and James Melville ： UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction. arXiv preprint, 2018. arXiv:1802.03426

[Okamura19] Okamura, K. ：Interdisciplinarity revisited: evidence for research impact and dynamism. Palgrave Commun , vol.5, no.141. 2019 https://doi.org/10.1057/s41599-019-0352-4

[Small85] Small, H; Sweeney, E; Greenlee E. ：Clustering the science citation index using co-citations. II. Mapping science. Scientometrics , vol. 8, no. 5-6, p. 321-340. 1985 [伊神 09] 伊神正貫 , 阪彩香 ： サイエンスマップによる科学研究の動的変化の観測 手法と応用 . 情報管理 ,vol.52, no. 5, p. 255-266. 2009 https://doi.org/10.1241/johokanri.52.255

[小柴 19] 小柴 等，池内 健太 , 元橋 一之：日米の特許データと論文データを用いた Mapping Patents の試行 . 人工知能学会「社会における AI 研究会」 Vol.35, No.8, pp.1–8, Nov 2019. http://id.nii.ac.jp/1004/ 00010441/

[小柴 20a] 小柴 等，伊神 正貫，伊藤 裕子，林 和弘，重茂 浩美： COVID-19 / SARS-CoV-2 に関する研究の概 況. Discussion Paper, DP181, NISTEP, May 2020. http://doi.org/10.15108/dp181

[小柴 20b] 小柴 等，林 和弘： COVID-19/SARS-CoV-2 関連のプレプリントに関する分散表現データセット ―2020 年 05 月 17 日版― . データ‧資料 , NISTEP, June 2020. http://doi.org/10.15108/data_ covid19_2020_5

[治部 12] 治部眞里 , 松邑勝治 , 斉藤隆行 ： J-GLOBAL foresight の構築について . 情報管理 , vol. 54, no.10, p. 639-651. 2012 https://doi.org/10.1241/johokanri.54.639

[林 20] 林 和弘： MedRxiv, ChemRxiv にみるプレプリントファーストへの変化の兆しと オープンサイエンス時 代の研究論文 . STI Horizon 2020 春号 , Vol.6, No.1, Mar 2020. https://doi.org/10.15108/stih.00205

[文科 19] 文部科学省：「海外の最新科学技術動向に係る新興・融合領域に関する調査分析業務」業務成果報告 書. 平成 30 年度科学技術調査資料作成委託事業 , 2019. https://www.mext.go.jp/a_menu/kagaku/ kihon/1404334.htm

[柳川 18] 柳川 洋： 臨床研究と疫学 . 月刊地域医学 , Vol.32, No.9, pp.804(54) – 812(64), 2018. 10 DISCUSSION PAPER No.186

COVID-19 / SARS-CoV-2 関連のプレプリントを用いた研究動向の試行的分析

2020 年 06 月

文部科学省 科学技術・学術政策研究所

小柴 等，林 和弘，伊藤 裕子

〒100-0013 東京都千代田区霞が関 3-2-2 中央合同庁舎第 7 号館 東館 16 階 TEL: 03-3581-2391 FAX: 03-3503-3996

A Trial of early detection system for research trends through the preprints data

─ Research status around COVID-19 / SARS-CoV-2 June 2020 KOSHIBA Hitoshi, HAYASHI Kazuhiro, ITO Yuko National Institute of Science and Technology Policy (NISTEP) Ministry of Education, Culture, Sports, Science and Technology (MEXT), Japan

http://doi.org/10.15108/dp186 https://www.nistep.go.jp
