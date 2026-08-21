# C-CRDS-FY2018-SP-04 原文切片

- 原文：`03_证据底稿\原文PDF\C-CRDS-FY2018-SP-04.pdf`
- PDF页数：67
- 页码口径：PDF物理页码；正式引用时仍需核对印刷页码。

## 执行摘要与开篇候选

### PDF页 5

STRATEGIC PROPOSAL
Quantum Computer Science for All -Towards novel quantum applications-
iii
CRDS-FY2018-SP-04 Center for Research and Development Strategy, Japan Science and Technology Agency
Executive Summary
The exp onential performance improvement of modern computers approaches
technological and economic limits of the semiconductor microfabrication. We are no
longer able to enjoy the “free lunch” of performance improvement by the increase
in the number of transistors. Meanwhile, computational demands, such as big data
analytics, media processing, deep learning, combinatorial optimization, secure cloud
computing, are expected to increase, thus great social expectation is given to the
improvement of the capability of modern computer systems. It is urgent to continually
improve the performance without increasing the number of transistors by using a new
computing paradigm, novel programming models, new algorithms and software, non-
conventional architectures, devices and materials, and so on.
　Reflecting such a research trend headed to the post-Moore’s-law era, “quantum
com-puter” is attracting academia and industry in recent years. If quantum
computer operates according to the theory, it is possible to perform essentially faster
computation than the modern computer (or so-called “classical” computer). However,
this quantum speedup has never been proven by experiment at the present time.
There is still a big gap between the situation of real machines and the number of
the qubit (quantum bit) and fidelity of the control gate required by typical quantum
algorithms, such as Shor’s factoring and Grover’s search algorithms.
　In order to fill this gap, it is necessary to enhance the research and development of
quantum software and architecture and strengthen the whole quantum computing re-
search from quantum information theory to quantum hardwares. The research targets
are (1) development, implementation, and demonstration of quantum-classical hybrid
algorithms, (2) preparation of quantum software development environment including
lan-guage, compiler, debugger, and simulator, and (3) quantum computer architecture
design based on quantum error correction code.
　In particular, for NISQ
2 computers, it is essential to explore and discover new algo-
rithms and killer applications as to what kind of problems can take benefit from
quantum computing. To that end, it is necessary to construct a software development
platform packaged with various tools and simulators that make the quantum
programs executable in a trial-and-error manner. It is also important to tackle
research topics that span hardware and software. More specifically, this includes the
quantum computer architec-tures that implement quantum error-correcting code, the
development of middleware and firmware to support the implementation of error
correction codes, electrical engineering on control electronics for precise control and
measurement of qubits.
　The field of quantum information processing has been growing as a part of physics,
but the trend of worldwide R&D on the quantum computing is gradually shifting to
2 Noisy Intermediate-Scale Quantum
戦略プロ_みんなの量子_本文.indd 3 2018/12/21 15:29

### PDF页 7

目　　次
エグゼクティブサマリー
Executive Summary
1. 研究開発の内容　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
 1
1.1 量子コンピューターとは
 ………………………………………………………… 1
1.2 提案する研究開発の概要
 ………………………………………………………… 2
1.3 推進方法
 …………………………………………………………………………… 4
2. 研究開発を実施する意義　　　　　　　　　
　　　　　　　　　　　　　　　　
 8
2.1 現状認識および問題点
 …………………………………………………………… 8
2.2 社会・経済的効果
 ………………………………………………………………… 22
2.3 科学技術上の効果
 ………………………………………………………………… 27
3. 具体的な研究開発課題　　　　　　　　　　　　　　　　　　　　　　　　　
 28
3.1 問題点と研究開発課題
 …………………………………………………………… 28
3.2 古典・量子ハイブリッドアルゴリズムの開発・実装・実証
 ………………… 28
3.3 量子ソフトウェア開発環境の整備
 ……………………………………………… 34
3.4 量子誤り訂正符号に基づく量子コンピューターアーキテクチャ設計
 ……… 36
4. 研究開発の推進方法および時間軸　　　　　　　　　　　　　　　　　　　　
 41
4.1 分野融合・企業参画・国際連携の促進
 ………………………………………… 41
4.2 量子コンピューター研究開発ネットワークとハブ拠点
 ……………………… 42
4.3 コミュニティ・エコシステムの醸成
 …………………………………………… 42
4.4 量子コンピューター教育・訓練
 ………………………………………………… 43
付録
A 検討の経緯　　　　　　　　　　　　　　　　　　　　　　　　　　　　
 45
A.1 インタビュー
 ……………………………………………………………………… 45
A.2 科学技術未来戦略ワークショップ
 ……………………………………………… 45
付録
B 論文で見た国内外の状況　　　　　　　　　　　　　　　　　　　　　　
 48
B.1 量子コンピューター関連論文マクロ動向
 ……………………………………… 48
B.2 Quantum Algorithm Zoo から引用された論文
 ………………………………… 49
付録Ｃ 専門用語説明　　　　　　　　　　　　　　　　　
　　　　　　　　　　
 52
付録Ｄ 参考文献　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
 54
v
CRDS-FY2018-SP-04 国立研究開発法人科学技術振興機構　研究開発戦略センター
戦略プロポーザル
みんなの量子コンピューター 〜情報・数理・電子工学と拓く新しい量子アプリ〜
戦略プロ_みんなの量子_本文.indd 5 2018/12/21 15:29

## T1_国家研发与方向设定

- PDF页6：ocial impact of realization of the quantum computer is expected, its R&D requires a long-term perspective and thus it is still too uncertainty and risky for many private companies. Therefore, the investment on the quantum com-puter from the market will be insufficient. Thus, the government should take action on the promotion of inevitable multidisciplinary research on quantum hardware and software, establish new R&D centers as a hub for the network, the provision of a quantum software development environment, and fostering quantum computing community and business ecosystem. In addition to the promotion of R&D by “quantum-native” researchers and engineers, it is necessary to provide education and training programs to people who are not so familiar with quantum mechanics. The quantum computing communi

## T2_市场与产业政策边界

未自动命中；需人工按目录复核。

## T4_国际合作与开放

- PDF页6：ow on, “quantum computer science” will play an important role as a guiding principle for building the quantum computer. The various players are needed in each aspect of interdisciplinary integration and collaboration, the participation from industry and developers community, and partnership with international collaborators. Because it is difficult for any player to prepare the necessary technology and personnel in full stack, it is key to exchanging everything necessary for the realization of the quantum computer such as knowledge, technology, human resources, over barriers of disciplines and affiliations. Although the great economic and social impact of realization of the quantum computer is expected, its R&D requires a long-term perspective and thus it is still too uncertainty and risky for many pr

## T5_供应链与技术依赖

未自动命中；需人工按目录复核。

## T7_管制与研究安全

未自动命中；需人工按目录复核。

## T8_新兴技术治理

未自动命中；需人工按目录复核。

## T10_预见与优先领域

未自动命中；需人工按目录复核。
