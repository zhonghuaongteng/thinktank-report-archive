# C-CRDS-FY2018-SP-09 原文切片

- 原文：`03_证据底稿\原文PDF\C-CRDS-FY2018-SP-09.pdf`
- PDF页数：38
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 5

STRATEGIC PROPOSAL
Live Cell Atlas Deciphering Dynamics of Biological Systems via Multi-Dimensional Analysis

CRDS-FY2018-SP-09 Center for Research and Development Strategy Japan Science and Technology Agency
iii
Executive Summary
What is Live Cell Atlas?
The Live Cell Atlas (LCA) will be made up of comprehensive four-dimensional reference map
of cells, with a focus on dynamics of interactive networks between biomolecules and cells,
including cell-cell communications. It will contribute as a basis for wide range of life science
research, from basics to applied, such as understanding the fundamentals of biological events
and acceleration of drug discovery. This proposal covers the strategies to build the scientific
and technological foundations that are required to establish the LCA. The LCA project
focuses on the dynamics of the interaction networks of wide range of biomolecules that can be
found in a cell, however, the dynamics shall be analysed not only in a single cell manner, but
also in multicellular systems. The dynamics will be captured in a spatial, temporal, and
quantitative manner, contemplating to build up mathematical models that simulate the
behaviour of each molecule in the biological system. Deciphering the regulatory system of life
and the effort to build up mathematical models that could simulate the biological event with
following the uncovered regulatory system would strongly contribute for applied biology area,
such as streamlining drug discovery process, as well as to deepen our understanding of rules
of life as basic research. For example, it is thought that in the recent drug discovery scene,
the major bottlenecks of the clinical test are the insufficient efficacy and safety issues (severe
side effects and toxicity). Quantitative visualisation of biological process from the aspect of
human science could provide better understanding of clinical condition, which enables to
simulate the effects of the candidate drug on the biological target. Such work flow in the drug
discovery process would facilitate more streamlined and effective prediction of efficacy and
the side effects of the candidate drugs.

Background and present state
Any biological events consist of the dynamic changes of intra-cellular interactome, where the
networks of the various types of biomolecules that interact each other within a minute space
of a cell, and cell -cell interaction networks. The biomolecules can be categorised into several
levels following the canonical central dogma in molecular biology: like nucleic acids (DNA &
RNA), proteins, and metabolites. The interaction between these biomolecules occur in both
intra- and inter -cellular manner. Qualitative and static information, such as the list of
biomolecules involved in ce rtain interaction networks and the nature of interactions, has
been relatively well collected; however, the dynamics of interactome and cell -cell interaction
have not been well described. This is partially because of that all the conventional analytical
methods have been invasive and brought critical damage to the living system; the molecular
consequences in living cells have been left almost untouched. In other words, knowledge
regarding truly “living” cell has been surprisingly limited, as majority of dat a have been
actually collected from dead cells.

### PDF页 9

戦略プロポーザル
ライブセルアトラス 多次元解析で紐解く生命システムのダイナミクス

CRDS-FY2018-SP-09 国立研究開発法人科学技術振興機構 研究開発戦略センター
i
目 次

エグゼクティブサマリー
Executive Summary
１．研究開発の内容 ··························································· 1
２．研究開発を実施する意義 ··················································· 4
２－１．現状認識および問題点 ·············································· 4
２－２．社会・経済的効果 ·················································· 7
２－３．科学技術上の効果 ·················································· 8
３．具体的な研究開発課題 ···················································· 10
３－１． 組織等細胞集団において１細胞単位で生体分子等を網羅・定量的
に解析する技術の開発 ··········································· 11
３－２．細胞および生体分子の時空間分布を高分解能で測定する技術の開発 ····· 11
３－３．生体分子・細胞の動的ネットワークの定量理解に向けた数理モデルの創出 12
４．研究開発の推進方法および時間軸 ·········································· 13
付録１．検討の経緯 ·························································· 17
付録２．国内外の状況 ························································ 22
付録３．専門用語 ···························································· 25

## T1_国家研发与方向设定

未自动命中；需人工按目录复核。

## T2_市场与产业政策边界

未自动命中；需人工按目录复核。

## T4_国际合作与开放

未自动命中；需人工按目录复核。

## T5_供应链与技术依赖

未自动命中；需人工按目录复核。

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

- PDF页4：メージングデータの統合解析技術 ・生体分子間・細胞間相互作用ネットワークを定量的に可視化する数理モデリング ライブセルアトラスに関連する動向として、米国では、ヒトの全身細胞の１細胞レベルでの遺 伝子発現マップを作成し、各臓器を構成する細胞の種類、状態、系統を分類し、カタログ化・マッ ピングする目的で “Human Cell Atlas（HCA） ” という壮大な国際プロジェクトを推進するなど、 近年のオミクス技術を背景に、網羅定量的に生体情報を取得しようとしている（日本からは理化 学研究所が本プロジェクトに参画） 。また欧州では次期Future and Emerging Technologies Flagship として“Life Time initiative”を2019 年3 月から開始している。このイニシアチブで は、 「ゲノムが細胞内でどのように機能しているかを理解することや、 細胞がどのようにして組織 を構成し、また病気の進行時にどのようにダイナミックに変化するのかを理解することが必要で ある」との考えに基づき、１細胞のゲノミクスとイメージングを統合した１細胞レベルの病理学 の実現や、電子健康記録（Electronic Health Record）と１細胞レベルのマルチオミクス等のビッ グデータを統合解析することによる病気の予測モデルの構築等に取り組むとしている。 このような各国動向に対して、本プロポーザルで提案する戦略は日本に強みのあるイメージン グ関連技術を中核とした我が国独自の研究開発戦略となっている。これを推進することで、ライ フサイエンス研究における世界的なプレゼンスを高めることが期待できる。また生命現象の制御 システムの解明及びモデル化は、生命を理解するという学術的側面のみならず、創薬の効率化等 への貢献も期待できる。例えば近年の創薬において、臨床研究で失敗する原因の大半は有効性不 足と

- PDF页33：デリングすることにより多次元マップ を構築し、グローバルな研究コミュニティに対して迅速に検索可能、アクセス可能、相互運 用可能、そして再利用可能にするオープンなデータプラットフォームの確立。 ・ 人体をマッピングするためのフレームワークおよびツールを構築するために、 他の資金提供 機関、プログラム、および生物医学研究コミュニティと調整と協力を行う。 ・ このプログラムにより開発されたリソースの価値を検証するためのパイロットプロジェク トをサポートする。 【欧州】 ・Life Time initiative 2019～ 次期FET (Future and Emerging Technologies) Flagship として、”Life Time”を採択し、2019 年3 月から開始している。 Life Time initiative の背景： ゲノム配列のみではヒトのフェノタイプや病気を予測するモデルを構築することはできない。 ゲノム配列の唯一の“通訳者”は細胞であり、ゲノムが細胞内でどのように機能しているかを理 解すること、 そして、 細胞がどのようにして組織を構成し、 病気の進行時にどのようにダイナミッ クに変化するのか、ということを理解することが必要である。これは、今世紀のサイエンスとテ クノロジーのグランドチャレンジであるが、近年の破壊的な技術革新がより発展することで、こ れらの障壁を乗り越え基礎生物学や医学にパラ ダイムシフトを引き起こすことが可能 である。 Life Time の長期ビジョンは、医師が患者の組織の分子状態をリアルタイムで評価し、早期診断 と効果的な介入を行うこととしている。 このビジョンを達成するためには、以下のような多数の融合的なチャレンジに取り組まなけれ ばならないとしている。 a） シングルセルゲノミクスをイメージングと統合して、臨床グレードのシングルセル病理学 を高い空間分

## T10_预见与优先领域

未自动命中；需人工按目录复核。
