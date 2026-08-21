# C-CRDS-FY2019-SP-10 原文切片

- 原文：`03_证据底稿\原文PDF\C-CRDS-FY2019-SP-10.pdf`
- PDF页数：53
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 5

STRATEGIC PROPOSAL
Sensor Fusion Technologies in IoT era - Multimodal Sensing and Data Processing for Creating New Value -

CRDS- FY2019-SP-10 Center for Research and Development Strategy, Japan Science and Technology Agency
iii
Executive Summary

The IoT is required to acquire a wide range of data through sensors installed at a variety of
places to derive sophisticated, valued information from such data, i.e., it is required to add
high values to sensing information. To realize this, it is essential to ac quire a wide range of
sensing data and process it in an integrated manner, which requires the buildup of the base
technology that enables this. This proposal focuses particular attention on the sensing system
used on the data creation side (edge side). Based on this, we propose that in order to build the
base technology required for adding high values to sensing information, we should work on
the research and development challenges at three different levels (system, sensor terminal,
and sensor levels) collaboratively. It shou ld be noted that the term “sensor” used in this
document refers to a device that detects desired physical/chemical quantities by converting
them into electric signals, and the term “sensor terminal” means a device consisting of
components such as sensors, analog-digital converter circuits, battery units, and
communication circuits, installed near the object to be measured. As such, this proposal
differentiates between the sensor and sensor terminals in terms of strategy structure.

The bu ildup of a sophisticated IoT system capable of adding high values to sensing
information requires a high -performance cloud server and network along with an edge -side
sensing system that acquires a variety of useful data, and processes such data in order to
send it to the cloud. Traditional sensing systems are used in limited places, such as factories,
for a specific application and only acquire and process limited types and amounts of data. On
the other hand, the IoT must collect a much wider range of data–—information such as on the
environment, device operation, and human health –—without human intervention. To this
end, it is important to use the sensing system at the edge side to automatically collect a
variety of information in order to make a determination on the spot and take necessary action,
or, in order to process information, send it to the cloud for determination at the cloud side.

For big data and AI-related technologies and services in the upper layers of the IoT system
such as the cloud, GAFA i n the U.S.A. and other platformers have already dominated the
market, and thus many players around the world start to take interest in the lower layers,
i.e., the edge side. With strength in sensing technology, which is positioned in the lowest layer
of the IoT system, Japan is expected to lead the IoT industry from the lower layer by
delivering an excellent edge-side sensing system.

This edge-side sensing system (hereafter simply referred to as the sensing system) consists
of a sensor terminal installed near the object to be measured for the purpose of acquiring data,
and a device (for processing edge-side information) that processes data acquired by the sensor
terminal to send it to the cloud. Although the capabilities required for the sensing system
depend on the application , it is recognized as a common direction of the sensing system to

### PDF页 9

戦略プロポーザル
IoT 時代のセンサ融合基盤技術の構築～センシング情報の高付加価値化に向けた多様なデータの取得と統合的処理～

CRDS- FY2019-SP-10 国立研究開発法人科学技術振興機構 研究開発戦略センター

目 次

エグゼクティブサマリー
Executive Summary
１．研究開発の内容 ·································································· 1
２．研究開発を実施する意義 ·························································· 5
２－１．現状認識および問題点 ····················································· 5
２－２．社会・経済的効果 ························································ 13
２－３．科学技術上の効果 ························································ 17
３．具体的な研究開発課題 ··························································· 21
３－１ センシング情報の統合的処理（システムレベル） ···························· 21
３－２ センサ端末の最適化・高機能化（端末レベル） ······························ 22
３－３ センサ性能の向上（センサレベル） ········································ 25
４．研究開発の推進方法および時間軸 ················································· 27
付録１．検討の経緯 ································································· 32
付録２．国内外の状況 ······························································· 36
付録３．専門用語の説明 ····························································· 40

## T1_国家研发与方向设定

- PDF页7：ed to realize these functions. Under this situation, where time is required for the research and development of the sensing system, in particular, the devel opment of hardware such as new sensors and sensor terminals, efforts are required from a long -term perspective based on a government policy and with cooperation between academia and industry. It is important to build the research and development platform mentioned above at an early stage, as well a s to work steadily on the research and development challenges. In working on the challenges, it is assumed that research activities will be conducted by academia with focus placed on seeds research, and that research and development activities will be carried out based on needs from industry. In both cases, the key is cooperation between academia and

## T2_市场与产业政策边界

未自动命中；需人工按目录复核。

## T4_国际合作与开放

未自动命中；需人工按目录复核。

## T5_供应链与技术依赖

未自动命中；需人工按目录复核。

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

- PDF页15：点検することなく、必要なときに必要な保守をおこ なえば良いことになる。同様に、畑や家畜にセンサを取り付けることで、これまで IT の恩恵が あまり受けられなかった農業分野でも効率化や省力化が期待できる。 モノから得られる情報には、そのモノの状態を表す情報（車のエンジンの回転数や燃料消費量 など） と、 そのモノが置かれた環境に関する情報 （畑の温度や湿度、 橋や道路の振動の情報など） がある。IoT ではこれらの多様な情報がネットワークを介してクラウドに伝わり、集まった情報 が可視化され、人間による分析や判断に用いられる。あるいはビッグデータ解析やAI（Artificial Intelligence:人工知能）によって自動的に判断がおこなわれる。判断結果はネットワークを通じ て現実社会に伝えられ、自動車の制御や、畑の水遣り、橋の補修などの動作（アクチュエーショ ン）を実行する。ここで重要なのは、取得すべきデータは多種・多様であり、それらの様々なデー タを統合的に処理・分析することで高次で重要な情報を抽出すること、すなわちセンシング情報 の高付加価値化が必要なことである。それによって、IoT による効率的な社会インフラの維持・ 管理や安全な交通システムの実現、医療・介護の最適化、二酸化炭素排出量の削減など、安全・ 安心でサステナブルな社会の実現に向けた課題への対処が可能になると期待される。 センシング情報の高付加価値化を実現する高度な IoT システムの構築には、ビッグデータ解析 や AI・機械学習による高度な分析･判断をおこなう高性能のクラウド・サーバ、ネットワークと ともに、様々なデータを正確に取得してクラウドに送るエッジ側のセンシングシステムが重要で ある。現状、クラウドなど IoT システムの上層側におけるビッグデータや AI 関連の技術・サー ビスについては、既に米国のGAFA を中心としたプラットフォーマー企

## T10_预见与优先领域

未自动命中；需人工按目录复核。
